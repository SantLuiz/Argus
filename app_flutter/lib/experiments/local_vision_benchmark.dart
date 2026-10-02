import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import 'benchmark_detector.dart';
import 'benchmark_image_converter.dart';
import 'benchmark_overlay.dart';
import 'tflite_benchmark_detector.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LocalVisionBenchmarkApp());
}

class LocalVisionBenchmarkApp extends StatelessWidget {
  const LocalVisionBenchmarkApp({super.key});
  @override
  Widget build(BuildContext context) => const MaterialApp(
        debugShowCheckedModeBanner: false,
        home: LocalVisionBenchmarkScreen(),
      );
}

class LocalVisionBenchmarkScreen extends StatefulWidget {
  const LocalVisionBenchmarkScreen({super.key});
  @override
  State<LocalVisionBenchmarkScreen> createState() => _LocalVisionBenchmarkScreenState();
}

class _LocalVisionBenchmarkScreenState extends State<LocalVisionBenchmarkScreen>
    with WidgetsBindingObserver {
  final Stopwatch _clock = Stopwatch()..start();
  CameraController? _camera;
  BenchmarkDetector? _detector;
  BenchmarkFrameScheduler? _scheduler;
  BenchmarkCandidate _candidate = BenchmarkCandidate.previewOnly;
  BenchmarkSnapshot? _snapshot;
  bool _debug = false;
  bool _screenActive = true;
  int _frameId = 0;
  String _status = 'Inicializando câmera';
  Timer? _refresh;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _openCamera();
    _refresh = Timer.periodic(const Duration(milliseconds: 200), (_) {
      if (mounted) setState(() => _snapshot = _scheduler?.latest);
    });
  }

  Future<void> _openCamera() async {
    try {
      final cameras = await availableCameras();
      final controller = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );
      await controller.initialize();
      _camera = controller;
      await controller.startImageStream(_onFrame);
      if (mounted) setState(() => _status = 'Preview ativo');
    } catch (error) {
      _scheduler?.invalidate();
      if (mounted) setState(() => _status = 'Câmera indisponível: $error');
    }
  }

  Future<void> _onFrame(CameraImage image) async {
    final scheduler = _scheduler;
    final camera = _camera;
    if (!_screenActive || scheduler == null || camera == null) return;
    final captured = _clock.elapsedMicroseconds;
    // A conversão respeita bytesPerRow/bytesPerPixel, orienta e aplica letterbox.
    final frame = convertCameraFrame(
      cameraImage: image,
      frameId: ++_frameId,
      capturedAtMicros: captured,
      rotationDegrees: camera.description.sensorOrientation,
      targetWidth: 320,
      targetHeight: 320,
    );
    try {
      await scheduler.offer(frame);
    } catch (error) {
      scheduler.invalidate();
      if (mounted) setState(() => _status = 'Inferência falhou: $error');
    }
  }

  Future<void> _select(BenchmarkCandidate candidate) async {
    final oldDetector = _detector;
    _detector = null;
    _scheduler = null;
    _snapshot = null;
    await oldDetector?.close();
    setState(() {
      _candidate = candidate;
      _status = candidate == BenchmarkCandidate.previewOnly ? 'Preview sem inferência' : 'Carregando modelo';
    });
    if (candidate == BenchmarkCandidate.previewOnly) return;
    try {
      final detector = await TfliteBenchmarkDetector.load(candidate);
      _detector = detector;
      _scheduler = BenchmarkFrameScheduler(detector: detector, nowMicros: () => _clock.elapsedMicroseconds);
      if (mounted) setState(() => _status = 'Inferência CPU, 2 threads, máximo 5 Hz');
    } catch (error) {
      if (mounted) setState(() => _status = 'Reconhecimento local indisponível: $error');
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _screenActive = state == AppLifecycleState.resumed;
    if (!_screenActive) {
      _scheduler?.invalidate();
      _snapshot = null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final camera = _camera;
    final metrics = _scheduler?.metrics;
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (camera?.value.isInitialized == true)
              FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: camera!.value.previewSize!.height,
                  height: camera.value.previewSize!.width,
                  child: CameraPreview(camera),
                ),
              ),
            if (_debug && _snapshot != null) BenchmarkOverlay(snapshot: _snapshot!),
            Align(
              alignment: Alignment.topCenter,
              child: ColoredBox(
                color: const Color(0xdd002b5c),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    DropdownButton<BenchmarkCandidate>(
                      value: _candidate,
                      dropdownColor: const Color(0xff002b5c),
                      style: const TextStyle(color: Colors.white),
                      items: const [
                        DropdownMenuItem(value: BenchmarkCandidate.previewOnly, child: Text('Preview')),
                        DropdownMenuItem(value: BenchmarkCandidate.efficientDetLite0, child: Text('EfficientDet-Lite0')),
                        DropdownMenuItem(value: BenchmarkCandidate.yoloV8n, child: Text('YOLOv8n TFLite')),
                      ],
                      onChanged: (value) { if (value != null) _select(value); },
                    ),
                    SwitchListTile(
                      value: _debug,
                      onChanged: (value) => setState(() => _debug = value),
                      title: const Text('Debug e caixas', style: TextStyle(color: Colors.white)),
                    ),
                    Text(_status, style: const TextStyle(color: Colors.white)),
                    if (_debug && metrics != null)
                      Text(
                        'p50 ${metrics.percentile(.5)?.toStringAsFixed(1) ?? 'não medido'} ms · '
                        'p95 ${metrics.percentile(.95)?.toStringAsFixed(1) ?? 'não medido'} ms · '
                        '${metrics.completedFrames} concluídos · ${metrics.droppedFrames} descartados\n'
                        'Memória, bateria, temperatura e tempo de UI: não medidos neste executor',
                        style: const TextStyle(color: Colors.white),
                      ),
                  ]),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _screenActive = false;
    _refresh?.cancel();
    _scheduler?.invalidate();
    final camera = _camera;
    if (camera?.value.isStreamingImages == true) camera!.stopImageStream();
    camera?.dispose();
    _detector?.close();
    super.dispose();
  }
}
