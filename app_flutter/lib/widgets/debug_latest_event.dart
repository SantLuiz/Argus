import 'package:flutter/material.dart';

import '../models/debug_event.dart';

class DebugLatestEvent extends StatelessWidget {
  const DebugLatestEvent({super.key, required this.event});

  final DebugEvent event;

  @override
  Widget build(BuildContext context) {
    final time = event.timestamp.toLocal();
    final clock = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}:${time.second.toString().padLeft(2, '0')}';
    final text = '$clock · ${event.category} · ${event.message}';
    return Semantics(
      label: text,
      excludeSemantics: true,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: const Color(0xFF0D47A1),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(text, maxLines: 1, overflow: TextOverflow.ellipsis,
            style: const TextStyle(color: Colors.white)),
      ),
    );
  }
}
