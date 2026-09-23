import 'dart:async';

import 'package:argus_mobile/controllers/voice_input_controller.dart';
import 'package:argus_mobile/models/voice_command.dart';
import 'package:argus_mobile/models/voice_state.dart';
import 'package:argus_mobile/services/feedback_service.dart';
import 'package:argus_mobile/services/speech_recognition_service.dart';
import 'package:argus_mobile/services/tts_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('push-to-talk executes direct recognized command on release', () async {
    final speech = _FakeSpeechRecognitionService(stopText: 'ajuda');
    final actions = <VoiceAction>[];
    final controller = VoiceInputController(
      speech: speech,
      feedback: _FakeFeedbackService(),
      onCommand: (action) async => actions.add(action),
    );

    await controller.beginPushToTalk();
    await controller.finishPushToTalk();

    expect(actions, [VoiceAction.help]);
    expect(controller.state.mode, VoiceInputMode.passive);
    controller.dispose();
  });

  test('push-to-talk quick release does not leave native listening active',
      () async {
    final speech = _FakeSpeechRecognitionService(
      stopText: 'ajuda',
      cancelDelay: const Duration(milliseconds: 20),
    );
    final actions = <VoiceAction>[];
    final controller = VoiceInputController(
      speech: speech,
      feedback: _FakeFeedbackService(),
      onCommand: (action) async => actions.add(action),
    );

    final start = controller.beginPushToTalk();
    await controller.finishPushToTalk();
    await start;

    expect(speech.listenStarted, isFalse);
    expect(actions, isEmpty);
    controller.dispose();
  });
}

class _FakeSpeechRecognitionService extends SpeechRecognitionService {
  _FakeSpeechRecognitionService({
    required this.stopText,
    this.cancelDelay = Duration.zero,
  });

  final String stopText;
  final Duration cancelDelay;
  bool listenStarted = false;
  Completer<String>? _listenCompleter;

  @override
  Future<String> listenOnce({
    SpeechTextCallback? onText,
    Duration listenFor = const Duration(seconds: 10),
    Duration pauseFor = const Duration(seconds: 3),
    Duration timeout = const Duration(seconds: 12),
  }) {
    listenStarted = true;
    _listenCompleter = Completer<String>();
    return _listenCompleter!.future;
  }

  @override
  Future<String> stopAndGetText() async {
    _listenCompleter?.complete(stopText);
    return stopText;
  }

  @override
  Future<void> cancel() async {
    if (cancelDelay > Duration.zero) {
      await Future<void>.delayed(cancelDelay);
    }
  }

  @override
  Future<void> dispose() async {}
}

class _FakeFeedbackService extends FeedbackService {
  _FakeFeedbackService() : super(tts: _FakeTtsService());

  @override
  Future<void> action(String message, {bool interrupt = false}) async {}

  @override
  Future<void> hapticOnly() async {}
}

class _FakeTtsService extends TtsService {
  @override
  Future<void> stop() async {}

  @override
  Future<void> speakText(
    String text, {
    bool interrupt = false,
    bool ignoreMute = false,
  }) async {}
}
