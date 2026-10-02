import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';

import '../models/detection_response.dart';
import '../models/debug_event.dart';
import '../services/argus_api_service.dart';
import '../services/debug_log_service.dart';
import '../services/tts_service.dart';

class AnalysisController extends ChangeNotifier {
  AnalysisController({required this.api, required this.tts, required this.debugLog});

  final ArgusApiService api;
  final TtsService tts;
  final DebugLogService debugLog;
  int _operationSequence = 0;

  DetectionResponse? response;
  String status = 'Aguardando captura.';
  bool running = false;
  bool navigationMode = false;

  Future<void> analyze(CameraController camera) async {
    if (running) {
      return;
    }
    running = true;
    final operationId = 'analysis-${++_operationSequence}';
    debugLog.record(category: 'analysis', code: DebugEventCodes.captureStarted, message: 'Captura iniciada.', operationId: operationId);
    status = 'Analisando imagem.';
    notifyListeners();

    File? temporaryFile;
    try {
      final picture = await camera.takePicture();
      debugLog.record(category: 'analysis', code: DebugEventCodes.captureCompleted, message: 'Captura concluída.', operationId: operationId);
      temporaryFile = File(picture.path);
      final result = await api.detect(
        temporaryFile,
        mode: navigationMode ? 'navigation' : 'exploration',
        targetClass: navigationMode ? 'door' : null,
      );
      response = result;
      status = result.message;
      await tts.speak(result.audio);
      debugLog.record(category: 'analysis', code: DebugEventCodes.analysisCompleted, message: 'Análise concluída.', operationId: operationId);
    } on ArgusApiException catch (error) {
      status = error.message;
      debugLog.record(category: 'analysis', code: DebugEventCodes.analysisFailed, message: '${error.code}: ${error.message}', severity: DebugSeverity.error, operationId: operationId);
    } catch (error) {
      status = 'Nao foi possivel analisar a imagem agora.';
      debugLog.record(category: 'analysis', code: DebugEventCodes.analysisFailed, message: '${error.runtimeType}: $error', severity: DebugSeverity.error, operationId: operationId);
    } finally {
      if (temporaryFile != null && temporaryFile.existsSync()) {
        temporaryFile.deleteSync();
      }
      running = false;
      debugLog.record(category: 'analysis', code: DebugEventCodes.analysisFinished, message: 'Operação de análise encerrada.', operationId: operationId);
      notifyListeners();
    }
  }

  void setNavigationMode(bool value) {
    navigationMode = value;
    notifyListeners();
  }

  Future<void> stopAudio() => tts.stop();

  Future<void> repeatDescription() async {
    final audio = response?.audio;
    if (audio == null) {
      await tts.speakText('Ainda nao ha uma descricao para repetir.',
          interrupt: true);
      return;
    }
    await tts.speakText(audio.text, interrupt: true);
  }
}
