import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;

import 'benchmark_detector.dart';

BenchmarkFrame convertCameraFrame({
  required CameraImage cameraImage,
  required int frameId,
  required int capturedAtMicros,
  required int rotationDegrees,
  required int targetWidth,
  required int targetHeight,
}) {
  if (cameraImage.planes.length < 3) {
    throw StateError('O benchmark Android exige câmera YUV420 com três planos.');
  }
  final source = img.Image(width: cameraImage.width, height: cameraImage.height);
  final yPlane = cameraImage.planes[0];
  final uPlane = cameraImage.planes[1];
  final vPlane = cameraImage.planes[2];
  final uvPixelStride = uPlane.bytesPerPixel ?? 1;
  for (var y = 0; y < cameraImage.height; y++) {
    for (var x = 0; x < cameraImage.width; x++) {
      final yValue = yPlane.bytes[y * yPlane.bytesPerRow + x];
      final uvIndex = (y ~/ 2) * uPlane.bytesPerRow + (x ~/ 2) * uvPixelStride;
      final uValue = uPlane.bytes[uvIndex];
      final vValue = vPlane.bytes[uvIndex];
      final c = yValue - 16;
      final d = uValue - 128;
      final e = vValue - 128;
      source.setPixelRgba(
        x,
        y,
        ((298 * c + 409 * e + 128) >> 8).clamp(0, 255),
        ((298 * c - 100 * d - 208 * e + 128) >> 8).clamp(0, 255),
        ((298 * c + 516 * d + 128) >> 8).clamp(0, 255),
        255,
      );
    }
  }
  final oriented = rotationDegrees % 360 == 0
      ? source
      : img.copyRotate(source, angle: rotationDegrees.toDouble());
  final scale = targetWidth / oriented.width < targetHeight / oriented.height
      ? targetWidth / oriented.width
      : targetHeight / oriented.height;
  final resizedWidth = (oriented.width * scale).round();
  final resizedHeight = (oriented.height * scale).round();
  final resized = img.copyResize(oriented, width: resizedWidth, height: resizedHeight);
  final canvas = img.Image(width: targetWidth, height: targetHeight);
  img.fill(canvas, color: img.ColorRgb8(114, 114, 114));
  final offsetX = (targetWidth - resizedWidth) ~/ 2;
  final offsetY = (targetHeight - resizedHeight) ~/ 2;
  img.compositeImage(canvas, resized, dstX: offsetX, dstY: offsetY);
  final rgb = Uint8List(targetWidth * targetHeight * 3);
  var offset = 0;
  for (final pixel in canvas) {
    rgb[offset++] = pixel.r.toInt();
    rgb[offset++] = pixel.g.toInt();
    rgb[offset++] = pixel.b.toInt();
  }
  return BenchmarkFrame(
    id: frameId,
    capturedAtMicros: capturedAtMicros,
    width: targetWidth,
    height: targetHeight,
    rgb: rgb,
    contentLeft: offsetX / targetWidth,
    contentTop: offsetY / targetHeight,
    contentWidth: resizedWidth / targetWidth,
    contentHeight: resizedHeight / targetHeight,
  );
}
