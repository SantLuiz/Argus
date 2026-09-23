# ARGUS: diagnóstico no Redmi e plano de execução

Data: 23/09/2026. Escopo: diagnóstico e planejamento; nenhuma correção do aplicativo foi implementada nesta rodada.

## Evidências obtidas

- ADB autorizado; Redmi Note 10, modelo M2101K7AI, Android 12. MIUI 14 informada pelo usuário.
- Instalado `com.example.argus_mobile`, versão 0.1.0, versionCode 1, APK debuggable. Não foi comprovada a identidade binária do APK com o código atual.
- CAMERA e RECORD_AUDIO concedidas. AppOps permite RECORD_AUDIO em primeiro plano; houve rejeição recente durante coleta com tela apagada. Isso não prova bloqueio durante uso com tela acesa.
- ARGUS aberto por `am start`; serviço Google iniciou reconhecimento com `callingApp: com.example.argus_mobile, locale: pt-BR`.
- Às 13:55:43: `RecognitionService#onMicrophoneOpened`; o STT chega ao serviço nativo e abre o microfone.
- Às 13:55:43: `SodaSpeechRecognizer: Failed to get language pack of required locale: error 13`. Falha de carregamento do pacote offline; não permite afirmar se ausente, corrompido ou incompatível.
- Reconhecedor online inicia simultaneamente. Às 13:56:23 houve `ONLINE_NO_PROGRESS`, junto de cancelamento; isoladamente isso não comprova falha de internet.
- Diversas sessões terminaram com `empty final recognition results` e `NO_SPEECH_DETECTED`. Houve eventos de início/fim de fala, que não comprovam compreensão de um comando humano.
- Exemplo: stop às 13:55:46.091 e resultado final nativo às 13:55:46.348. O resultado pode chegar depois do pedido de parada.
- A tela foi observada como `mWakefulness=Asleep` durante a coleta. TalkBack não estava ativo (`enabled_accessibility_services=null`).
- `flutter test --no-pub`: 7 testes passaram. `flutter analyze --no-pub`: sem problemas.
- Não existem testes do serviço de STT, do controlador de entrada ou do gesto de segurar/soltar.

Limite da validação: ainda é necessário correlacionar fala humana controlada, modo usado e retorno Dart. Foi solicitado ao usuário testar “Argus ajuda”, “ajuda” segurando/soltando e “ajuda” com mais dois segundos antes de soltar. Sem esse retorno não declarar sucesso ou falha de cada caso. Não foram validados áudio percebido, TalkBack, contraste nem análise de imagens no backend.

## Nova coleta após tentativas do usuário com celular desbloqueado

O usuário informou que desbloqueou o aparelho e falou, sem obter retorno. Logs consultados na sequência, com eventos entre 14:24 e 14:25:

- `callingApp: com.example.argus_mobile, locale: pt-BR` permanece confirmado.
- Às 14:24:45.766 aparece `#onResults withSpeech: true`. Isso altera a hipótese de ausência total de resultados: o serviço nativo reportou ao menos um resultado com fala. O log não expõe o texto, nem comprova sua entrega ao parser ou a qual gesto corresponde.
- Às 14:24:47.841 há `onStartOfSpeech`; às 14:24:47.955 há um novo `onStartListening`, seguido de `onMicrophoneDeactivated` às 14:24:47.970. Novas sessões também aparecem aproximadamente a cada 2–3 segundos.
- Outro exemplo: início de fala às 14:25:17.173, novo start às 14:25:17.636 e resultado vazio às 14:25:17.773. Essa ordem é compatível com reinício/conflito de sessões enquanto ainda chegam eventos anteriores; sem identificadores nativos e logs Dart, não comprova por si só a origem do reinício.
- Continua a falha offline `Failed to get language pack of required locale: error 13`.
- Às 14:25:23.764 aparecem `ONLINE_NO_PROGRESS`, `Recognizer network error` e `CANCELLED`, após pedido de stop. Não concluir que falta internet apenas com esse cancelamento.

Prioridade revisada: instrumentar texto e identificação de sessão (tarefa 1), reproduzir passivo/manual separadamente (2), testar a finalização e impedir reinícios/contaminação de callbacks (4–6 e 9). O pacote offline deve ser investigado em paralelo (3), mas não explica sozinho o resultado com fala observado. Ainda faltam os textos exatos falados, o modo de cada tentativa e o retorno Dart para fechar a causa. Nenhuma correção foi aplicada nesta coleta adicional.

