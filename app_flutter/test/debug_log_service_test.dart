import 'package:argus_mobile/models/debug_event.dart';
import 'package:argus_mobile/services/debug_log_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('coleta somente ligado, mantém ordem e limpa ao desligar', () {
    final log = DebugLogService();
    expect(log.record(category: 'test', code: 'ignored', message: 'x'), isNull);
    expect(log.events, isEmpty);

    log.setEnabled(true);
    log.record(category: 'test', code: 'second', message: 'Segundo');

    expect(log.events.map((event) => event.sequence), [1, 2]);
    expect(log.latest?.code, 'second');
    expect(() => log.events.add(DebugEvent(
      sequence: 3, timestamp: DateTime.now(), category: 'test',
      severity: DebugSeverity.info, code: 'x', message: 'x')),
      throwsUnsupportedError);

    log.setEnabled(false);
    expect(log.events, isEmpty);
    expect(log.latest, isNull);
  });
}
