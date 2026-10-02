import 'dart:math' as math;

enum BenchmarkCandidate { previewOnly, efficientDetLite0, yoloV8n }

class NormalizedBox {
  const NormalizedBox({
    required this.left,
    required this.top,
    required this.right,
    required this.bottom,
  });

  final double left;
  final double top;
  final double right;
  final double bottom;

  double get width => right - left;
  double get height => bottom - top;
  double get area => math.max(0, width) * math.max(0, height);

  NormalizedBox clamped() => NormalizedBox(
        left: left.clamp(0.0, 1.0),
        top: top.clamp(0.0, 1.0),
        right: right.clamp(0.0, 1.0),
        bottom: bottom.clamp(0.0, 1.0),
      );

  double intersectionOverUnion(NormalizedBox other) {
    final intersectionWidth =
        math.max(0.0, math.min(right, other.right) - math.max(left, other.left));
    final intersectionHeight =
        math.max(0.0, math.min(bottom, other.bottom) - math.max(top, other.top));
    final intersection = intersectionWidth * intersectionHeight;
    final union = area + other.area - intersection;
    return union <= 0 ? 0 : intersection / union;
  }
}

class BenchmarkDetection {
  const BenchmarkDetection({
    required this.classIndex,
    required this.label,
    required this.confidence,
    required this.box,
  });

  final int classIndex;
  final String label;
  final double confidence;
  final NormalizedBox box;
}

/// Resultado do último frame, sem rastreamento entre frames.
class BenchmarkSnapshot {
  BenchmarkSnapshot({
    required this.frameId,
    required this.capturedAtMicros,
    required this.completedAtMicros,
    required List<BenchmarkDetection> detections,
  }) : detections = List.unmodifiable(detections);

  final int frameId;
  final int capturedAtMicros;
  final int completedAtMicros;
  final List<BenchmarkDetection> detections;

  int get captureToResultMicros => completedAtMicros - capturedAtMicros;

  bool isFreshAt(int monotonicMicros, {int lifetimeMicros = 1000000}) =>
      monotonicMicros - capturedAtMicros < lifetimeMicros;
}

class BenchmarkMetrics {
  const BenchmarkMetrics({
    required this.acceptedFrames,
    required this.completedFrames,
    required this.droppedFrames,
    required this.captureToResultMicros,
  });

  final int acceptedFrames;
  final int completedFrames;
  final int droppedFrames;
  final List<int> captureToResultMicros;

  double? percentile(double fraction) {
    if (captureToResultMicros.isEmpty) return null;
    final sorted = [...captureToResultMicros]..sort();
    final index = ((sorted.length - 1) * fraction).round();
    return sorted[index] / 1000;
  }
}

abstract class BenchmarkDetector {
  Future<List<BenchmarkDetection>> detect(BenchmarkFrame frame);
  Future<void> close();
}

class BenchmarkFrame {
  const BenchmarkFrame({
    required this.id,
    required this.capturedAtMicros,
    required this.width,
    required this.height,
    required this.rgb,
    this.contentLeft = 0,
    this.contentTop = 0,
    this.contentWidth = 1,
    this.contentHeight = 1,
  });

  final int id;
  final int capturedAtMicros;
  final int width;
  final int height;
  final List<int> rgb;
  final double contentLeft;
  final double contentTop;
  final double contentWidth;
  final double contentHeight;

  BenchmarkDetection unletterbox(BenchmarkDetection detection) {
    final box = detection.box;
    return BenchmarkDetection(
      classIndex: detection.classIndex,
      label: detection.label,
      confidence: detection.confidence,
      box: NormalizedBox(
        left: (box.left - contentLeft) / contentWidth,
        top: (box.top - contentTop) / contentHeight,
        right: (box.right - contentLeft) / contentWidth,
        bottom: (box.bottom - contentTop) / contentHeight,
      ).clamped(),
    );
  }
}

/// Controla backpressure: um frame em voo, nenhum frame em fila, máximo de 5 Hz.
class BenchmarkFrameScheduler {
  BenchmarkFrameScheduler({required this.detector, required this.nowMicros});

  final BenchmarkDetector detector;
  final int Function() nowMicros;
  static const int minimumIntervalMicros = 200000;