## Achados no código e hipóteses

1. Serviço nativo retorna vazio: observado, causa ainda não isolada. Investigar fala controlada, pacote offline, serviço online e estado da tela. Idioma en-US e falta de permissão inicial não são as principais hipóteses nesta coleta.
2. Finalização prematura: `SpeechRecognitionService.stopAndGetText` completa com `_bestWords` logo após `stop`; `onStatus` também completa em `notListening`. O pacote 7.3.0 distingue `notListening` de `done` e prevê resultado final posterior. Risco confirmado pelo código; impacto sobre comando falado ainda depende de reprodução.
3. Erros ocultos: `_runPassiveLoop` e `_listenPushToTalk` usam `catch (_)`. Código, stack e fase são perdidos.
4. Corrida ao pressionar/soltar: `beginPushToTalk` aguarda TTS/cancel antes de marcar o modo; soltar nesse intervalo faz `finishPushToTalk` retornar, mas o início continua depois.
5. Resultado automático ignorado: `_listenPushToTalk` descarta o texto retornado por `listenOnce`; depende de uma soltura posterior. Callbacks antigos podem afetar `_bestWords` compartilhado.
6. Parser já normaliza caixa, acentos e pontuação. No modo manual rejeita “Argus ajuda” por contrato atual, documentado nos testes. Não adicionar aproximação fonética sem uma transcrição real que a justifique.
7. Escuta passiva é um loop de sessões curtas; não há serviço Android próprio para escuta contínua em segundo plano. `_wakeFeedbackSession` usa o mesmo identificador ao longo do loop, podendo vibrar apenas no primeiro despertar.
8. Transcrição superior e preferência persistida já existem. Entretanto `_processRecognizedText` copia texto sem wake word para o estado mesmo no modo passivo; o loop seguinte o apaga rapidamente.

## Regras para quem executar

Executar uma tarefa por vez. Preservar alterações existentes no repositório. Ler AGENTS.md e docs/01 a docs/07 antes de editar. Caminhos abaixo são relativos à raiz do repositório. Não atualizar dependências, trocar de STT, reorganizar backend ou implementar hotword em segundo plano como tentativa inicial. Cada correção deve incluir seu teste antes de seguir. Registrar casos não executados como pendentes, nunca aprovados.

1. **Objetivo: tornar uma tentativa de voz rastreável.**
   - Arquivos: alterar `app_flutter/lib/services/speech_recognition_service.dart` e `app_flutter/lib/controllers/voice_input_controller.dart`.
   - Passos: acrescentar logs de diagnóstico protegidos por `kDebugMode`, prefixo `[ARGUS_VOICE]`, horário, identificador de sessão, modo e evento. Em `listenOnce`, registrar entrada, retorno de initialize, idioma solicitado, início de listen, todos os status, resultado parcial/final e erro com `errorMsg`/`permanent`. Registrar stop/cancel/timeout. No controlador, registrar início/soltura, texto entregue ao parser, wake word exigida, ação encontrada, início/fim da execução. Substituir os dois `catch (_)` por captura de erro e stack com log. Para este experimento usar apenas as frases de teste; não gravar áudio. Ligar `debugLogging` do plugin apenas em debug. Não alterar o fluxo nesta tarefa.
   - Aceite: uma tentativa gera sequência correlacionável desde o gesto até resultado, erro ou timeout; build release não emite os logs de diagnóstico do app.

2. **Objetivo: reproduzir cada modo com o APK instrumentado. Depende de 1.**
   - Arquivos: criar `results/voz_redmi_2026-09-23/README.md`; usar `scripts/build_apk_mvp.ps1`.
   - Passos: executar `powershell -ExecutionPolicy Bypass -File scripts/build_apk_mvp.ps1 -Mode debug`; instalar com `.tools/android-sdk/platform-tools/adb.exe -s 10cf6cc7 install -r app_flutter/build/app/outputs/flutter-apk/app-debug.apk`. Registrar hash do APK e horário da instalação. Manter celular desbloqueado, tela acesa e ARGUS visível. Coletar logcat filtrado por `[ARGUS_VOICE]` e tags nativas de reconhecimento. Fazer três repetições de cada caso: silêncio por 15 s; “Argus ajuda” passivo; “ajuda” manual soltando ao terminar; “ajuda” manual aguardando 2 s para soltar. Registrar horário, texto, erro, ação e resposta audível de cada repetição. Não iniciar backend para estes comandos.
   - Aceite: tabela com 12 tentativas, ou linhas explicitamente pendentes se não houver operador disponível; nenhum resultado presumido a partir de captura do microfone.

