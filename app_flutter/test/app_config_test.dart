import 'package:argus_mobile/config/app_config.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('empty config has no backend URL', () {
    const config = AppConfig.empty();

    expect(config.hasBackendUrl, isFalse);
    expect(() => config.endpoint('/ready'), throwsStateError);
  });

  test('builds endpoint from runtime settings', () {
    const config =
        AppConfig(scheme: 'https', host: 'argus.example.test', port: 9443);

    expect(config.hasBackendUrl, isTrue);
    expect(config.endpoint('/detect').toString(),
        'https://argus.example.test:9443/detect');
  });
}
