import 'dart:typed_data';

import 'package:tflite_flutter/tflite_flutter.dart';

import 'benchmark_detector.dart';

const cocoLabels = <String>[
  'person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light',
  'fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow',
  'elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee',
  'skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard',
  'tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple',
  'sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch',
  'potted plant','bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone',
  'microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear',
  'hair drier','toothbrush',
];

class TfliteBenchmarkDetector implements BenchmarkDetector {
  TfliteBenchmarkDetector._(this.candidate, this._interpreter, this._isolate);

  final BenchmarkCandidate candidate;
  final Interpreter _interpreter;
  final IsolateInterpreter _isolate;

  static Future<TfliteBenchmarkDetector> load(BenchmarkCandidate candidate) async {
    if (candidate == BenchmarkCandidate.previewOnly) {
      throw ArgumentError('Preview não carrega detector.');
    }
    final asset = candidate == BenchmarkCandidate.efficientDetLite0
        ? 'assets/mobile_models/efficientdet_lite0_int8.tflite'
        : 'assets/mobile_models/yolov8n_float32_320.tflite';
    final options = InterpreterOptions()..threads = 2;
    final interpreter = await Interpreter.fromAsset(asset, options: options);
    final isolate = await IsolateInterpreter.create(address: interpreter.address);
    return TfliteBenchmarkDetector._(candidate, interpreter, isolate);
  }

  @override
  Future<List<BenchmarkDetection>> detect(BenchmarkFrame frame) async {
    final inputTensor = _interpreter.getInputTensor(0);
    final shape = inputTensor.shape;
    if (shape.length != 4 || shape[0] != 1 || shape[3] != 3) {
      throw StateError('Tensor de entrada não suportado: $shape');
    }
    if (frame.width != shape[2] || frame.height != shape[1]) {
      throw StateError('Frame ${frame.width}x${frame.height}; modelo espera ${shape[2]}x${shape[1]}.');
    }
    final input = _input(frame.rgb, shape[1], shape[2], inputTensor.type);
    final outputs = <int, Object>{};
    for (var i = 0; i < _interpreter.getOutputTensors().length; i++) {
      final tensor = _interpreter.getOutputTensor(i);
      outputs[i] = _zeros(tensor.shape);
    }
    await _isolate.runForMultipleInputs([input], outputs);
    final decoded = candidate == BenchmarkCandidate.efficientDetLite0
        ? _decodeEfficient(outputs)
        : _decodeYolo(outputs);
    return decoded.map(frame.unletterbox).toList(growable: false);
  }

  Object _input(List<int> rgb, int height, int width, TensorType type) {
    var offset = 0;
    return [List.generate(height, (_) => List.generate(width, (_) {
      final pixel = rgb.sublist(offset, offset + 3);
      offset += 3;
      return type == TensorType.float32
          ? pixel.map((value) => value / 255.0).toList(growable: false)
          : Uint8List.fromList(pixel);
    }, growable: false), growable: false)];
  }

  Object _zeros(List<int> shape, [int depth = 0]) {
    if (depth == shape.length - 1) return Float32List(shape[depth]);
    return List.generate(shape[depth], (_) => _zeros(shape, depth + 1), growable: false);
  }

  List<BenchmarkDetection> _decodeEfficient(Map<int, Object> outputs) {
    List<List<double>>? boxes;
    final vectors = <List<double>>[];
    var count = 0;
    for (final value in outputs.values) {
      final unbatched = (value as List).first;
      if (unbatched is List && unbatched.isNotEmpty && unbatched.first is List) {
        final matrix = unbatched.cast<List>().map((row) => row.cast<num>().map((n) => n.toDouble()).toList()).toList();
        if (matrix.first.length == 4) boxes = matrix;
      } else if (unbatched is List) {
        final vector = unbatched.cast<num>().map((n) => n.toDouble()).toList();
        if (vector.length == 1) count = vector.first.round(); else vectors.add(vector);
      }
    }
    if (boxes == null || vectors.length < 2) return const [];
    vectors.sort((a, b) => b.fold<double>(0, (p, e) => p + e).compareTo(a.fold<double>(0, (p, e) => p + e)));
    final scores = vectors.first;
    final classes = vectors.last;
    return decodeEfficientDet(boxes: boxes, classes: classes, scores: scores, count: count, labels: cocoLabels);
  }

  List<BenchmarkDetection> _decodeYolo(Map<int, Object> outputs) {
    final batch = outputs.values.first as List;
    final matrix = (batch.first as List).cast<List>()
        .map((row) => row.cast<num>().map((n) => n.toDouble()).toList()).toList();
    return decodeYoloV8(matrix, labels: cocoLabels);
  }

  @override
  Future<void> close() async {
    await _isolate.close();
    _interpreter.close();
  }
}
