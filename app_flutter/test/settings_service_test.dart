import 'package:argus_mobile/services/settings_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('novas preferências começam desligadas e persistem', () async {
    final service = SettingsService();
    await service.load();
    expect(service.settings.debugEnabled, isFalse);
    expect(service.settings.passiveListeningEnabled, isFalse);

    await service.setDebugEnabled(true);
    await service.setPassiveListeningEnabled(true);
    final reloaded = SettingsService();
    await reloaded.load();
    expect(reloaded.settings.debugEnabled, isTrue);
    expect(reloaded.settings.passiveListeningEnabled, isTrue);
  });

  test('fila preserva toggle quando formulário atualiza campos do backend', () async {
    final service = SettingsService();
    await service.load();
    final toggle = service.setDebugEnabled(true);
    final form = service.update((current) => current.copyWith(
      host: '10.0.0.2', ttsVolumePercent: 70));
    await Future.wait([toggle, form]);

    expect(service.settings.debugEnabled, isTrue);
    expect(service.settings.host, '10.0.0.2');
    expect(service.settings.ttsVolumePercent, 70);
  });
}
