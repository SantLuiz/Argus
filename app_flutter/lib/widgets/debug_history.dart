import 'package:flutter/material.dart';

import '../models/debug_event.dart';

class DebugHistory extends StatelessWidget {
  const DebugHistory({super.key, required this.events});

  final List<DebugEvent> events;

  @override
  Widget build(BuildContext context) {
    if (events.isEmpty) return const Text('Nenhum evento de debug nesta sessão.');
    return SizedBox(
      height: 280,
      child: ListView.builder(
        key: const Key('debug-history-list'),
        itemCount: events.length,
        itemBuilder: (context, index) {
          final event = events[index];
          final time = event.timestamp.toLocal();
          final clock = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}:${time.second.toString().padLeft(2, '0')}';
          final operation = event.operationId == null
              ? ''
              : ' · operação ${event.operationId}';
          return ListTile(
            dense: true,
            title: Text('${event.sequence}. $clock · ${event.severity.name} · ${event.category} · ${event.code}$operation'),
            subtitle: Text(event.message),
          );
        },
      ),
    );
  }
}
