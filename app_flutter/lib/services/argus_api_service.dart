import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/app_config.dart';
import '../models/detection_response.dart';

class ArgusApiService {
  ArgusApiService({required AppConfig config, http.Client? client})
      : _config = config,
        _client = client ?? http.Client();

  AppConfig _config;
  final http.Client _client;

  set config(AppConfig value) => _config = value;

  Future<bool> ready() async {
    if (!_config.hasBackendUrl) {
      return false;
    }
    final response = await _client
        .get(_config.endpoint('/ready'))
        .timeout(Duration(seconds: _config.readyTimeoutSeconds));
    if (response.statusCode != 200) {
      return false;
    }
    final json = jsonDecode(response.body) as Map<String, dynamic>;
    return json['ready'] == true && json['busy'] != true;
  }

  Future<DetectionResponse> detect(File imageFile,
      {String mode = 'exploration', String? targetClass}) async {
    if (!_config.hasBackendUrl) {
      throw const ArgusApiException('CONFIG_MISSING',
          'Abra as configuracoes e informe o host do backend.');
    }

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

    final streamed = await _client
        .send(request)
        .timeout(Duration(seconds: _config.detectTimeoutSeconds));
    final body = await streamed.stream
        .bytesToString()
        .timeout(Duration(seconds: _config.detectTimeoutSeconds));
    if (streamed.statusCode < 200 || streamed.statusCode >= 300) {
      throw ArgusApiException.fromBody(body, streamed.statusCode);
    }
    return DetectionResponse.fromJson(jsonDecode(body) as Map<String, dynamic>);
  }
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
