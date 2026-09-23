# Mapa da codebase e guia para agentes

Este documento descreve a implementação atual. Leia [AGENTS.md](../AGENTS.md), os fundamentos 01–07 e [PENDENCIAS.md](PENDENCIAS.md) antes de editar. O objetivo é uma demonstração de IC em ambientes internos: imagem → detecção e profundidade relativa → mensagem → áudio.

## Pontos de entrada

| Entrada | Responsabilidade |
|---|---|
| `app/server.py:main` | Lê host/porta do ambiente e inicia Uvicorn com um worker |
| `app/main.py` | Instancia FastAPI e registra as rotas |
| `app/routes/detect.py:detect_image` | Valida upload/modo, controla concorrência e chama o pipeline |
| `app/services/detection_pipeline.py:DetectionPipeline.analyze` | Coordena inferência, profundidade, orientação e resposta |
| `app_flutter/lib/main.dart:main` | Carrega preferências, configura TTS e cria `ArgusApp` |
| `app_flutter/lib/screens/camera_screen.dart` | Integra câmera, controles, ciclo de vida e despacho das ações de voz |
| `scripts/run_backend_mvp.ps1` | Prepara/testa/inicia o backend local |
| `scripts/build_apk_mvp.ps1` | Resolve toolchain, analisa/testa e gera APK |

## Backend: responsabilidades

| Caminho | O que fica aqui |
|---|---|
| `app/config.py` | Flags, limites, prompts e configuração por ambiente |
| `app/errors.py` | Exceções operacionais com código e status HTTP |
| `app/routes/` | Contrato HTTP; não colocar inferência pesada nas funções de rota |
| `app/schemas/detection.py` | Modelos Pydantic de detecção, profundidade, navegação, áudio e readiness |
| `app/services/detection_pipeline.py` | Orquestração; permite injetar detectores/estimador nos testes |
| `app/routing/` | `SceneRouter` monta `DetectionPlan`; `GeneralistSceneAnalyzer` fornece achados para refinar o plano |
| `app/vision/yolo_detector.py` | Detector geral e carregamento dos pesos YOLO |
| `app/vision/open_vocabulary_detector.py` | Detecção experimental por vocabulário aberto, incluindo portas |
| `app/vision/midas_estimator.py` | Carregamento sob demanda do MiDaS e mapa relativo normalizado |
| `app/vision/depth.py` | Mediana do mapa na bbox, zona horizontal e categoria de proximidade |
| `app/vision/preprocessing.py` | Decodificação e preparação da imagem |
| `app/detection/` | Especialistas opcionais, mapeamento de classes, fusão e pós-processamento |
| `app/guidance/` | Priorização e geração de mensagem em português |
| `app/navigation/` | Seleção de alvo e orientação local baseada no frame atual |
| `app/audio/speech_payload.py` | Monta instrução de áudio; não sintetiza som no servidor |

`navigation_policy.py` mantém duas funções públicas usadas pelo pipeline e testes, delegando para `NavigationPriority`. `message_builder.py` contém regras de frase ainda cobertas por testes; não confundir com o gerador usado diretamente pelo pipeline, `MessageGenerator`.

### Caminho de uma análise

1. Flutter envia multipart com campo `image` e parâmetros de modo.
2. A rota valida modo, tipo, limite de bytes e tamanho decodificado; adquire um lock sem esperar.
3. `run_in_threadpool` chama `DetectionPipeline.analyze` sem executar a inferência diretamente no event loop.
4. O router cria o plano, o analisador generalista produz achados e o plano é refinado. O perfil MVP restringe o plano final.
5. Detectores selecionados produzem `ObjectDetection`; fusão e pós-processamento removem redundâncias.
6. Com detecções válidas, MiDaS estima profundidade; `combine_detections_with_depth` associa a mediana da bbox a cada objeto.
7. Priorização e navegação local produzem uma orientação; `MessageGenerator` cria a frase e `build_audio_payload` prepara os metadados de áudio.
8. A API retorna `DetectionResponse`; o Flutter interpreta a resposta e a lê com TTS.

No perfil MVP, falha do MiDaS com objetos detectados gera erro. Fora dele existe fallback experimental identificado na resposta; isso não é evidência de profundidade monocular real. Sem objetos, `depth_source=not_run` é esperado.

