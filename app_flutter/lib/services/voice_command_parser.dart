import '../models/voice_command.dart';

class VoiceCommandParser {
  const VoiceCommandParser();

  VoiceCommand? parse(String input, {bool requireWakeWord = true}) {
    final normalized = normalize(input);
    const prefix = 'argus ';
    if (requireWakeWord && !normalized.startsWith(prefix)) {
      return null;
    }
    final actionText = normalized.startsWith(prefix)
        ? normalized.substring(prefix.length).trim()
        : normalized;
    final action = _actions[actionText];
    return action == null ? null : VoiceCommand(action);
  }

  String? commandAfterWakeWord(String input) {
    final normalized = normalize(input);
    const wakeWord = 'argus';
    if (normalized == wakeWord) {
      return '';
    }
    const prefix = '$wakeWord ';
    if (!normalized.startsWith(prefix)) {
      return null;
    }
    return normalized.substring(prefix.length).trim();
  }

  static final Map<String, VoiceAction> _actions = {
    'analisar agora': VoiceAction.analyzeNow,
    'tirar foto': VoiceAction.analyzeNow,
    'capturar imagem': VoiceAction.analyzeNow,
    'repetir descricao': VoiceAction.repeatDescription,
    'parar audio': VoiceAction.stopAudio,
    'aumentar volume': VoiceAction.increaseVolume,
    'diminuir volume': VoiceAction.decreaseVolume,
    'abrir configuracoes': VoiceAction.openSettings,
    'voltar a camera': VoiceAction.backToCamera,
    'ativar modo porta': VoiceAction.enableDoorMode,
    'desativar modo porta': VoiceAction.disableDoorMode,
    'silenciar': VoiceAction.muteAudio,
    'ativar audio': VoiceAction.unmuteAudio,
    'ligar audio': VoiceAction.unmuteAudio,
    'ajuda': VoiceAction.help,
  };

  static String normalize(String value) {
    return value
        .toLowerCase()
        .replaceAll(RegExp(r'[àáâãä]'), 'a')
        .replaceAll(RegExp(r'[èéêë]'), 'e')
        .replaceAll(RegExp(r'[ìíîï]'), 'i')
        .replaceAll(RegExp(r'[òóôõö]'), 'o')
        .replaceAll(RegExp(r'[ùúûü]'), 'u')
        .replaceAll('ç', 'c')
        .replaceAll(RegExp(r'[^a-z0-9]+'), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }
}
