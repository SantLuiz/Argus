import 'package:flutter/material.dart';

import '../services/argus_api_service.dart';
import '../services/debug_log_service.dart';
import '../services/feedback_service.dart';
import '../services/settings_service.dart';
import '../models/debug_event.dart';
import '../widgets/debug_history.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({
    super.key,
    required this.settingsService,
    required this.feedback,
    required this.debugLog,
  });

  final SettingsService settingsService;
  final FeedbackService feedback;
  final DebugLogService debugLog;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late String _scheme;
  late final TextEditingController _hostController;
  late final TextEditingController _portController;
  late final TextEditingController _readyTimeoutController;
  late final TextEditingController _detectTimeoutController;
  late bool _showTranscription;
  late bool _debugEnabled;
  late bool _passiveListeningEnabled;
  String _status = 'Informe o backend usado pelo prototipo ARGUS.';

  @override
  void initState() {
    super.initState();
    final settings = widget.settingsService.settings;
    _scheme = settings.scheme;
    _hostController = TextEditingController(text: settings.host);
    _portController =
        TextEditingController(text: settings.port?.toString() ?? '');
    _readyTimeoutController =
        TextEditingController(text: settings.readyTimeoutSeconds.toString());
    _detectTimeoutController =
        TextEditingController(text: settings.detectTimeoutSeconds.toString());
    _showTranscription = settings.showTranscription;
    _debugEnabled = settings.debugEnabled;
    _passiveListeningEnabled = settings.passiveListeningEnabled;
  }

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    _readyTimeoutController.dispose();
    _detectTimeoutController.dispose();
    super.dispose();
  }

  Future<bool> _save({bool announce = true}) async {
    final settings = _readSettings();
    if (settings == null) {
      return false;
    }
    await widget.settingsService.update((current) => current.copyWith(
          scheme: settings.scheme,
          host: settings.host,
          port: settings.port,
          clearPort: settings.port == null,
          readyTimeoutSeconds: settings.readyTimeoutSeconds,
          detectTimeoutSeconds: settings.detectTimeoutSeconds,
        ));
    if (!mounted) {
      return true;
    }
    setState(() => _status = 'Configuracoes salvas.');
    if (announce) {
      await widget.feedback.action('Configuracoes salvas.', interrupt: true);
    }
    return true;
  }

  Future<void> _testConnection() async {
    if (!await _save(announce: false)) return;
    if (!mounted) return;
    if (!widget.settingsService.settings.hasBackend) {
      const message = 'Informe o host do backend antes de testar a conexão.';
      setState(() => _status = message);
      await widget.feedback.action(message, interrupt: true);
      return;
    }
    final service =
        ArgusApiService(config: widget.settingsService.settings.config, debugLog: widget.debugLog);
    setState(() => _status = 'Testando conexao com o backend.');
    bool ready;
    try {
      ready = await service.ready();
    } catch (error) {
      widget.debugLog.record(category: 'settings', code: DebugEventCodes.connectionFailed, message: 'Teste de conexão falhou: ${error.runtimeType}: $error', severity: DebugSeverity.error);
      if (!mounted) return;
      const message = 'Nao foi possivel conectar ao backend.';
      setState(() => _status = message);
      await widget.feedback.action(message, interrupt: true);
      return;
    }
    if (!mounted) {
      return;
    }
    final message = ready
        ? 'O backend respondeu e esta disponivel para requisicoes.'
        : 'O backend respondeu, mas informou indisponibilidade.';
    setState(() => _status = message);
    await widget.feedback.action(message, interrupt: true);
  }

  ArgusSettings? _readSettings() {
    final host = _hostController.text.trim();
    final portText = _portController.text.trim();
    final readyText = _readyTimeoutController.text.trim();
    final detectText = _detectTimeoutController.text.trim();
    final port = portText.isEmpty ? null : int.tryParse(portText);
    final readyTimeout = int.tryParse(readyText);
    final detectTimeout = int.tryParse(detectText);

    if (host.contains('/') || host.contains('@') || host.contains(':')) {
      _setError(
          'Informe apenas o host ou IP, sem caminho, usuario ou protocolo.');
      return null;
    }
    if (portText.isNotEmpty && (port == null || port < 1 || port > 65535)) {
      _setError('A porta deve estar entre 1 e 65535.');
      return null;
    }
    if (readyTimeout == null || readyTimeout < 1 || readyTimeout > 120) {
      _setError('O timeout de status deve ficar entre 1 e 120 segundos.');
      return null;
    }
    if (detectTimeout == null || detectTimeout < 1 || detectTimeout > 120) {
      _setError('O timeout de deteccao deve ficar entre 1 e 120 segundos.');
      return null;
    }

    return widget.settingsService.settings.copyWith(
      scheme: _scheme, host: host, port: port, clearPort: port == null,
      readyTimeoutSeconds: readyTimeout, detectTimeoutSeconds: detectTimeout,
    );
  }

  Future<void> _setDebugEnabled(bool value) async {
    setState(() => _debugEnabled = value);
    await widget.settingsService.setDebugEnabled(value);
    widget.debugLog.setEnabled(value);
    if (!mounted) return;
    setState(() => _status = value ? 'Debug ativado.' : 'Debug desativado e histórico apagado.');
    await widget.feedback.action(_status, interrupt: true);
  }

  Future<void> _setPassiveListeningEnabled(bool value) async {
    setState(() => _passiveListeningEnabled = value);
    await widget.settingsService.setPassiveListeningEnabled(value);
    widget.debugLog.record(category: 'settings', code: DebugEventCodes.settingChanged,
        message: value ? 'Escuta passiva ativada.' : 'Escuta passiva desativada.');
    if (!mounted) return;
    setState(() => _status = value ? 'Escuta passiva ativada.' : 'Escuta passiva desativada.');
    await widget.feedback.action(_status, interrupt: true);
  }

  Future<void> _setShowTranscription(bool value) async {
    setState(() => _showTranscription = value);
    await widget.settingsService.setShowTranscription(value);
    if (!mounted) {
      return;
    }
    setState(() {
      _status = value
          ? 'Transcricao visivel na tela.'
          : 'Transcricao oculta na tela.';
    });
    await widget.feedback.action(_status, interrupt: true);
  }

  void _setError(String message) {
    setState(() => _status = message);
    widget.feedback.action(message, interrupt: true);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Configuracoes')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Semantics(
                liveRegion: true,
                child: Text(_status,
                    style: Theme.of(context).textTheme.titleMedium)),
            const SizedBox(height: 16),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'https', label: Text('HTTPS')),
                ButtonSegment(value: 'http', label: Text('HTTP local')),
              ],
              selected: {_scheme},
              onSelectionChanged: (value) =>
                  setState(() => _scheme = value.single),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _hostController,
              decoration: const InputDecoration(
                labelText: 'Host ou IP do backend',
                hintText: 'exemplo: servidor.tailnet.ts.net',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _portController,
              decoration: const InputDecoration(
                labelText: 'Porta opcional',
                hintText: 'vazio usa o padrao do protocolo',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _readyTimeoutController,
              decoration: const InputDecoration(
                labelText: 'Timeout de status em segundos',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _detectTimeoutController,
              decoration: const InputDecoration(
                labelText: 'Timeout de deteccao em segundos',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 12),
            SwitchListTile(
              value: _showTranscription,
              onChanged: _setShowTranscription,
              title: const Text('Mostrar transcricao na tela'),
              subtitle: const Text(
                'Quando desligado, os comandos continuam funcionando por audio.',
              ),
            ),
            SwitchListTile(
              value: _passiveListeningEnabled,
              onChanged: _setPassiveListeningEnabled,
              title: const Text('Ativar escuta passiva — Argus'),
              subtitle: const Text('O botão de falar continua disponível. A escuta passiva opera na tela da câmera.'),
            ),
            SwitchListTile(
              value: _debugEnabled,
              onChanged: _setDebugEnabled,
              title: const Text('Mostrar debug na tela'),
              subtitle: const Text('Ao desligar, o histórico desta sessão será apagado.'),
            ),
            if (_debugEnabled) ...[
              const SizedBox(height: 8),
              Text('Histórico de debug', style: Theme.of(context).textTheme.titleMedium),
              AnimatedBuilder(
                animation: widget.debugLog,
                builder: (context, _) => DebugHistory(events: widget.debugLog.events),
              ),
            ],
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () async => _save(),
              icon: const Icon(Icons.save),
              label: const Text('Salvar configuracoes'),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: _testConnection,
              icon: const Icon(Icons.wifi_tethering),
              label: const Text('Testar conexao'),
            ),
          ],
        ),
      ),
    );
  }
}