## Flutter: separação por camada

Todos os caminhos abaixo são relativos a `app_flutter/lib/`.

| Arquivo/pasta | Responsabilidade |
|---|---|
| `screens/camera_screen.dart` | Layout, inicialização/liberação da câmera, estados do app, execução das ações |
| `screens/settings_screen.dart` | Edição e validação das preferências |
| `widgets/accessible_action_button.dart` | Botão compartilhado com semântica e área de toque |
| `widgets/push_to_talk_button.dart` | Eventos do gesto e ativação semântica do microfone |
| `widgets/transcription_panel.dart` | Caixa única de transcrição |
| `widgets/system_status.dart` | Exibição/semântica do estado |
| `controllers/analysis_controller.dart` | Captura, chamada da API, TTS da resposta e remoção do arquivo temporário |
| `controllers/voice_input_controller.dart` | Coordena sessões passivas/manuais, transcrição e despacho ao handler |
| `services/speech_recognition_service.dart` | Encapsula `speech_to_text`, locale, resultados, stop/cancel e logs |
| `services/voice_command_parser.dart` | Normalização e mapa fechado de texto → `VoiceAction` |
| `services/argus_api_service.dart` | Readiness, upload multipart, timeouts e erros HTTP |
| `services/settings_service.dart` | `ArgusSettings` e persistência via SharedPreferences |
| `services/tts_service.dart` | Seleção de voz/idioma, fala, interrupção e volume |
| `services/feedback_service.dart` | Combina resposta falada e feedback tátil |
| `services/media_volume_service.dart` | Integração com volume de mídia Android |
| `services/system_ui_service.dart` | Modo de exibição das barras do sistema |
| `config/app_config.dart` | Montagem da URL e timeouts, sem host compilado |
| `models/` | Resposta da API, comandos e estado de voz |

`android/app/src/main/kotlin/com/example/argus_mobile/MainActivity.kt` contém a integração nativa Android. `AndroidManifest.xml` declara permissões e consultas de serviços. A plataforma entregue no repositório é Android; iOS/VoiceOver não foram preparados nem validados.

## Onde alterar cada comportamento

| Tarefa | Arquivos principais | Validação relacionada |
|---|---|---|
| Novo campo na resposta | `app/schemas/detection.py`, pipeline, `models/detection_response.dart` | `tests/test_api.py`, `test/detection_response_test.dart` |
| Regra de profundidade | `midas_estimator.py`, `depth.py` | `test_midas_estimator.py`, `test_depth_combination.py` |
| Regra de orientação | `guidance/`, `navigation/` | Testes de guidance, navigation e local navigator |
| Novo comando de voz | Parser, `models/voice_command.dart`, handler na câmera | `test/voice_command_parser_test.dart`; teste no aparelho |
| Preferência persistida | `SettingsService`, tela de configurações e consumidor | Testes de config e reinício do app |
| Layout acessível | Tela e widgets correspondentes | Analyze, teste de widget quando aplicável e TalkBack |
| Porta/endereço do backend | Ambiente/scripts; host do celular em Configurações | `/health`, `/ready`, upload de imagem |

Os nomes de testes Flutter acima ficam em `app_flutter/test/`; os Python em `tests/`. Use [DEVELOPMENT.md](DEVELOPMENT.md) para os comandos completos.

## Regras para continuar sem perder contexto

1. Consulte `git status` antes de editar. Alterações locais podem ser trabalho do responsável.
2. Siga os imports e chamadas reais; não implemente um plano em `docs/history/` por ele existir.
3. Não reintroduza o antigo `AnalysisService` simulado ou o `VoiceCommandController` substituído. O fluxo ativo é o descrito acima.
4. Não trate a voz como resolvida. Leia a pendência V01 antes de retomá-la; nesta reorganização não houve nova correção do STT.
5. Mantenha os contratos Python/Dart sincronizados. Prefira injeção de fakes para testes de lógica; registre separadamente inferência real e validação no aparelho.
6. Preserve a configuração local: sem host do usuário no código Flutter, sem chaves/caches/pesos no Git.
7. Ao mudar comportamento, atualize o guia correspondente e o estado da pendência. Declare o que foi testado e o que continua sem comprovação.
