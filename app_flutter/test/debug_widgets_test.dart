import 'package:argus_mobile/models/debug_event.dart';
import 'package:argus_mobile/widgets/debug_history.dart';
import 'package:argus_mobile/widgets/debug_latest_event.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  DebugEvent event(int sequence, String message) => DebugEvent(
    sequence: sequence, timestamp: DateTime(2026, 1, 1, 12, 30),
    category: 'camera', severity: DebugSeverity.info,
    code: 'camera.ready', message: message);

  testWidgets('linha mostra somente evento fornecido sem overflow em fonte ampliada', (tester) async {
    await tester.pumpWidget(MaterialApp(home: MediaQuery(
      data: const MediaQueryData(textScaler: TextScaler.linear(2)),
      child: Scaffold(body: DebugLatestEvent(event: event(2, 'Mensagem completa para diagnóstico da câmera'))),
    )));
    expect(find.textContaining('Mensagem completa'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('histórico preserva ordem cronológica', (tester) async {
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: DebugHistory(
      events: [event(1, 'Primeiro'), event(2, 'Segundo')],
    ))));
    expect(find.text('Primeiro'), findsOneWidget);
    expect(find.text('Segundo'), findsOneWidget);
  });
}
