# README tecnico - ARGUS IC

## Elementos de acessibilidade e modelo customizado

O backend possui suporte semantico para classes de acessibilidade quando elas forem retornadas pelo modelo de deteccao:

- `ramp` -> rampa
- `handrail` -> corrimao
- `tactile_paving` -> piso tatil
- `accessibility_sign` -> sinalizacao de acessibilidade
- `wheelchair_ramp` -> rampa acessivel
- `accessible_entrance` -> entrada acessivel
- `elevator` -> elevador
- `stairs` -> escada
- `step` -> degrau

O YOLO generico treinado em COCO provavelmente nao detecta esses elementos com boa precisao. Para reconhecer esses recursos em ambientes internos, recomenda-se criar um dataset especifico, anotado manualmente ou com apoio do Roboflow.

Fluxo recomendado:

1. Coletar imagens internas com recursos de acessibilidade.
2. Anotar as classes de interesse.
3. Treinar um YOLO leve no Google Colab.
4. Exportar o melhor peso como `models/best.pt`.
5. Rodar o backend com `ARGUS_YOLO_MODEL_PATH=models/best.pt`.

Mais detalhes estao em `docs/dataset_accessibilidade.md`.

## Modos do endpoint `/detect`

O endpoint aceita dois modos:

- `mode=exploration`: modo padrao. Resume pontos de interesse, acessibilidade e obstaculos relevantes no frame atual.
- `mode=navigation&target_class=door`: orientacao local simples ate um alvo visivel, como `door`, `elevator` ou `reception`.

Exemplos:

```bash
curl -X POST "http://127.0.0.1:8000/detect?mode=exploration" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
curl -X POST "http://127.0.0.1:8000/detect?mode=navigation&target_class=door" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
```

O modo de navegacao nao implementa SLAM, mapa 3D ou rota global. Ele apenas usa a deteccao do frame atual, posicao horizontal e profundidade monocular relativa para sugerir uma direcao curta.

## Detector open-vocabulary experimental

O backend tambem aceita `use_open_vocab=true` para complementar o YOLO atual com um detector de vocabulario aberto. A prioridade esperada e YOLOE, com fallback para YOLO-World quando disponivel no ambiente.

```bash
curl -X POST "http://127.0.0.1:8000/detect?mode=exploration&use_open_vocab=true" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
```

Esse recurso nao e padrao porque precisa ser comparado em latencia e qualidade nas imagens do ARGUS IC. Use:

```bash
python scripts/evaluate_navigation_detection.py --image-dir tests/img_exemplo --compare-open-vocab
```

## Modelo YOLO customizado futuro

Para substituir o detector generico por um modelo treinado com classes de pontos de interesse e acessibilidade, exporte o melhor peso como `models/best.pt` e rode o backend com:

```bash
set ARGUS_YOLO_MODEL_PATH=models/best.pt
```

Para o detector open-vocabulary experimental, os caminhos podem ser ajustados com:

```bash
set ARGUS_YOLOE_MODEL_PATH=models/yoloe_custom.pt
set ARGUS_YOLO_WORLD_MODEL_PATH=models/yolo_world_custom.pt
```
