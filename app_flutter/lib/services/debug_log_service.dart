import 'dart:collection';

import 'package:flutter/foundation.dart';

import '../models/debug_event.dart';

class DebugLogService extends ChangeNotifier {
  DebugLogService({bool enabled = false}) : _enabled = enabled {
    if (enabled) {
      record(category: 'debug', code: DebugEventCodes.debugEnabled, message: 'Debug ativado.');
    }
  }

  bool _enabled;
  int _nextSequence = 1;
  final List<DebugEvent> _events = [];

  bool get enabled => _enabled;
  UnmodifiableListView<DebugEvent> get events => UnmodifiableListView(_events);
  DebugEvent? get latest => _events.isEmpty ? null : _events.last;

  void setEnabled(bool value) {
    if (_enabled == value) return;
    _enabled = value;
    if (!value) {
      _events.clear();
      _nextSequence = 1;
      notifyListeners();
      return;
    }
    record(category: 'debug', code: DebugEventCodes.debugEnabled, message: 'Debug ativado.');
  }

  DebugEvent? record({
    required String category,
    required String code,
    required String message,
    DebugSeverity severity = DebugSeverity.info,
    String? operationId,
  }) {
    if (!_enabled) return null;
    final event = DebugEvent(
      sequence: _nextSequence++,
      timestamp: DateTime.now(),
      category: category,
      severity: severity,
      code: code,
      message: message,
      operationId: operationId,
    );
    _events.add(event);
    notifyListeners();
    return event;
  }
}
