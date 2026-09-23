import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';

import '../models/detection_response.dart';
import '../services/argus_api_service.dart';
import '../services/tts_service.dart';

class AnalysisController extends ChangeNotifier {
  AnalysisController({required this.api, required this.tts});

  final ArgusApiService api;
  final TtsService tts;

  DetectionResponse? response;
  String status = 'Aguardando captura.';
  bool running = false;
  bool navigationMode = false;

  Future<void> analyze(CameraController camera) async {
    if (running) {
      return;
    }
    running = true;
    status = 'Analisando imagem.';
    notifyListeners();

    File? temporaryFile;
    try {
      final picture = await camera.takePicture();
      temporaryFile = File(picture.path);
      final result = await api.detect(
        temporaryFile,
        mode: navigationMode ? 'navigation' : 'exploration',
        targetClass: navigationMode ? 'door' : null,
      );
      response = result;
      status = result.message;
      await tts.speak(result.audio);
    } on ArgusApiException catch (error) {
      status = error.message;
    } catch (_) {
      status = 'Nao foi possivel analisar a imagem agora.';
    } finally {
      if (temporaryFile != null && temporaryFile.existsSync()) {
        temporaryFile.deleteSync();
      }
      running = false;
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
