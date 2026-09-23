# Backend: API, modelos e configuração

## Contrato HTTP

A API FastAPI é criada em `app/main.py`. Com o servidor ativo, `/docs` exibe o contrato OpenAPI da implementação.

| Endpoint | Comportamento |
|---|---|
| `GET /health` | Processo vivo: `status=ok`, `project=ARGUS IC` |
| `GET /ready` | Informa `ready`, `busy`, perfil e modelos carregados sob demanda |
| `POST /detect` | Recebe multipart no campo `image`; retorna detecções e mensagem para TTS |

`/ready` não executa inferência: `ready=true` não comprova que pesos foram baixados ou que MiDaS funciona. A rota usa um lock por processo para uma análise por vez; rode um worker no protótipo.

O upload aceita JPEG, PNG e WebP. Limites padrão: 5 MiB compactados e 12 milhões de pixels decodificados. `mode` aceita `fast`, `poi`, `tactile`, `auto`, `exploration` e `navigation`. O aplicativo usa `exploration` ou `navigation&target_class=door`.

Parâmetros experimentais: `use_open_vocab`, `use_semantic_segmentation`, `use_tactile_specialist`, `use_classic_tactile`, `use_ocr`. O roteador decide os modelos finais; consulte `detection_plan`, `models_called` e `notes` na resposta em vez de presumir que todas as flags executarão um especialista.

`DetectionResponse`, em `app/schemas/detection.py`, contém as detecções, caixas, zonas, profundidade, mensagem, `audio`, navegação, tempos e rastreabilidade dos modelos. O backend devolve **texto e metadados** para síntese; o som é produzido no Flutter.

Erros de validação usam HTTP 400/413; backend ocupado retorna 429 com `Retry-After`. Falhas operacionais como `DEPTH_UNAVAILABLE` e `TARGET_DETECTOR_UNAVAILABLE` usam 503. A forma estruturada é `detail: {code, message}`; nem todas as exceções genéricas seguem essa forma. Não apresentar indisponibilidade do modelo como ausência de obstáculos.

## Perfil de demonstração

Use `ARGUS_MVP_PROFILE=true`, como faz o script de execução. Navegação é restrita a porta; o plano final reduz especialistas opcionais e a profundidade real é obrigatória quando há detecções. O plano inicial/análise generalista ainda ocorre antes da restrição final; não afirmar ausência absoluta de trabalho extra apenas por ativar o perfil.

Se não houver detecções, MiDaS não é executado e `depth_source=not_run`. Se houver detecções e MiDaS falhar, o MVP responde com erro. Fora do perfil, o pipeline pode usar `depth_source=fallback` e registrar a limitação em `notes`; esse resultado não valida profundidade monocular real.

## Modelos

- `YoloDetector`: objetos gerais; pesos indicados por `ARGUS_YOLO_MODEL_PATH`.
- `OpenVocabularyDetector`: YOLOE com alternativa YOLO-World; caminhos em `ARGUS_YOLOE_MODEL_PATH` e `ARGUS_YOLO_WORLD_MODEL_PATH`.
- `MidasEstimator`: `MiDaS_small` via Torch Hub, carregado na primeira inferência. O cache deve ficar em `models/torch` por meio de `TORCH_HOME`.
- Especialistas de piso tátil, OCR, segmentação e heurísticas: experimentais, preservados para comparação científica.

Rode `scripts/prepare_models.ps1` antes de demonstrações. Ele prepara `models/yolo/yolov8n.pt`, `models/yolo/yoloe-11s-seg.pt`, `models/yolo/yolov8s-world.pt` e o cache do MiDaS em `models/torch`. `run_backend_mvp.ps1` aponta para esses caminhos automaticamente quando as variáveis ainda não foram definidas. Coloque pesos customizados em `models/` e aponte a variável correspondente. Não inclua pesos no Git. O detector COCO genérico não garante classes como portas ou piso tátil; veja [datasets](dataset_accessibilidade.md) e [roteamento](routed_detection_architecture.md).

A profundidade é normalizada por imagem. Valores maiores representam maior proximidade no contrato atual; a mediana da região da bbox é classificada em `very_near`, `near`, `medium` ou `far`. Não comparar esses valores como metros nem como escala absoluta entre frames.

## Configuração

| Variável | Finalidade |
|---|---|
| `ARGUS_BACKEND_HOST`, `ARGUS_BACKEND_PORT` | Obrigatórias ao usar `python -m app.server` |
| `ARGUS_MVP_PROFILE` | Restrições do protótipo de demonstração |
| `ARGUS_MAX_UPLOAD_BYTES` | Limite de bytes recebidos |
| `ARGUS_MAX_DECODED_PIXELS` | Limite da imagem decodificada |
| `ARGUS_DETECT_RETRY_AFTER_SECONDS` | Cabeçalho de nova tentativa quando ocupado |
| `ARGUS_YOLO_MODEL_PATH` | Nome/caminho dos pesos gerais |
| `ARGUS_YOLOE_MODEL_PATH`, `ARGUS_YOLO_WORLD_MODEL_PATH` | Pesos de vocabulário aberto |
| `ARGUS_TACTILE_MODEL_PATH` | Peso opcional do especialista de piso tátil |
| `TORCH_HOME` | Cache local do PyTorch/Torch Hub usado pelo MiDaS |
| `ARGUS_DETECT_URL` | URL completa para scripts HTTP; não é lida pelo app móvel |

A configuração Python é lida na importação: reinicie o processo após alterar variáveis. O app tem preferências independentes para host/protocolo/porta/timeouts. Não usar `--dart-define` para endereço do backend.

Consulte [desenvolvimento](DEVELOPMENT.md) para comandos e [CODEBASE](CODEBASE.md) para o mapa dos módulos. Preserve os nomes do contrato ao reorganizar código; mudanças exigem atualizar o parser Dart e os testes de ambos os lados.