3. **Objetivo: separar problema do reconhecedor e problema do aplicativo. Depende de 2.**
   - Arquivos: atualizar `results/voz_redmi_2026-09-23/README.md`; sem alteração de código.
   - Passos: com ARGUS fechado, testar ditado em português em um campo de texto, usando “ajuda” três vezes. Registrar que o teclado pode usar outro serviço e que sucesso ali não absolve o serviço do ARGUS. Repetir ARGUS com acesso à internet confirmado pelo operador. Se a falha offline persistir, conferir a disponibilidade do pacote pt-BR nas configurações do serviço de fala Google; instalar/rebaixar nenhum componente automaticamente. Se houver opção de baixar pt-BR, baixar e repetir a mesma matriz, anotando mudança. Não confundir voz TTS instalada com pacote STT. Se o Dart receber texto correto e parser devolver null, seguir a tarefa 7; se não houver texto nativo, manter investigação do serviço. Se final chegar depois de stop, aplicar 5.
   - Aceite: relatório diferencia resultado online, disponibilidade offline e retorno Dart; a mensagem `error 13` não é apresentada como causa única sem comparação antes/depois.

4. **Objetivo: criar testes reproduzíveis de callbacks de STT.**
   - Arquivos: criar `app_flutter/test/speech_recognition_service_test.dart`.
   - Passos: usar a injeção existente `SpeechRecognitionService(speech: ...)` com fake de `SpeechToText`; não adicionar biblioteca. O fake armazena callbacks de initialize/listen e permite emitir eventos em ordem controlada. Cobrir: parcial “abrir”, stop, notListening, final “abrir configurações”; resultado final sem parcial; done sem texto; erro na inicialização/escuta; cancelamento seguido de outra sessão; callback de resultado da sessão cancelada após início da seguinte.
   - Aceite: testes identificam perda de final ou contaminação de sessão no código anterior. Não enfraquecer expectativas para torná-los verdes.

5. **Objetivo: aguardar a conclusão real da fala sem misturar sessões. Depende de 4; aplicar ao defeito de finalização descrito acima.**
   - Arquivos: alterar `app_flutter/lib/services/speech_recognition_service.dart` e testes da tarefa 4.
   - Passos: remover conclusão em `notListening`; usar esse evento apenas como fim de captação. Em `stopAndGetText`, solicitar stop uma única vez e aguardar o Future da sessão. Concluir por resultado final, done, erro ou timeout limitado. Fixar espera final em 3 segundos após stop, superior ao `finalTimeout` padrão de 2 segundos do plugin; ao vencer, devolver último parcial da mesma sessão ou texto vazio. Manter watchdog de duração total separado da espera final. Tornar stop/cancel idempotentes. Invalidar sessão antes de cancelar; guardar texto/completer/timers por sessão; não deixar callback antigo de resultado alterar sessão nova. Para status/erros globais do plugin, serializar cancelamento/início e registrar eventos sem identificação nativa; não prometer isolamento que a API não fornece. Anexar tratamento de erro ao Future desde sua criação e limpar timers no finally.
   - Aceite: todos os testes de 4 passam; “abrir configurações” final vence “abrir” parcial; ausência de resultado não trava; nenhum Future sem tratamento ou execução duplicada.

6. **Objetivo: resolver o gesto rápido e garantir execução única no modo manual. Depende de 5.**
   - Arquivos: alterar `app_flutter/lib/controllers/voice_input_controller.dart`, `app_flutter/lib/models/voice_state.dart`, `app_flutter/lib/widgets/push_to_talk_button.dart`; criar `app_flutter/test/voice_input_controller_test.dart` e `app_flutter/test/push_to_talk_button_test.dart`.
   - Passos: acrescentar estado de preparação manual e marcar intenção de pressionamento antes do primeiro await. Soltura durante preparação deve cancelar essa intenção e impedir listen tardio. Centralizar conclusão manual em uma função por sessão, chamada tanto ao soltar quanto ao chegar final/timeout; executar parser no máximo uma vez. Revalidar sessão e dispose após cada await. Diferenciar cancelamento do gesto de envio: `onTapCancel` cancela, não executa comando. Manter alternância semântica acessível de iniciar/finalizar. Só anunciar prontidão e vibrar depois de status listening.
   - Aceite: testes simulam soltura antes de initialize, dois eventos de soltura, final antes de soltar, cancelamento e dispose pendente; no máximo uma ação por sessão e nenhuma escuta tardia após cancelamento.

