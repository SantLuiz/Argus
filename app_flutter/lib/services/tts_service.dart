import 'package:flutter_tts/flutter_tts.dart';

import '../models/detection_response.dart';

class TtsService {
  TtsService({FlutterTts? tts}) : _tts = tts ?? FlutterTts();

  final FlutterTts _tts;
  String? _activeText;
  DateTime _lastSpokenAt = DateTime.fromMillisecondsSinceEpoch(0);
  bool _muted = false;
  bool _hasBrazilianVoice = false;

  bool get muted => _muted;

  bool get hasBrazilianVoice => _hasBrazilianVoice;

  Future<void> configure() async {
    await _tts.awaitSpeakCompletion(true);
    await _tts.setLanguage('pt-BR');
    await _tts.setSpeechRate(0.48);
    await _tts.setVolume(1);
    _hasBrazilianVoice = await _selectBrazilianVoice();
  }

  Future<void> setMuted(bool value) async {
    _muted = value;
    if (value) {
      await _tts.stop();
    }
  }

  Future<void> toggleMuted() async {
    final next = !_muted;
    await setMuted(next);
    if (!next) {
      await speakText('Audio ativado.', interrupt: true, ignoreMute: true);
    }
  }

  Future<void> speak(AudioPayload audio) async {
    final text = audio.text.trim();
    if (text.isEmpty || _muted) {
      return;
    }

    final now = DateTime.now();
    final isCritical = audio.priority == 'critical';
    final sameAsActive = _activeText == text;
    final cooldown =
        isCritical ? const Duration(seconds: 3) : const Duration(seconds: 8);
    if (sameAsActive && now.difference(_lastSpokenAt) < cooldown) {
      return;
    }

    if (isCritical) {
      await _tts.stop();
    }
    _activeText = text;
    _lastSpokenAt = now;
    await _tts.speak(text);
  }

  Future<void> speakText(
    String text, {
    bool interrupt = false,
    bool ignoreMute = false,
  }) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || (_muted && !ignoreMute)) {
      return;
    }
    if (interrupt) {
      await _tts.stop();
    }
    _activeText = trimmed;
    _lastSpokenAt = DateTime.now();
    await _tts.speak(trimmed);
  }

  Future<void> stop() => _tts.stop();

  Future<bool> _selectBrazilianVoice() async {
    try {
      final voices = await _tts.getVoices;
      final voice = _findBrazilianVoice(voices);
      if (voice == null) {
        return false;
      }
      await _tts.setVoice(voice);
      return true;
    } catch (_) {
      return false;
    }
  }

  static Map<String, String>? _findBrazilianVoice(dynamic voices) {
    if (voices is! Iterable) {
      return null;
    }

    final candidates = voices.whereType<Map>().map((voice) {
      return voice.map((key, value) => MapEntry('$key', '$value'));
    }).where((voice) {
      final locale = _normalize(voice['locale'] ?? voice['language'] ?? '');
      return locale == 'pt-br' || locale == 'pt_br' || locale == 'ptbr';
    }).toList();

    if (candidates.isEmpty) {
      return null;
    }

    candidates.sort((a, b) {
      final aScore = _voiceScore(a);
      final bScore = _voiceScore(b);
      return bScore.compareTo(aScore);
    });
    return candidates.first;
  }

  static int _voiceScore(Map<String, String> voice) {
    final text = _normalize('${voice['name']} ${voice['quality']}');
    var score = 0;
    if (text.contains('brasil') || text.contains('brazil')) {
      score += 4;
    }
    if (text.contains('female') || text.contains('feminina')) {
      score += 1;
    }
    if (text.contains('network')) {
      score -= 1;
    }
    if (text.contains('not installed')) {
      score -= 4;
    }
    return score;
  }

  static String _normalize(String value) {
    return value.toLowerCase().replaceAll('_', '-').trim();
  }
}
