# Pendências e limites conhecidos

Atualizado em 23/09/2026. Este registro distingue implementação de validação experimental.

## V01 — Reconhecimento de comandos no Redmi (adiado)

**Estado:** continua falhando segundo o responsável, mesmo após o último APK. A investigação foi adiada explicitamente para priorizar organização e documentação.

Ambiente observado: Redmi Note 10, Android 12, MIUI 14 em inglês; app solicita STT em `pt-BR`. O microfone abre, há falha do pacote offline no reconhecedor e foi observado resultado nativo com fala. Isso não identifica sozinho a causa do comando não executado.

Já existem logs `[ARGUS_VOICE]`, ajustes de finalização e serialização das operações, processamento do retorno manual e aceitação de `Argus` opcional no modo manual. Essas alterações **não resolveram o problema confirmado pelo usuário**. Os testes com fakes não validam a comunicação real do plugin com Android.

Ao retomar:

1. Identificar APK instalado e versão do serviço de reconhecimento; registrar se o app está visível e a tela desbloqueada.
2. Reproduzir separadamente `ajuda` segurando/soltando e `Argus ajuda` sem tocar; anotar horário e modo.
3. Coletar `adb logcat -d -v time -s flutter RecognitionClient RecognitionServiceImpl SodaSpeechRecognizer NetworkSpeechRecognizer AndroidRuntime`.
4. Correlacionar texto recebido, sessão, resultado final, parse aceito/rejeitado e execução. Não assumir problema de permissão, idioma ou backend sem evidência.
5. Criar correção e teste de regressão a partir dessa evidência; validar novamente no dispositivo.

[Histórico do diagnóstico](history/12_DIAGNOSTICO_VOZ_REDMI_E_PLANO.md) preserva a coleta anterior; suas tarefas não devem ser executadas cegamente, pois parte delas já recebeu alterações.

## A01 — Validação completa de acessibilidade

Há controles semânticos, feedback tátil/sonoro e transcrição opcional. Falta percorrer câmera e configurações apenas com TalkBack/áudio, verificar foco, fonte ampliada e medir contraste sobre frames claros e escuros. Transparência sobre câmera não garante contraste constante. Não afirmar conformidade WCAG total antes dessa avaliação.

## E01 — Demonstração ponta a ponta

Registrar imagem usada, modelos, `depth_source`, latência, mensagem e áudio percebido. `/ready` retorna estado do processo e modelos lazy: `ready=true` não comprova carregamento bem-sucedido. Testes automatizados não substituem esse experimento.

## D01 — Contêiner e hospedagem

Arquivos Docker existem, mas build limpo em outra máquina e inferência real no contêiner exigem validação própria. Dependências PyTorch/Ultralytics podem exigir ajustes conforme arquitetura. Não considerar OCI provisionada nem prometer disponibilidade gratuita.

## M01 — Distribuição Android

O build release ainda usa chave debug. Assinatura de distribuição, identificador definitivo e validação de instalação/atualização são tarefas futuras, se necessárias. O responsável instala e testa o APK.

## T01 — Avisos de dependências

O build atual passa, mas Flutter avisa que `flutter_tts` e `speech_to_text` ainda aplicam Kotlin Gradle Plugin e podem precisar de atualização para versões futuras do Flutter. A suíte Python também emite aviso de depreciação de `torch.jit.load`. Registrar e tratar numa atualização de dependências separada; não alterar o toolchain durante a organização sem necessidade.