7. **Objetivo: alterar o parser somente quando houver evidência de rejeição incorreta. Depende de 2 e 3.**
   - Arquivos: `app_flutter/lib/services/voice_command_parser.dart`, `app_flutter/test/voice_command_parser_test.dart`.
   - Passos: para cada texto correto rejeitado, registrar entrada exata, modo e ação esperada em teste. Corrigir apenas a regra demonstrada. Não usar contains, fuzzy matching ou NLP livre. Manter “Argus não tirar foto” rejeitado. Prefixo Argus opcional no modo manual depende da decisão D3 abaixo; se aprovado, remover somente prefixo inicial normalizado e manter lista fechada. Sem evidência e sem D3, não modificar parser.
   - Aceite: novos casos reproduzem os logs; todos os comandos negativos continuam rejeitados; capitalização e acentos continuam aceitos.

8. **Objetivo: separar silêncio de falhas e exibir estado de voz acessível. Depende de 1, 5 e 6.**
   - Arquivos: alterar `app_flutter/lib/controllers/voice_input_controller.dart`, `app_flutter/lib/models/voice_state.dart`, `app_flutter/lib/screens/camera_screen.dart`; criar `app_flutter/lib/models/voice_failure.dart` e ampliar testes do controlador.
   - Passos: representar falhas com categoria e código original. Mapear somente códigos efetivamente fornecidos pelo plugin: ausência de fala, permissão, rede, serviço ocupado e erro desconhecido. Silêncio passivo não anuncia “indisponível” a cada ciclo. Permissão negada interrompe tentativas automáticas e apresenta orientação audível uma vez. Erro desconhecido preserva código nos logs. Mostrar `voiceState.message` em um único status semântico na câmera, sem substituir a descrição de análise; anúncios somente em transições relevantes, sem leitura de cada parcial. Evitar loop de TTS seguido de autocaptura; pausar captura durante fala do próprio app e retomar após conclusão, se o modo ainda for solicitado.
   - Aceite: testes distinguem silêncio e permissão negada; erro fica acessível mesmo com transcrição desligada; uma mensagem TTS não causa nova execução de comando.

9. **Objetivo: isolar a política passiva e impedir concorrência entre modos. Depende de 6 e decisão D1/D2.**
   - Arquivos: alterar `app_flutter/lib/controllers/voice_input_controller.dart`, `app_flutter/lib/screens/camera_screen.dart`; criar `app_flutter/lib/controllers/passive_voice_flow.dart`, `app_flutter/lib/controllers/push_to_talk_flow.dart` e `app_flutter/test/voice_mode_arbitration_test.dart`.
   - Passos: mover a lógica de wake word/transcrição/despertar para PassiveVoiceFlow e intenção pressionar/soltar para PushToTalkFlow. Apenas VoiceInputController pode acessar o serviço STT compartilhado. Fluxos recebem eventos e devolvem intenções; não instanciam reconhecedores. Uma sessão nativa por vez. Após aprovação de D2, ao pressionar durante escuta passiva, invalidar/cancelar sessão passiva antes de iniciar manual. Não executar resultado passivo cancelado. Dar identificador próprio a cada ciclo passivo e vibrar uma vez por despertar, inclusive no ciclo seguinte. Em pause/dispose/suspensão, invalidar todos os trabalhos e não reiniciar automaticamente por retorno atrasado.
   - Aceite: testes cobrem pressão durante escuta passiva, pressão durante execução, dois despertares consecutivos, ida/volta de configurações, pausa e retorno; nunca dois listen concorrentes.

