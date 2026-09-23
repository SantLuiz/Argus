# Aplicativo ARGUS

Frontend Flutter do protótipo de IC. Plataforma nativa incluída: Android. O projeto usa câmera, HTTP, SharedPreferences, `flutter_tts` e `speech_to_text`.

```sh
flutter pub get
flutter analyze
flutter test
flutter run
```

Execute os comandos nesta pasta. Os arquivos Android já estão versionados; não recrie o projeto com `flutter create`.

Na primeira execução, abra Configurações e informe protocolo, host e porta do backend. Preferências são persistidas no aparelho; nenhum endereço é necessário no build.

- [Ambiente e geração do APK](../docs/DEVELOPMENT.md).
- [Arquivos, responsabilidades e fluxos](../docs/CODEBASE.md).
- [Voz e acessibilidade](../docs/11_VOZ_ACESSIBILIDADE_MOBILE.md).
- [Pendências](../docs/PENDENCIAS.md).

O reconhecimento de voz continua com falha reportada no Redmi Note 10. Testes automatizados não comprovam STT ou TalkBack no aparelho. A instalação e o teste do APK ficam com o responsável.
