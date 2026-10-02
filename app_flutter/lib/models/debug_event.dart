import 'package:flutter/foundation.dart';

enum DebugSeverity { info, warning, error }

@immutable
class DebugEvent {
  const DebugEvent({
    required this.sequence,
    required this.timestamp,
    required this.category,
    required this.severity,
    required this.code,
    required this.message,
    this.operationId,
  });

  final int sequence;
  final DateTime timestamp;
  final String category;
  final DebugSeverity severity;
  final String code;
  final String message;
  final String? operationId;
}

abstract final class DebugEventCodes {
  static const debugEnabled = 'debug.enabled';
  static const settingChanged = 'settings.changed';
  static const cameraInitializing = 'camera.initializing';
  static const cameraReady = 'camera.ready';
  static const cameraFailed = 'camera.failed';
  static const appLifecycle = 'app.lifecycle';
  static const settingsOpened = 'settings.opened';
  static const settingsClosed = 'settings.closed';
  static const captureStarted = 'analysis.capture_started';
  static const captureCompleted = 'analysis.capture_completed';
  static const analysisCompleted = 'analysis.completed';
  static const analysisFailed = 'analysis.failed';
  static const analysisFinished = 'analysis.finished';
  static const requestStarted = 'network.request_started';
  static const responseReceived = 'network.response_received';
  static const requestTimeout = 'network.timeout';
  static const connectionFailed = 'network.connection_failed';
  static const invalidResponse = 'network.invalid_response';
  static const configurationMissing = 'network.configuration_missing';
  static const speechInitialization = 'speech.initialization';
  static const speechAvailability = 'speech.availability';
  static const speechListenRequested = 'speech.listen_requested';
  static const speechStatus = 'speech.status';
  static const speechPartial = 'speech.partial';
  static const speechFinal = 'speech.final';
  static const speechTimeout = 'speech.timeout';
  static const speechError = 'speech.error';
  static const speechStopped = 'speech.stopped';
  static const speechCanceled = 'speech.canceled';
  static const passiveStarted = 'voice.passive_started';
  static const passiveSuspended = 'voice.passive_suspended';
  static const wakeWord = 'voice.wake_word';
  static const parserAccepted = 'voice.parser_accepted';
  static const parserRejected = 'voice.parser_rejected';
  static const actionStarted = 'voice.action_started';
  static const actionCompleted = 'voice.action_completed';
  static const actionFailed = 'voice.action_failed';
  static const pushToTalkStarted = 'voice.ptt_started';
  static const pushToTalkFinished = 'voice.ptt_finished';
  static const ttsConfigured = 'tts.configured';
  static const ttsSpeakRequested = 'tts.speak_requested';
  static const ttsSpeakCompleted = 'tts.speak_completed';
  static const ttsStopped = 'tts.stopped';
  static const ttsFailed = 'tts.failed';
}
