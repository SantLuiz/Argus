class AppConfig {
  const AppConfig({
    required this.scheme,
    required this.host,
    this.port,
    this.readyTimeoutSeconds = 5,
    this.detectTimeoutSeconds = 30,
  });

  const AppConfig.empty()
      : scheme = 'https',
        host = '',
        port = null,
        readyTimeoutSeconds = 5,
        detectTimeoutSeconds = 30;

  final String scheme;
  final String host;
  final int? port;
  final int readyTimeoutSeconds;
  final int detectTimeoutSeconds;

  bool get hasBackendUrl => host.trim().isNotEmpty;

  Uri endpoint(String path) {
    if (!hasBackendUrl) {
      throw StateError('Backend nao configurado.');
    }
    return Uri(
      scheme: scheme,
      host: host.trim(),
      port: port,
      path: path.startsWith('/') ? path : '/$path',
    );
  }
}
