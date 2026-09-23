import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../controllers/analysis_controller.dart';
import '../controllers/voice_input_controller.dart';
import '../models/voice_command.dart';
import '../models/voice_state.dart';
import '../services/argus_api_service.dart';
import '../services/feedback_service.dart';
import '../services/media_volume_service.dart';
import '../services/settings_service.dart';
import '../services/speech_recognition_service.dart';
import '../services/system_ui_service.dart';
import '../services/tts_service.dart';
import '../widgets/accessible_action_button.dart';
import '../widgets/push_to_talk_button.dart';
import '../widgets/system_status.dart';
import '../widgets/transcription_panel.dart';
import 'settings_screen.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({
    super.key,
    required this.settingsService,
    required this.tts,
    required this.feedback,
  });

  final SettingsService settingsService;
  final TtsService tts;
  final FeedbackService feedback;

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen>
    with WidgetsBindingObserver {
  CameraController? _camera;
  late final ArgusApiService _api;
  late final AnalysisController _analysis;
  late final VoiceInputController _voice;
  final MediaVolumeService _mediaVolume = const MediaVolumeService();
  String? _cameraError;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _api = ArgusApiService(config: widget.settingsService.settings.config);
    _analysis = AnalysisController(api: _api, tts: widget.tts);
    _voice = VoiceInputController(
      speech: SpeechRecognitionService(),
      feedback: widget.feedback,
      onCommand: _executeVoiceAction,
    );
    _voice.updateTranscriptionPreference(
        widget.settingsService.settings.showTranscription);
    widget.settingsService.addListener(_onSettingsChanged);
    SystemUiService.enterCameraMode();
    _startCamera();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _voice.startPassive();
    });
  }

  void _onSettingsChanged() {
    _api.config = widget.settingsService.settings.config;
    _voice.updateTranscriptionPreference(
        widget.settingsService.settings.showTranscription);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final camera = _camera;
    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused) {
      _voice.suspendPassive(message: 'Escuta pausada.');
      camera?.dispose();
      _camera = null;
    } else if (state == AppLifecycleState.resumed) {
      _startCamera();
      SystemUiService.enterCameraMode();
      _voice.startPassive();
    }
  }

  Future<void> _startCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        throw CameraException('NO_CAMERA', 'Nenhuma camera encontrada.');
      }
      final rearCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );
      final controller = CameraController(
        rearCamera,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        _camera = controller;
        _cameraError = null;
      });
      await widget.feedback.action('Camera pronta.');
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() => _cameraError = 'Nao foi possivel iniciar a camera.');
      await widget.feedback
          .action('Nao foi possivel iniciar a camera.', interrupt: true);
    }
  }

  @override
  void dispose() {
    widget.settingsService.removeListener(_onSettingsChanged);
    WidgetsBinding.instance.removeObserver(this);
    SystemUiService.exitCameraMode();
    _analysis.stopAudio();
    _analysis.dispose();
    _voice.dispose();
    _camera?.dispose();
    super.dispose();
  }

  Future<void> _openSettings() async {
    await _voice.suspendPassive(message: 'Configuracoes abertas.');
    await SystemUiService.exitCameraMode();
    if (!mounted) {
      return;
    }
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => SettingsScreen(
          settingsService: widget.settingsService,
          feedback: widget.feedback,
        ),
      ),
    );
    if (mounted) {
      await SystemUiService.enterCameraMode();
      await widget.feedback.action('Voltou para a camera.');
      await _voice.startPassive();
    }
  }

  Future<void> _executeVoiceAction(VoiceAction action) async {
    switch (action) {
      case VoiceAction.analyzeNow:
        final camera = _camera;
        if (camera == null) {
          await widget.feedback
              .action('Camera ainda nao esta pronta.', interrupt: true);
          return;
        }
        await _analysis.analyze(camera);
      case VoiceAction.repeatDescription:
        await _analysis.repeatDescription();
      case VoiceAction.stopAudio:
        await _analysis.stopAudio();
        await widget.feedback.action('Audio interrompido.', interrupt: true);
      case VoiceAction.increaseVolume:
        await _changeMediaVolume(1);
      case VoiceAction.decreaseVolume:
        await _changeMediaVolume(-1);
      case VoiceAction.openSettings:
        await widget.feedback.action('Abrindo configuracoes.', interrupt: true);
        await _openSettings();
      case VoiceAction.backToCamera:
        await widget.feedback
            .action('Voce ja esta na camera.', interrupt: true);
      case VoiceAction.enableDoorMode:
        _analysis.setNavigationMode(true);
        await widget.feedback.action('Modo porta ativado.', interrupt: true);
      case VoiceAction.disableDoorMode:
        _analysis.setNavigationMode(false);
        await widget.feedback.action('Modo porta desativado.', interrupt: true);
      case VoiceAction.muteAudio:
        await _setMuted(true);
      case VoiceAction.unmuteAudio:
        await _setMuted(false);
      case VoiceAction.help:
        await widget.feedback.action(
          'Comandos disponiveis: Argus analisar agora, repetir descricao, parar audio, silenciar, ativar audio, aumentar volume, diminuir volume, abrir configuracoes, ativar modo porta e desativar modo porta.',
          interrupt: true,
        );
    }
  }

  Future<void> _changeMediaVolume(int steps) async {
    await widget.feedback.hapticOnly();
    final percent = await _mediaVolume.changeBySteps(steps);
    final message = percent == null
        ? 'Use os botoes de volume do celular para ajustar o audio.'
        : 'Volume de midia ajustado para $percent por cento.';
    await widget.feedback.action(message, interrupt: true);
  }

  Future<void> _setMuted(bool value) async {
    if (value) {
      await widget.feedback.hapticOnly();
      await widget.tts.setMuted(true);
      if (mounted) {
        setState(() {});
      }
      return;
    }
    await widget.tts.setMuted(false);
    if (mounted) {
      setState(() {});
    }
    await widget.feedback.action('Audio ativado.', interrupt: true);
  }

  Future<void> _toggleMute() async {
    if (widget.tts.muted) {
      await _setMuted(false);
      return;
    }
    await _setMuted(true);
  }

  Future<void> _analyzeNow() async {
    await widget.feedback.hapticOnly();
    final camera = _camera;
    if (camera == null) {
      await widget.feedback
          .action('Camera ainda nao esta pronta.', interrupt: true);
      return;
    }
    await _analysis.analyze(camera);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: AnimatedBuilder(
        animation:
            Listenable.merge([_analysis, _voice, widget.settingsService]),
        builder: (context, _) {
          final camera = _camera;
          final status = widget.tts.hasBrazilianVoice
              ? _analysis.status
              : 'Voz brasileira nao encontrada. Configure uma voz pt-BR no Android.';
          return Stack(
            fit: StackFit.expand,
            children: [
              _CameraBackground(camera: camera, error: _cameraError),
              _ControlsOverlay(
                status: status,
                running: _analysis.running,
                voiceState: _voice.state,
                muted: widget.tts.muted,
                navigationMode: _analysis.navigationMode,
                hasCamera: camera != null && camera.value.isInitialized,
                onAnalyze: _analyzeNow,
                onPushToTalkStart: _voice.beginPushToTalk,
                onPushToTalkEnd: _voice.finishPushToTalk,
                onPushToTalkToggle: _voice.toggleAccessiblePushToTalk,
                onRepeat: _analysis.repeatDescription,
                onMute: _toggleMute,
                onToggleDoorMode: () async {
                  final enabled = !_analysis.navigationMode;
                  _analysis.setNavigationMode(enabled);
                  await widget.feedback.action(enabled
                      ? 'Modo porta ativado.'
                      : 'Modo porta desativado.');
                },
                onSettings: _openSettings,
                onHelp: () => _executeVoiceAction(VoiceAction.help),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _CameraBackground extends StatelessWidget {
  const _CameraBackground({required this.camera, required this.error});

  final CameraController? camera;
  final String? error;

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(error!, textAlign: TextAlign.center),
        ),
      );
    }
    if (camera == null || !camera!.value.isInitialized) {
      return const Center(child: CircularProgressIndicator());
    }
    final previewSize = camera!.value.previewSize;
    if (previewSize == null) {
      return const ColoredBox(color: Colors.black);
    }
    return ExcludeSemantics(
      child: ColoredBox(
        color: Colors.black,
        child: FittedBox(
          fit: BoxFit.cover,
          child: SizedBox(
            width: previewSize.height,
            height: previewSize.width,
            child: CameraPreview(camera!),
          ),
        ),
      ),
    );
  }
}

class _ControlsOverlay extends StatelessWidget {
  const _ControlsOverlay({
    required this.status,
    required this.running,
    required this.voiceState,
    required this.muted,
    required this.navigationMode,
    required this.hasCamera,
    required this.onAnalyze,
    required this.onPushToTalkStart,
    required this.onPushToTalkEnd,
    required this.onPushToTalkToggle,
    required this.onRepeat,
    required this.onMute,
    required this.onToggleDoorMode,
    required this.onSettings,
    required this.onHelp,
  });

  final String status;
  final bool running;
  final VoiceState voiceState;
  final bool muted;
  final bool navigationMode;
  final bool hasCamera;
  final VoidCallback? onAnalyze;
  final VoidCallback onPushToTalkStart;
  final VoidCallback onPushToTalkEnd;
  final VoidCallback onPushToTalkToggle;
  final VoidCallback? onRepeat;
  final VoidCallback? onMute;
  final VoidCallback? onToggleDoorMode;
  final VoidCallback? onSettings;
  final VoidCallback? onHelp;

  @override
  Widget build(BuildContext context) {
    return FocusTraversalGroup(
      policy: OrderedTraversalPolicy(),
      child: Stack(
        fit: StackFit.expand,
        children: [
          Positioned(
            top: 0,
            left: 0,
            child: SafeArea(
              minimum: const EdgeInsets.only(top: 16, left: 16),
              child: Row(
                children: [
                  AccessibleActionButton(
                    label: muted ? 'Ativar audio' : 'Silenciar audio',
                    icon: muted ? Icons.volume_off : Icons.volume_up,
                    selected: muted,
                    order: 1,
                    onPressed: onMute,
                  ),
                  const SizedBox(width: 16),
                  AccessibleActionButton(
                    label: 'Ajuda de comandos',
                    icon: Icons.help_outline,
                    order: 2,
                    onPressed: onHelp,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            top: 0,
            right: 0,
            child: SafeArea(
              minimum: const EdgeInsets.only(top: 16, right: 16),
              child: AccessibleActionButton(
                label: 'Abrir configuracoes',
                icon: Icons.settings,
                order: 3,
                onPressed: onSettings,
              ),
            ),
          ),
          Positioned(
            top: 0,
            left: 16,
            right: 16,
            child: SafeArea(
              minimum: const EdgeInsets.only(top: 88),
              child: Center(
                child: voiceState.showTranscription
                    ? TranscriptionPanel(text: voiceState.transcription)
                    : const SizedBox.shrink(),
              ),
            ),
          ),
          Positioned(
            left: 16,
            right: 16,
            bottom: 0,
            child: SafeArea(
              minimum: const EdgeInsets.only(bottom: 18),
              top: false,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  _StatusPill(text: status),
                  const SizedBox(height: 14),
                  Wrap(
                    alignment: WrapAlignment.center,
                    spacing: 18,
                    runSpacing: 14,
                    children: [
                      AccessibleActionButton(
                        label: navigationMode
                            ? 'Desativar modo porta'
                            : 'Ativar modo porta',
                        icon: Icons.door_front_door,
                        selected: navigationMode,
                        order: 4,
                        onPressed: running ? null : onToggleDoorMode,
                      ),
                      AccessibleActionButton(
                        label: running
                            ? 'Analise em andamento'
                            : 'Capturar imagem',
                        icon: Icons.camera_alt,
                        size: 80,
                        iconSize: 38,
                        order: 5,
                        prominent: true,
                        onPressed: !hasCamera || running ? null : onAnalyze,
                      ),
                      AccessibleActionButton(
                        label: 'Repetir descricao',
                        icon: Icons.replay,
                        order: 6,
                        onPressed: onRepeat,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            right: 0,
            bottom: 0,
            child: SafeArea(
              minimum: const EdgeInsets.only(right: 16, bottom: 116),
              top: false,
              child: PushToTalkButton(
                active: voiceState.pushToTalkActive,
                order: 7,
                onPressStart: onPushToTalkStart,
                onPressEnd: onPushToTalkEnd,
                onSemanticToggle: onPushToTalkToggle,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      liveRegion: true,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: const Color(0xFF0D47A1).withValues(alpha: 0.72),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white.withValues(alpha: 0.80)),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          child: SystemStatus(text: text),
        ),
      ),
    );
  }
}
