import 'package:flutter/services.dart';

class SystemUiService {
  static const _channel = MethodChannel('argus/system_ui');

  static Future<void> enterCameraMode() async {
    await SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
    await SystemChrome.setPreferredOrientations([]);
    try {
      await _channel.invokeMethod<void>('enterCameraMode');
    } catch (_) {
      // Flutter's SystemChrome remains the fallback on platforms without the channel.
    }
  }

  static Future<void> exitCameraMode() async {
    await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    try {
      await _channel.invokeMethod<void>('exitCameraMode');
    } catch (_) {}
  }
}
