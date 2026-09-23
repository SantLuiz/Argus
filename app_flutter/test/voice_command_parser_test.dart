import 'package:argus_mobile/models/voice_command.dart';
import 'package:argus_mobile/services/voice_command_parser.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const parser = VoiceCommandParser();

  test('accepts closed commands with Argus prefix', () {
    expect(parser.parse('Argus - Aumentar Volume')?.action,
        VoiceAction.increaseVolume);
    expect(parser.parse('argus tirar foto')?.action, VoiceAction.analyzeNow);
    expect(parser.parse('ARGUS, ativar modo porta')?.action,
        VoiceAction.enableDoorMode);
    expect(parser.parse('Argus repetir descrição')?.action,
        VoiceAction.repeatDescription);
    expect(parser.parse('Argus silenciar')?.action, VoiceAction.muteAudio);
    expect(parser.parse('Argus ativar áudio')?.action, VoiceAction.unmuteAudio);
  });

  test('rejects free text and commands without prefix', () {
    expect(parser.parse('aumentar volume'), isNull);
    expect(parser.parse('Argus aumente um pouco o volume'), isNull);
    expect(parser.parse('Argus nao tirar foto'), isNull);
  });

  test('accepts direct commands when wake word is not required', () {
    expect(parser.parse('capturar imagem', requireWakeWord: false)?.action,
        VoiceAction.analyzeNow);
    expect(parser.parse('aumentar volume', requireWakeWord: false)?.action,
        VoiceAction.increaseVolume);
    expect(parser.parse('Argus ajuda', requireWakeWord: false)?.action,
        VoiceAction.help);
  });

  test('extracts command text only after wake word', () {
    expect(parser.commandAfterWakeWord('Argus capturar imagem'),
        'capturar imagem');
    expect(parser.commandAfterWakeWord('argus'), '');
    expect(parser.commandAfterWakeWord('largus capturar imagem'), isNull);
  });
}