10. **Objetivo: preservar a caixa única e impedir transcrição de fala ambiente. Depende de 9.**
    - Arquivos: alterar `app_flutter/lib/controllers/voice_input_controller.dart`, `app_flutter/lib/screens/camera_screen.dart`, `app_flutter/lib/widgets/transcription_panel.dart`; criar `app_flutter/test/transcription_panel_test.dart` e `app_flutter/test/settings_service_test.dart`.
    - Passos: manter a caixa superior existente. Atualizar texto manual apenas da sessão manual ativa; atualizar texto passivo somente após wake word. Não copiar texto passivo sem Argus para estado de apresentação. Manter a chave `argus.voice.showTranscription`; condição de visibilidade fica exclusivamente na UI, nunca bloqueia parser. Testar persistência após nova instância de SettingsService. Ajustar restrição de altura da caixa apenas se teste de escala 2,0 revelar overflow; permitir conteúdo rolável e texto completo na semântica.
    - Aceite: preferência off esconde caixa sem impedir ação; fala sem wake word não aparece; existe apenas um painel; escala 2,0 sem overflow.

11. **Objetivo: tornar build e coleta repetíveis. Depende das correções selecionadas.**
    - Arquivos: criar `scripts/diagnose_android_voice.ps1`; alterar `scripts/build_apk_mvp.ps1` somente para metadados de entrega, se necessário.
    - Passos: script diagnóstico recebe Serial e OutputDirectory; valida ADB, dispositivo autorizado e pacote instalado; coleta versão, permissões e logs filtrados sem apagar logcat global nem gravar áudio. Falhar explicitamente em unauthorized/offline. Build mantém analyze/test e gera APK/hash já existentes; acrescentar manifesto de build com versão, data e estado dirty, sem segredos. Não alterar `scripts/run_backend_mvp.ps1`: nenhuma evidência atual associa falha STT ao backend.
    - Aceite: uma execução produz relatório legível com dispositivo e APK identificados; falhas de ADB retornam código não zero; APK continua configurando backend em runtime.

12. **Objetivo: validar no Redmi e documentar a entrega. Depende de 2–11 conforme aplicáveis.**
    - Arquivos: atualizar `results/voz_redmi_2026-09-23/README.md`, `docs/11_VOZ_ACESSIBILIDADE_MOBILE.md`, `README.md`.
    - Passos: rodar analyze e todos os testes; build/install do novo APK. Repetir matriz de 2 e acrescentar dez alternâncias passivo/manual, cinco toques rápidos, ida/volta de configurações, tela apagada/retorno e transcrição off/on. Com participação do operador, testar TalkBack: focar microfone, iniciar pela ação semântica, falar “ajuda” e finalizar; confirmar fala e vibração. Registrar quais casos exigem rede do serviço Google. Para backend parado, ajuda/modo porta devem funcionar; captura deve informar falha de conexão, separada de STT. Documentar estrutura dos fluxos e limitações de segundo plano.
    - Aceite: toda linha tem resultado e evidência; nenhum comando executado duas vezes; nenhum crash ou escuta após suspensão indevida. Falha ou caso pendente impede declarar validação completa de voz/acessibilidade.

## Decisões antes de executar as tarefas dependentes

- **D1 — Significado de escuta passiva:** (A) manter sessões curtas apenas com câmera visível, menor complexidade e possíveis intervalos sem escuta; (B) hotword local e suporte Android explícito para segundo plano/tela bloqueada, com escolha de motor, licença, permissões, notificação e consumo a validar. O pacote atual não deve ser apresentado como hotword contínua. Tarefas 1–8 independem de implantar B.
- **D2 — Pressionar durante execução:** (A) recusar novo comando e dar feedback de ocupado, mantendo a ação atual; (B) permitir interrupção apenas do TTS e de ações explicitamente canceláveis, exigindo contrato de cancelamento. Recomendação para IC: A. Não cancelar implicitamente envio/análise já iniciados.
- **D3 — Argus opcional no manual:** (A) aceitar “ajuda” e “Argus ajuda”, tornando uso mais tolerante; (B) manter somente comando direto, comportamento atual. Recomendação: A, com prefixo estritamente inicial.

## Commits sugeridos após validação

Separar `chore(voice): add diagnostic tracing`, `fix(voice): await final recognition results`, `fix(voice): serialize manual and passive sessions`, `fix(a11y): expose voice status and gate transcription`, `docs(voice): document Redmi validation`. Antes de publicar, executar `git status --short`, `git diff --check` e revisar `git diff --cached`; adicionar arquivos específicos, pois há alterações preexistentes de backend. Este diagnóstico não realizou commit ou push. Publicação deve incluir somente mudanças revisadas e autorizadas para a entrega.
