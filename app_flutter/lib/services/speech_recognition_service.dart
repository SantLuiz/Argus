import 'dart:async';

import 'package:speech_to_text/speech_recognition_error.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';

import '../models/debug_event.dart';
import 'debug_log_service.dart';

typedef SpeechTextCallback = void Function(String text);

class SpeechRecognitionService {
  SpeechRecognitionService({SpeechToText? speech, DebugLogService? debugLog})
      : _speech = speech ?? SpeechToText(),
        _debugLog = debugLog;

  final SpeechToText _speech;
  final DebugLogService? _debugLog;
  bool _initialized = false;
  Completer<String>? _activeCompleter;
  String _bestWords = '';
  int _listenSession = 0;
  int? _activeListenSession;
  Future<void> _speechOperation = Future<void>.value();

  Future<String> listenOnce({
    SpeechTextCallback? onText,
    Duration listenFor = const Duration(seconds: 10),
    Duration pauseFor = const Duration(seconds: 3),
    Duration timeout = const Duration(seconds: 12),
  }) async {
    await cancel();
    final completer = Completer<String>();
    final session = ++_listenSession;
    _activeListenSession = session;
    _activeCompleter = completer;
    _bestWords = '';
    String lastReportedWords = '';
    final operationId = 'speech-$session';
    _record(DebugEventCodes.speechListenRequested, 'Escuta solicitada em pt_BR.', operationId: operationId);
    _log('listenOnce start session=$session');
    if (!_initialized) {
      _initialized = await _speech.initialize(
        debugLogging: false,
        finalTimeout: const Duration(seconds: 3),
        onError: (SpeechRecognitionError error) {
          _record(DebugEventCodes.speechError,
              '${error.errorMsg}; permanente=${error.permanent}.',
              severity: DebugSeverity.error,
              operationId: _activeListenSession == null
                  ? null
                  : 'speech-$_activeListenSession');
          _log(
            'error session=$_activeListenSession msg=${error.errorMsg} '
            'permanent=${error.permanent}',
          );
          final active = _activeCompleter;
          if (active != null && !active.isCompleted) {
            active.completeError(Exception(error.errorMsg));
          }
        },
        onStatus: (status) {
          _record(DebugEventCodes.speechStatus, 'Status nativo: $status.',
              operationId: _activeListenSession == null
                  ? null
                  : 'speech-$_activeListenSession');
          _log(
            'status session=$_activeListenSession status=$status '
            'best="$_bestWords"',
          );
          if (status == 'done' &&
              _activeCompleter != null &&
              !_activeCompleter!.isCompleted &&
              _bestWords.isNotEmpty) {
            _activeCompleter!.complete(_bestWords);
          }
        },
      );
      _record(DebugEventCodes.speechAvailability, _initialized ? 'Reconhecimento de fala disponível.' : 'Reconhecimento de fala indisponível.', severity: _initialized ? DebugSeverity.info : DebugSeverity.warning, operationId: operationId);
    }
    if (!_initialized) {
      throw Exception('Reconhecimento de fala indisponivel.');
    }

    await _runSpeechOperation(
      () => _speech.listen(
        localeId: 'pt_BR',
        listenFor: listenFor,
        pauseFor: pauseFor,
        onResult: (SpeechRecognitionResult result) {
          if (_activeListenSession != session) return;
          _bestWords = result.recognizedWords.trim();
          _log(
            'result session=$session final=${result.finalResult} '
            'words="$_bestWords"',
          );
          if (result.finalResult || _bestWords != lastReportedWords) {
            lastReportedWords = _bestWords;
            _record(result.finalResult ? DebugEventCodes.speechFinal : DebugEventCodes.speechPartial, result.finalResult ? 'Texto final: "$_bestWords".' : 'Texto parcial: "$_bestWords".', operationId: operationId);
            onText?.call(_bestWords);
          }
          if (result.finalResult && !completer.isCompleted) {
            completer.complete(_bestWords);
          }
        },
      ),
    );

    return completer.future.timeout(
      timeout,
      onTimeout: () async {
        _record(DebugEventCodes.speechTimeout, 'Tempo limite da escuta.', severity: DebugSeverity.warning, operationId: operationId);
        _log('timeout session=$session best="$_bestWords"');
        await _stopSpeech();
        return _bestWords;
      },
    ).whenComplete(() {
      _log('listenOnce complete session=$session best="$_bestWords"');
      if (identical(_activeCompleter, completer)) {
        _activeCompleter = null;
        _activeListenSession = null;
      }
    });
  }

  Future<String> stopAndGetText() async {
    final active = _activeCompleter;
    _log(
      'stopAndGetText requested best="$_bestWords" hasActive=${active != null}',
    );
    await _stopSpeech();
    _record(DebugEventCodes.speechStopped, 'Parada da escuta solicitada.', operationId: _activeListenSession == null ? null : 'speech-$_activeListenSession');
    if (active != null && !active.isCompleted) {
      await Future<void>.delayed(const Duration(milliseconds: 900));
    }
    if (active != null && !active.isCompleted) {
      active.complete(_bestWords);
    }
    final text = active == null ? _bestWords : await active.future;
    _log('stopAndGetText complete text="$text"');
    return text;
  }

  Future<void> cancel() async {
    _log('cancel requested');
    await _runSpeechOperation(_speech.cancel);
    _record(DebugEventCodes.speechCanceled, 'Escuta cancelada.', operationId: _activeListenSession == null ? null : 'speech-$_activeListenSession');
    final active = _activeCompleter;
    if (active != null && !active.isCompleted) {
      active.complete('');
    }
    _activeCompleter = null;
    _activeListenSession = null;
    _bestWords = '';
  }

  Future<void> dispose() async {
    await cancel();
    await _stopSpeech();
  }

  Future<void> _stopSpeech() => _runSpeechOperation(_speech.stop);

  Future<T> _runSpeechOperation<T>(Future<T> Function() operation) {
    final nextOperation = _speechOperation.then((_) => operation());
    _speechOperation = nextOperation.then<void>(
      (_) {},
      onError: (_) {},
    );
    return nextOperation;
  }

  void _log(String message) {
    // Mantém os pontos de diagnóstico existentes sem emitir eventos duplicados.
  }

  void _record(String code, String message, {DebugSeverity severity = DebugSeverity.info, String? operationId}) {
    _debugLog?.record(category: 'speech', code: code, message: message, severity: severity, operationId: operationId);
  }
}
