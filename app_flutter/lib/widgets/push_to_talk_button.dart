import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

class PushToTalkButton extends StatelessWidget {
  const PushToTalkButton({
    super.key,
    required this.active,
    required this.onPressStart,
    required this.onPressEnd,
    required this.onSemanticToggle,
    this.order,
  });

  final bool active;
  final VoidCallback onPressStart;
  final VoidCallback onPressEnd;
  final VoidCallback onSemanticToggle;
  final double? order;

  @override
  Widget build(BuildContext context) {
    final background = active
        ? const Color(0xFF0D47A1).withValues(alpha: 0.92)
        : Colors.white.withValues(alpha: 0.94);
    final foreground = active ? Colors.white : const Color(0xFF0D47A1);
    final label =
        active ? 'Soltar para enviar comando' : 'Manter pressionado para falar';
    final button = Semantics(
      button: true,
      toggled: active,
      label: label,
      hint: 'Comando direto, sem dizer Argus',
      sortKey: order == null ? null : OrdinalSortKey(order!),
      onTap: onSemanticToggle,
      child: GestureDetector(
        excludeFromSemantics: true,
        onTapDown: (_) => onPressStart(),
        onTapUp: (_) => onPressEnd(),
        onTapCancel: onPressEnd,
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: background,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.90),
              width: 1.6,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.35),
                blurRadius: active ? 14 : 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: SizedBox.square(
            dimension: 84,
            child: Icon(Icons.mic, color: foreground, size: 40),
          ),
        ),
      ),
    );
    final ordered = order == null
        ? button
        : FocusTraversalOrder(order: NumericFocusOrder(order!), child: button);
    return ordered;
  }
}
