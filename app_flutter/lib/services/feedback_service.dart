import 'package:flutter/services.dart';

import 'tts_service.dart';

class FeedbackService {
  FeedbackService({required this.tts});

  final TtsService tts;

  Future<void> action(String message, {bool interrupt = false}) async {
    await HapticFeedback.selectionClick();
    await tts.speakText(message, interrupt: interrupt);
  }

  Future<void> hapticOnly() => HapticFeedback.selectionClick();
}
