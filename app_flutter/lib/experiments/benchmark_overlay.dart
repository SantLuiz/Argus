import 'package:flutter/material.dart';

import 'benchmark_detector.dart';

class BenchmarkOverlay extends StatelessWidget {
  const BenchmarkOverlay({super.key, required this.snapshot});

  final BenchmarkSnapshot snapshot;

  @override
  Widget build(BuildContext context) => IgnorePointer(
        child: CustomPaint(
          painter: _BoxPainter(snapshot.detections),
          size: Size.infinite,
        ),
      );
}

class _BoxPainter extends CustomPainter {
  _BoxPainter(this.detections);
  final List<BenchmarkDetection> detections;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.amber
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    for (final detection in detections) {
      final box = detection.box;
      final rect = Rect.fromLTRB(box.left * size.width, box.top * size.height,
          box.right * size.width, box.bottom * size.height);
      canvas.drawRect(rect, paint);
      final text = TextPainter(
        text: TextSpan(
          text: '${detection.label} ${(detection.confidence * 100).round()}%',
          style: const TextStyle(color: Colors.black, backgroundColor: Colors.amber, fontSize: 14),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width);
      text.paint(canvas, Offset(rect.left, (rect.top - text.height).clamp(0, size.height)));
    }
  }

  @override
  bool shouldRepaint(_BoxPainter oldDelegate) => oldDelegate.detections != detections;
}
