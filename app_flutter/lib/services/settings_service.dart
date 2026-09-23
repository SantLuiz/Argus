import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_config.dart';

@immutable
class ArgusSettings {
  const ArgusSettings({
    this.scheme = 'https',
    this.host = '',
    this.port,
    this.readyTimeoutSeconds = 5,
    this.detectTimeoutSeconds = 30,
    this.ttsVolumePercent = 100,
    this.showTranscription = true,
  });

  final String scheme;
  final String host;
  final int? port;
  final int readyTimeoutSeconds;
  final int detectTimeoutSeconds;
  final int ttsVolumePercent;
  final bool showTranscription;

  bool get hasBackend => host.trim().isNotEmpty;

  AppConfig get config => AppConfig(
        scheme: scheme,
        host: host.trim(),
        port: port,
        readyTimeoutSeconds: readyTimeoutSeconds,
        detectTimeoutSeconds: detectTimeoutSeconds,
      );

  double get ttsVolume => ttsVolumePercent.clamp(10, 100).toDouble() / 100;

  ArgusSettings copyWith({
    String? scheme,
    String? host,
    int? port,
    bool clearPort = false,
    int? readyTimeoutSeconds,
    int? detectTimeoutSeconds,
    int? ttsVolumePercent,
    bool? showTranscription,
  }) {
    return ArgusSettings(
      scheme: scheme ?? this.scheme,
      host: host ?? this.host,
      port: clearPort ? null : port ?? this.port,
      readyTimeoutSeconds: readyTimeoutSeconds ?? this.readyTimeoutSeconds,
      detectTimeoutSeconds: detectTimeoutSeconds ?? this.detectTimeoutSeconds,
      ttsVolumePercent: ttsVolumePercent ?? this.ttsVolumePercent,
      showTranscription: showTranscription ?? this.showTranscription,
    );
  }
}

class SettingsService extends ChangeNotifier {
  SettingsService({SharedPreferencesAsync? preferences})
      : _preferences = preferences ?? SharedPreferencesAsync();

  static const _schemeKey = 'argus.backend.scheme';
  static const _hostKey = 'argus.backend.host';
  static const _portKey = 'argus.backend.port';
  static const _readyTimeoutKey = 'argus.backend.readyTimeoutSeconds';
  static const _detectTimeoutKey = 'argus.backend.detectTimeoutSeconds';
  static const _ttsVolumeKey = 'argus.tts.volumePercent';
  static const _showTranscriptionKey = 'argus.voice.showTranscription';

  final SharedPreferencesAsync _preferences;

  ArgusSettings settings = const ArgusSettings();

  Future<void> load() async {
    final scheme = await _preferences.getString(_schemeKey);
    final host = await _preferences.getString(_hostKey);
    final port = await _preferences.getInt(_portKey);
    final readyTimeout = await _preferences.getInt(_readyTimeoutKey);
    final detectTimeout = await _preferences.getInt(_detectTimeoutKey);
    final volume = await _preferences.getInt(_ttsVolumeKey);
    final showTranscription = await _preferences.getBool(_showTranscriptionKey);
    settings = ArgusSettings(
      scheme: _validScheme(scheme) ? scheme! : 'https',
      host: host?.trim() ?? '',
      port: _validPort(port) ? port : null,
      readyTimeoutSeconds: _clampTimeout(readyTimeout, 5),
      detectTimeoutSeconds: _clampTimeout(detectTimeout, 30),
      ttsVolumePercent: _clampVolume(volume),
      showTranscription: showTranscription ?? true,
    );
    notifyListeners();
  }

  Future<void> save(ArgusSettings value) async {
    final normalized = ArgusSettings(
      scheme: _validScheme(value.scheme) ? value.scheme : 'https',
      host: value.host.trim(),
      port: _validPort(value.port) ? value.port : null,
      readyTimeoutSeconds: _clampTimeout(value.readyTimeoutSeconds, 5),
      detectTimeoutSeconds: _clampTimeout(value.detectTimeoutSeconds, 30),
      ttsVolumePercent: _clampVolume(value.ttsVolumePercent),
      showTranscription: value.showTranscription,
    );
    await _preferences.setString(_schemeKey, normalized.scheme);
    await _preferences.setString(_hostKey, normalized.host);
    if (normalized.port == null) {
      await _preferences.remove(_portKey);
    } else {
      await _preferences.setInt(_portKey, normalized.port!);
    }
    await _preferences.setInt(_readyTimeoutKey, normalized.readyTimeoutSeconds);
    await _preferences.setInt(
        _detectTimeoutKey, normalized.detectTimeoutSeconds);
    await _preferences.setInt(_ttsVolumeKey, normalized.ttsVolumePercent);
    await _preferences.setBool(
        _showTranscriptionKey, normalized.showTranscription);
    settings = normalized;
    notifyListeners();
  }

  Future<void> setVolumePercent(int value) =>
      save(settings.copyWith(ttsVolumePercent: _clampVolume(value)));

  Future<void> setShowTranscription(bool value) =>
      save(settings.copyWith(showTranscription: value));

  static bool _validScheme(String? value) =>
      value == 'https' || value == 'http';

  static bool _validPort(int? value) =>
      value == null || value >= 1 && value <= 65535;

  static int _clampTimeout(int? value, int fallback) =>
      (value ?? fallback).clamp(1, 120).toInt();

  static int _clampVolume(int? value) => (value ?? 100).clamp(10, 100).toInt();
}
