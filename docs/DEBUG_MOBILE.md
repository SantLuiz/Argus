# Diagnóstico no aplicativo móvel

Este guia descreve o diagnóstico observável no próprio aplicativo ARGUS e o protocolo para investigar câmera, rede e voz sem depender de um computador conectado. Ele não declara resolvida a falha de reconhecimento de voz no Redmi Note 10; consulte [PENDENCIAS.md](PENDENCIAS.md).

## Contrato do log de debug

- A preferência **Mostrar debug na tela** começa desligada e é persistida no aparelho.
- O mecanismo existe em builds debug e release. Ele não depende de `kDebugMode`.
- Enquanto desligado, nenhum evento é armazenado. Ao desligá-lo, todo o histórico da sessão é apagado imediatamente.
- Enquanto ligado, o histórico completo fica somente em memória e desaparece quando o processo termina. Logs, transcrições e respostas não são gravados em arquivo nem enviados ao backend.
- A câmera mostra apenas o evento mais recente. Configurações mostra o histórico da sessão em ordem cronológica.
- Cada evento contém sequência, horário, categoria, severidade, código, mensagem e, quando aplicável, identificador da operação.
- O identificador correlaciona começo e término de uma captura, requisição ou sessão de voz; ele não representa usuário nem aparelho.
- A linha de debug não usa TTS, vibração ou `liveRegion`. Portanto, novos eventos não interrompem continuamente o usuário ou o leitor de tela.
- O texto reconhecido pode aparecer no diagnóstico. Mantenha a sessão local e revise qualquer trecho antes de compartilhá-lo.

Debug e transcrição são preferências independentes. Ativar debug não obriga a exibir a caixa de transcrição, e ocultar a transcrição não desativa o reconhecimento de voz.

## Como interpretar um evento

Uma sequência de eventos permite separar três níveis que antes podiam parecer uma única falha:

1. **Solicitação do ARGUS:** o controlador pediu abertura da câmera, escuta ou requisição.
2. **Retorno da plataforma/serviço:** Android informou estado de escuta ou o backend respondeu um status HTTP.
3. **Resultado do aplicativo:** o parser aceitou/rejeitou o texto e a ação terminou ou falhou.

Um evento comprova apenas o fato que descreve. Por exemplo, `speech.listen_requested` comprova uma solicitação ao plugin; somente `speech.status` com o estado correspondente mostra o retorno nativo. Da mesma forma, resposta de `/ready` comprova comunicação com o processo, não carregamento bem-sucedido dos modelos lazy.

## Instrumentação

Os códigos ficam centralizados em `app_flutter/lib/models/debug_event.dart`. A tabela abaixo é o mapa de rastreabilidade da instrumentação móvel.

| Área | Arquivo e pontos observados | Códigos principais |
|---|---|---|
| Estado do debug e preferências | `debug_log_service.dart`; alterações em Configurações | `debug.enabled`, `settings.changed` |
| Câmera e ciclo de vida | `camera_screen.dart`: inicialização, ciclo de vida e ida/volta de Configurações | `camera.initializing`, `camera.ready`, `camera.failed`, `app.lifecycle`, `settings.opened`, `settings.closed` |
| Captura e análise | `analysis_controller.dart`: captura, análise e finalização | `analysis.capture_started`, `analysis.capture_completed`, `analysis.completed`, `analysis.failed`, `analysis.finished` |
| HTTP | `argus_api_service.dart`: `/ready` e `/detect` | `network.request_started`, `network.response_received`, `network.timeout`, `network.connection_failed`, `network.invalid_response`, `network.configuration_missing` |
| Reconhecimento nativo | `speech_recognition_service.dart`: inicialização, callbacks, stop e cancel | `speech.initialization`, `speech.availability`, `speech.listen_requested`, `speech.status`, `speech.partial`, `speech.final`, `speech.timeout`, `speech.error`, `speech.stopped`, `speech.canceled` |
| Coordenação de voz | `voice_input_controller.dart`: passivo, PTT, wake word, parser e execução | `voice.passive_started`, `voice.passive_suspended`, `voice.wake_word`, `voice.parser_accepted`, `voice.parser_rejected`, `voice.action_started`, `voice.action_completed`, `voice.action_failed`, `voice.ptt_started`, `voice.ptt_finished` |
| Síntese | `tts_service.dart`: configuração, fala e interrupção | `tts.configured`, `tts.speak_requested`, `tts.speak_completed`, `tts.stopped`, `tts.failed` |

Não registrar bytes de imagem/áudio, cabeçalhos de autenticação ou respostas HTTP completas. Exceções devem preservar tipo e mensagem úteis, sem transformar hipótese em causa confirmada.

## Escuta passiva e push-to-talk

A preferência **Ativar escuta passiva — Argus** começa desligada, inclusive depois de uma atualização que ainda não possua a chave persistida. Ela controla somente o Modo A:

- O Modo A pode iniciar apenas com a tela da câmera disponível e o aplicativo em primeiro plano.
- Ao desligá-lo, a sessão passiva atual é invalidada e resultados tardios não devem executar ações.
- Abrir Configurações, bloquear o aparelho ou mandar o aplicativo para segundo plano suspende a escuta passiva.
- O botão push-to-talk continua disponível quando o Modo A está desligado.
- Desligar o Modo A durante push-to-talk não cancela o comando manual atual; impede apenas a retomada passiva posterior.
- Uma ação já iniciada pode terminar, mas não deve abrir outra sessão passiva se a preferência ou a tela não permitirem.

Esse controle ajuda a comparar condições e evitar reinícios indesejados. Ele não corrige nem comprova corrigida a falha do STT observada no Redmi.

## Roteiro de diagnóstico no celular

Use o mesmo APK, aparelho e backend em toda a comparação. Ative o debug e mantenha anotados os horários aproximados.

1. Com Modo A desligado, abra a câmera, faça cinco capturas e registre sucesso, timeout ou erro.
2. Ainda desligado, faça cinco tentativas de PTT dizendo `ajuda`. Registre início, status nativo, texto final, decisão do parser e execução.
3. Ative o Modo A e repita cinco capturas e cinco tentativas de PTT.
4. Em uma sessão passiva, diga `Argus ajuda`; diferencie wake word detectada, parser aceito e ação executada.
5. Abra e feche Configurações, bloqueie/desbloqueie o aparelho e confirme pelos eventos se houve suspensão e retomada permitida.
6. Teste o backend disponível e indisponível. Separe timeout, falha de conexão, HTTP inválido e resposta inválida.
7. Observe se TTS e STT se sobrepõem e se os sons nativos de reconhecimento deixam de ocorrer com o Modo A desligado. O ARGUS não silencia globalmente sons do Android.

Registre cada tentativa como uma linha: condição, horário, identificador de sessão/operação, últimos códigos, texto reconhecido, resultado e observação sobre TTS. Atribua causa somente quando o comportamento for reproduzível e os eventos sustentarem a conclusão.

## Validação e limites

Execute `flutter analyze` e `flutter test` em `app_flutter/`, depois gere o APK release pelo script descrito em [DEVELOPMENT.md](DEVELOPMENT.md). Testes automatizados verificam contratos e lógica; não validam câmera, serviço STT do Android, TalkBack ou áudio real.

A instalação e a execução manual no Redmi Note 10, Android 12/MIUI 14, ficam com o responsável pelo aparelho. Até essa execução, marque cada caso manual como **não testado no dispositivo**, sem preencher resultados por inferência.
