# Reorganização de 23/09/2026

Objetivo: tornar o repositório compreensível e reproduzível sem ampliar o escopo da IC ou retomar a correção de voz adiada.

## Arquivos movidos

| Origem | Destino |
|---|---|
| `curl_runner.py` | `scripts/benchmark_api.py` |
| `test_image.py` | `scripts/test_yolo_image.py` |
| `ARGUS_CONTEXT_MVP_FLUTTER_CODEX.md` | `docs/history/MVP_MOBILE_CONTEXT.md` |
| `docs/08_CRONOGRAMA_MUDANCAS_POI_DATASETS.md` | `docs/history/08_CRONOGRAMA_MUDANCAS_POI_DATASETS.md` |
| `docs/09_ARGUS_ROUTED_DETECTION_CODEX_PROMPT.md` | `docs/history/09_ARGUS_ROUTED_DETECTION_CODEX_PROMPT.md` |
| `docs/12_DIAGNOSTICO_VOZ_REDMI_E_PLANO.md` | `docs/history/12_DIAGNOSTICO_VOZ_REDMI_E_PLANO.md` |

O benchmark HTTP passa a ler `ARGUS_DETECT_URL`; a constante duplicada da imagem foi removida. O teste YOLO passou a localizar o pacote `app` a partir de seu novo diretório.

## Remoções e consolidação

- `mobile_flutter/`: somente diretórios vazios; `app_flutter/` é o aplicativo atual.
- Instalador local do Postman: removido com confirmação do responsável; não pertencia ao código.
- `README_Codex_Context.md`: instruía a copiar um pacote de documentos já incorporado. Substituído pelo índice e guia atuais.
- Dois guias `docs/10_*`: continham instruções antigas de build com URL e duplicavam deploy. Consolidados em `DEPLOYMENT.md`.
- `app/services/analysis_service.py`, `app/vision/detection.py` e `PlaceholderDepthEstimator`: caminho inicial simulado sem consumidores externos, substituído pelo pipeline real.
- `app_flutter/lib/controllers/voice_command_controller.dart`: controlador sem consumidores, substituído por `VoiceInputController`.
- `app/guidance/navigation_policy.py`: removidas definições antigas sobrescritas no mesmo arquivo e seus auxiliares; preservadas as funções públicas que delegam para `NavigationPriority`.

## Preservado

Módulos experimentais ativos, testes, imagens já versionadas, fundamentos 01–07, pesos locais, SDKs, APK existente e resultados científicos locais. A limpeza não remove caches indiscriminadamente nem descarta experimentos por não participarem do perfil MVP.

O backend continua em `app/` e o Flutter mantém separação por telas, widgets, controladores, serviços e modelos. Uma mudança de diretório de todo o backend acrescentaria migração de imports e comandos sem benefício necessário nesta etapa.

## Publicação

O código Flutter e as alterações locais anteriores do MVP passam a integrar o repositório. `.gitignore` exclui ambientes, caches, APKs, pesos, logs, segredos e resultados gerados; mantém o README de resultados. `.dockerignore` impede que SDKs e artefatos locais sejam enviados ao contexto de build.
