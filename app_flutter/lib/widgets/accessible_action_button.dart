import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

class AccessibleActionButton extends StatelessWidget {
  const AccessibleActionButton({
    super.key,
    required this.label,
    required this.icon,
    required this.onPressed,
    this.tooltip,
    this.selected = false,
    this.size = 56,
    this.iconSize = 28,
    this.order,
    this.prominent = false,
  });

  final String label;
  final IconData icon;
  final VoidCallback? onPressed;
  final String? tooltip;
  final bool selected;
  final double size;
  final double iconSize;
  final double? order;
  final bool prominent;

  @override
  Widget build(BuildContext context) {
    final background = selected || prominent
        ? Colors.white.withValues(alpha: 0.92)
        : const Color(0xFF0D47A1).withValues(alpha: 0.76);
    final foreground =
        selected || prominent ? const Color(0xFF0D47A1) : Colors.white;
    final borderColor = Colors.white.withValues(alpha: 0.82);
    final button = Semantics(
      button: true,
      label: label,
      selected: selected,
      sortKey: order == null ? null : OrdinalSortKey(order!),
      child: IconButton.filledTonal(
        onPressed: onPressed,
        tooltip: tooltip ?? label,
        icon: Icon(icon, size: iconSize),
        constraints: BoxConstraints(minWidth: size, minHeight: size),
        style: IconButton.styleFrom(
          backgroundColor: background,
          foregroundColor: foreground,
          disabledBackgroundColor: const Color(0xFF0D47A1).withValues(
            alpha: 0.40,
          ),
          disabledForegroundColor: Colors.white70,
          side: BorderSide(color: borderColor, width: 1.4),
          shadowColor: Colors.black.withValues(alpha: 0.35),
          elevation: prominent ? 8 : 3,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
    final ordered = order == null
        ? button
        : FocusTraversalOrder(order: NumericFocusOrder(order!), child: button);
    return SizedBox.square(dimension: size, child: ordered);
  }
}
