import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/voice_command.dart';
import '../models/voice_state.dart';
import '../services/feedback_service.dart';
import '../services/speech_recognition_service.dart';
import '../services/voice_command_parser.dart';

typedef VoiceCommandHandler = Future<void> Function(VoiceAction action);

class VoiceInputController extends ChangeNotifier {
  VoiceInputController({
    required SpeechRecognitionService speech,
    required FeedbackService feedback,
    required VoiceCommandHandler onCommand,
    VoiceCommandParser parser = const VoiceCommandParser(),
  })  : _speech = speech,
        _feedback = feedback,
        _onCommand = onCommand,
        _parser = parser;

  final SpeechRecognitionService _speech;
  final FeedbackService _feedback;
  final VoiceCommandHandler _onCommand;
  final VoiceCommandParser _parser;

  VoiceState state = const VoiceState();
  bool _passiveRequested = false;
  bool _disposed = false;
  int _session = 0;
  int? _wakeFeedbackSession;
  bool _pushStartInProgress = false;
  bool _pushFinishRequested = false;
  bool _pushProcessed = false;

  void updateTranscriptionPreference(bool value) {
    state = state.copyWith(showTranscription: value);
    notifyListeners();
  }

  Future<void> startPassive() async {
    if (_disposed || _passiveRequested || state.pushToTalkActive) {
      return;
    }
    _passiveRequested = true;
    _runPassiveLoop(++_session);
  }

  Future<void> suspendPassive({String message = ''}) async {
    _passiveRequested = false;
    _session++;
    await _speech.cancel();
    state = state.copyWith(
      mode: VoiceInputMode.suspended,
      listening: false,
      processing: false,
      transcription: '',
      message: message,
    );
    notifyListeners();
  }

  Future<void> beginPushToTalk() async {
    if (_disposed || state.processing) {
      return;
    }
    _passiveRequested = false;
    final session = ++_session;
    _pushStartInProgress = true;
    _pushFinishRequested = false;
    _pushProcessed = false;
    _log('push start requested session=$session');
    state = state.copyWith(
      mode: VoiceInputMode.pushToTalk,
      listening: true,
      processing: false,
      transcription: '',
      message: 'Ouvindo comando.',
    );
    notifyListeners();
    await _feedback.tts.stop();
    await _speech.cancel();
    _pushStartInProgress = false;
    if (_disposed || session != _session || _pushFinishRequested) {
      _log('push start canceled before native listen session=$session');
      await startPassive();
      return;
    }
    unawaited(_listenPushToTalk(session));
  }

  Future<void> finishPushToTalk() async {
    if (_pushStartInProgress) {
      _pushFinishRequested = true;
      _log('push finish requested before native listen');
      return;
    }
    if (!state.pushToTalkActive || _pushProcessed) {
      return;
    }
    final session = _session;
    _log('push finish requested session=$session');
    final text = await _speech.stopAndGetText();
    await _completePushToTalk(session, text);
    await startPassive();
  }

  Future<void> toggleAccessiblePushToTalk() async {
    if (state.pushToTalkActive) {
      await finishPushToTalk();
      return;
    }
    await beginPushToTalk();
  }

  Future<void> _runPassiveLoop(int session) async {
    while (!_disposed &&
        _passiveRequested &&
        session == _session &&
        !state.pushToTalkActive) {
      state = state.copyWith(
        mode: VoiceInputMode.passive,
        listening: true,
        processing: false,
        transcription: '',
        message: 'Escuta passiva ativa.',
      );
      notifyListeners();
      try {
        final text = await _speech.listenOnce(
          onText: (partial) => _setPassiveTranscription(partial, session),
        );
        if (!_passiveRequested || session != _session) {
          return;
        }
        await _processRecognizedText(text, requireWakeWord: true);
      } catch (_) {
        if (!_disposed && _passiveRequested && session == _session) {
          state = state.copyWith(
            listening: false,
            message: 'Reconhecimento de voz indisponivel.',
          );
          notifyListeners();
          await Future<void>.delayed(const Duration(seconds: 2));
        }
      }
    }
  }

  Future<String> _listenPushToTalk(int session) async {
    try {
      final text = await _speech.listenOnce(
        listenFor: const Duration(seconds: 15),
        pauseFor: const Duration(seconds: 15),
        timeout: const Duration(seconds: 16),
        onText: (partial) {
          if (session != _session || !state.pushToTalkActive) {
            return;
          }
          state = state.copyWith(transcription: partial);
          notifyListeners();
        },
      );
      _log('push native listen completed session=$session text="$text"');
      if (!_pushProcessed && session == _session && state.pushToTalkActive) {
        await _completePushToTalk(session, text);
        await startPassive();
      }
      return text;
    } catch (_) {
      if (!_disposed && session == _session) {
        state = state.copyWith(
          mode: VoiceInputMode.idle,
          listening: false,
          message: 'Nao foi possivel ouvir o comando agora.',
        );
        notifyListeners();
        await _feedback.action('Nao foi possivel ouvir o comando agora.',
            interrupt: true);
      }
      return '';
    }
  }

  Future<void> _completePushToTalk(int session, String text) async {
    if (_disposed || _pushProcessed || session != _session) {
      return;
    }
    _pushProcessed = true;
    _log('push processing session=$session text="$text"');
    await _processRecognizedText(text, requireWakeWord: false);
  }

  void _setPassiveTranscription(String text, int session) {
    if (session != _session || !_passiveRequested) {
      return;
    }
    final commandText = _parser.commandAfterWakeWord(text);
    if (commandText == null) {
      return;
    }
    state = state.copyWith(
      mode: VoiceInputMode.wakeCommand,
      transcription: commandText.isEmpty ? 'Argus' : commandText,
      message: 'Argus reconhecido.',
    );
    notifyListeners();
    if (_wakeFeedbackSession != session) {
      _wakeFeedbackSession = session;
      _feedback.hapticOnly();
    }
  }

  Future<void> _processRecognizedText(
    String text, {
    required bool requireWakeWord,
  }) async {
    _log('parse text="$text" requireWakeWord=$requireWakeWord');
    final command = _parser.parse(text, requireWakeWord: requireWakeWord);
    if (command == null) {
      _log('parse rejected text="$text" requireWakeWord=$requireWakeWord');
      state = state.copyWith(
        mode: VoiceInputMode.idle,
        listening: false,
        processing: false,
        transcription: text,
        message: requireWakeWord
            ? 'Aguardando comando com Argus.'
            : 'Comando nao reconhecido.',
      );
      notifyListeners();
      if (!requireWakeWord) {
        await _feedback.action('Comando nao reconhecido.', interrupt: true);
      }
      return;
    }
    _log('parse accepted action=${command.action.name}');
    state = state.copyWith(
      mode: VoiceInputMode.executing,
      listening: false,
      processing: true,
      transcription: text,
      message: 'Executando comando.',
    );
    notifyListeners();
    await _onCommand(command.action);
    state = state.copyWith(
      mode: VoiceInputMode.idle,
      listening: false,
      processing: false,
      message: 'Comando executado.',
    );
    notifyListeners();
  }

  void _log(String message) {
    if (kDebugMode) {
      debugPrint('[ARGUS_VOICE][VoiceInputController] $message');
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _passiveRequested = false;
    _session++;
    _speech.dispose();
    super.dispose();
  }
}
