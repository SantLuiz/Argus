import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/app_config.dart';
import '../models/detection_response.dart';
import '../models/debug_event.dart';
import 'debug_log_service.dart';

class ArgusApiService {
  ArgusApiService({required AppConfig config, required DebugLogService debugLog, http.Client? client})
      : _config = config,
        _debugLog = debugLog,
        _client = client ?? http.Client();

  AppConfig _config;
  final http.Client _client;
  final DebugLogService _debugLog;
  int _operationSequence = 0;

  set config(AppConfig value) => _config = value;

  Future<bool> ready() async {
    if (!_config.hasBackendUrl) {
      _debugLog.record(category: 'network', code: DebugEventCodes.configurationMissing, message: 'Backend não configurado.');
      return false;
    }
    final operationId = _newOperationId('ready');
    final stopwatch = Stopwatch()..start();
    _debugLog.record(category: 'network', code: DebugEventCodes.requestStarted, message: 'Consulta de disponibilidade iniciada.', operationId: operationId);
    try {
      final response = await _client.get(_config.endpoint('/ready')).timeout(Duration(seconds: _config.readyTimeoutSeconds));
      _debugLog.record(category: 'network', code: DebugEventCodes.responseReceived, message: 'Backend respondeu HTTP ${response.statusCode} em ${stopwatch.elapsedMilliseconds} ms.', operationId: operationId);
      if (response.statusCode != 200) return false;
      try {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return json['ready'] == true && json['busy'] != true;
      } catch (error) {
        _debugLog.record(category: 'network', code: DebugEventCodes.invalidResponse, message: 'Resposta de disponibilidade inválida: ${error.runtimeType}: $error', severity: DebugSeverity.error, operationId: operationId);
        return false;
      }
    } on TimeoutException catch (error) {
      _debugLog.record(category: 'network', code: DebugEventCodes.requestTimeout, message: 'Tempo limite ao consultar o backend: ${error.runtimeType}.', severity: DebugSeverity.warning, operationId: operationId);
      rethrow;
    } catch (error) {
      _debugLog.record(category: 'network', code: DebugEventCodes.connectionFailed, message: 'Falha na consulta ao backend: ${error.runtimeType}: $error', severity: DebugSeverity.error, operationId: operationId);
      rethrow;
    }
  }

  Future<DetectionResponse> detect(File imageFile,
      {String mode = 'exploration', String? targetClass}) async {
    if (!_config.hasBackendUrl) {
      _debugLog.record(category: 'network', code: DebugEventCodes.configurationMissing, message: 'Backend não configurado.', severity: DebugSeverity.warning);
      throw const ArgusApiException('CONFIG_MISSING',
          'Abra as configuracoes e informe o host do backend.');
    }

    final operationId = _newOperationId('detect');
    final stopwatch = Stopwatch()..start();
    _debugLog.record(category: 'network', code: DebugEventCodes.requestStarted, message: 'Análise remota iniciada.', operationId: operationId);
    final uri = _config.endpoint('/detect').replace(
      queryParameters: {
        'mode': mode,
        if (targetClass != null) 'target_class': targetClass,
      },
    );
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        contentType: MediaType('image', 'jpeg'),
      ));

    try {
      final streamed = await _client.send(request).timeout(Duration(seconds: _config.detectTimeoutSeconds));
      final body = await streamed.stream.bytesToString().timeout(Duration(seconds: _config.detectTimeoutSeconds));
      _debugLog.record(category: 'network', code: DebugEventCodes.responseReceived, message: 'Análise respondeu HTTP ${streamed.statusCode} em ${stopwatch.elapsedMilliseconds} ms.', operationId: operationId);
      if (streamed.statusCode < 200 || streamed.statusCode >= 300) {
        throw ArgusApiException.fromBody(body, streamed.statusCode);
      }
      try {
        return DetectionResponse.fromJson(jsonDecode(body) as Map<String, dynamic>);
      } catch (error) {
        _debugLog.record(category: 'network', code: DebugEventCodes.invalidResponse, message: 'Resposta de análise inválida: ${error.runtimeType}: $error', severity: DebugSeverity.error, operationId: operationId);
        throw const ArgusApiException('INVALID_RESPONSE', 'Resposta inválida do backend.');
      }
    } on TimeoutException catch (error) {
      _debugLog.record(category: 'network', code: DebugEventCodes.requestTimeout, message: 'Tempo limite na análise: ${error.runtimeType}.', severity: DebugSeverity.warning, operationId: operationId);
      rethrow;
    } on ArgusApiException {
      rethrow;
    } catch (error) {
      _debugLog.record(category: 'network', code: DebugEventCodes.connectionFailed, message: 'Falha de conexão na análise: ${error.runtimeType}: $error', severity: DebugSeverity.error, operationId: operationId);
      rethrow;
    }
  }

  String _newOperationId(String prefix) =>
      '$prefix-${DateTime.now().microsecondsSinceEpoch}-${++_operationSequence}';
}

class ArgusApiException implements Exception {
  const ArgusApiException(this.code, this.message, [this.statusCode]);

  factory ArgusApiException.fromBody(String body, int statusCode) {
    try {
      final json = jsonDecode(body) as Map<String, dynamic>;
      final detail = json['detail'];
      if (detail is Map<String, dynamic>) {
        return ArgusApiException(
          detail['code'] as String? ?? 'HTTP_$statusCode',
          detail['message'] as String? ?? 'Erro no backend.',
          statusCode,
        );
      }
    } catch (_) {
      return ArgusApiException(
          'HTTP_$statusCode', 'Erro ao comunicar com o backend.', statusCode);
    }
    return ArgusApiException(
        'HTTP_$statusCode', 'Erro ao comunicar com o backend.', statusCode);
  }

  final String code;
  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}