  bool _busy = false;
  int? _lastAcceptedMicros;
  int _accepted = 0;
  int _completed = 0;
  int _dropped = 0;
  final List<int> _latencies = [];
  BenchmarkSnapshot? _latest;

  BenchmarkSnapshot? get latest {
    final value = _latest;
    if (value == null || !value.isFreshAt(nowMicros())) return null;
    return value;
  }

  BenchmarkMetrics get metrics => BenchmarkMetrics(
        acceptedFrames: _accepted,
        completedFrames: _completed,
        droppedFrames: _dropped,
        captureToResultMicros: List.unmodifiable(_latencies),
      );

  Future<bool> offer(BenchmarkFrame frame) async {
    final previous = _lastAcceptedMicros;
    if (_busy || (previous != null && frame.capturedAtMicros - previous < minimumIntervalMicros)) {
      _dropped++;
      return false;
    }
    _busy = true;
    _lastAcceptedMicros = frame.capturedAtMicros;
    _accepted++;
    try {
      final detections = await detector.detect(frame);
      final completedAt = nowMicros();
      _latest = BenchmarkSnapshot(
        frameId: frame.id,
        capturedAtMicros: frame.capturedAtMicros,
        completedAtMicros: completedAt,
        detections: detections,
      );
      _completed++;
      _latencies.add(completedAt - frame.capturedAtMicros);
      return true;
    } catch (_) {
      _latest = null;
      rethrow;
    } finally {
      _busy = false;
    }
  }

  void invalidate() => _latest = null;
}

List<BenchmarkDetection> decodeEfficientDet({
  required List<List<double>> boxes,
  required List<double> classes,
  required List<double> scores,
  required int count,
  required List<String> labels,
  double threshold = 0.5,
}) {
  final result = <BenchmarkDetection>[];
  final limit = math.min(count, math.min(boxes.length, math.min(classes.length, scores.length)));
  for (var i = 0; i < limit; i++) {
    if (scores[i] < threshold || boxes[i].length < 4) continue;
    final classIndex = classes[i].round();
    final box = boxes[i]; // DetectionPostProcess: top, left, bottom, right.
    result.add(BenchmarkDetection(
      classIndex: classIndex,
      label: classIndex >= 0 && classIndex < labels.length ? labels[classIndex] : 'classe $classIndex',
      confidence: scores[i],
      box: NormalizedBox(left: box[1], top: box[0], right: box[3], bottom: box[2]).clamped(),
    ));
  }
  return result;
}

List<BenchmarkDetection> decodeYoloV8(
  List<List<double>> features, {
  required List<String> labels,
  double threshold = 0.5,
  double nmsThreshold = 0.45,
}) {
  if (features.isEmpty) return const [];
  // Aceita [84,N] (export padrão) e [N,84].
  final rows = features.length <= 100 && features.first.length > features.length
      ? List.generate(features.first.length, (column) => List.generate(features.length, (row) => features[row][column]))
      : features;
  final candidates = <BenchmarkDetection>[];
  for (final row in rows) {
    if (row.length < 5) continue;
    var classIndex = 0;
    var score = row[4];
    for (var i = 5; i < row.length; i++) {
      if (row[i] > score) {
        score = row[i];
        classIndex = i - 4;
      }
    }
    if (score < threshold) continue;
    final centerX = row[0], centerY = row[1], width = row[2], height = row[3];
    candidates.add(BenchmarkDetection(
      classIndex: classIndex,
      label: classIndex < labels.length ? labels[classIndex] : 'classe $classIndex',
      confidence: score,
      box: NormalizedBox(
        left: centerX - width / 2,
        top: centerY - height / 2,
        right: centerX + width / 2,
        bottom: centerY + height / 2,
      ).clamped(),
    ));
  }
  candidates.sort((a, b) => b.confidence.compareTo(a.confidence));
  final kept = <BenchmarkDetection>[];
  for (final candidate in candidates) {
    if (kept.any((other) => other.classIndex == candidate.classIndex &&
        other.box.intersectionOverUnion(candidate.box) > nmsThreshold)) {
      continue;
    }
    kept.add(candidate);
  }
  return kept;
}
