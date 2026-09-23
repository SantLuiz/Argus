import 'package:flutter/services.dart';

class MediaVolumeService {
  const MediaVolumeService({MethodChannel? channel})
      : _channel = channel ?? const MethodChannel('argus/media_volume');

  final MethodChannel _channel;

  Future<int?> changeBySteps(int steps) async {
    try {
      return await _channel.invokeMethod<int>('changeBySteps', {
        'steps': steps,
      });
    } on PlatformException {
      return null;
    }
  }
}
