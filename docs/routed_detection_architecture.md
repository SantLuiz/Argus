# Arquitetura de detecção roteada - ARGUS IC

## Objetivo

A detecção roteada evita rodar todos os modelos em toda imagem. O ARGUS usa um plano simples para decidir quando acionar modelos generalistas, especialistas e heurísticas, mantendo o foco da IC: demonstrar detecção útil para orientação indoor com profundidade monocular e mensagem curta em áudio.

## Fluxo

```text
Imagem
-> SceneRouter / DetectionPlan
-> GeneralistSceneAnalyzer, quando habilitado
-> Detectores necessários
-> DetectionMerger
-> Profundidade monocular
-> NavigationPriority
-> LocalNavigator, quando houver alvo
-> MessageGenerator
```

## GeneralistSceneAnalyzer

O `GeneralistSceneAnalyzer` procura indícios de portas, elevadores, escadas, recepções, rampas e piso tátil. Ele não gera a resposta final. Sua função é alimentar o `SceneRouter` com evidências para decidir quais detectores acionar.

O analisador pode usar YOLOE primeiro e YOLO-World como fallback via `OpenVocabularyDetector`. Se os pesos ou dependências não estiverem disponíveis, o pipeline continua com YOLO padrão.

## SegFormer/ADE20K

`SemanticSegmentationDetector` é uma interface opcional para SegFormer/ADE20K. Por padrão fica desabilitada, porque `transformers`, pesos e latência ainda precisam ser validados. Quando habilitada, deve servir como evidência complementar para estruturas como chão, parede, porta, escada e passagem.

## Especialistas

- `TactilePavingDetector`: prepara uso futuro de `models/tactile_best.pt` ou outro `best.pt` treinado para piso tátil.
- `ClassicTactileDetector`: fallback OpenCV com HSV/contornos para possível piso tátil amarelo ou de alto contraste.
- `OCRSignDetector`: OCR opcional para placas de elevador, recepção, entrada, saída e acessibilidade.
- `StairRampHeuristicDetector`: heurística simples com bordas/linhas para escadas e rampas.

Nenhum especialista deve ser tratado como medição definitiva. Heurísticas retornam confiança baixa ou média.

## Modos

- `fast`: YOLO padrão e profundidade. Prioriza latência.
- `poi`: YOLO padrão + open-vocabulary para pontos de interesse.
- `tactile`: foco em piso tátil, especialista configurável e fallback OpenCV.
- `auto`: o roteador decide conforme alvo, flags e indícios.
- `exploration`: compatibilidade com modo anterior, comportamento leve.
- `navigation`: compatibilidade com modo anterior, exige `target_class` e usa navegação local.

## Endpoint

Exemplos:

```bash
curl -X POST "http://127.0.0.1:8000/detect?mode=fast" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
curl -X POST "http://127.0.0.1:8000/detect?mode=poi&target_class=elevator&use_open_vocab=true" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
curl -X POST "http://127.0.0.1:8000/detect?mode=tactile&use_classic_tactile=true" -F "image=@tests/img_exemplo/[REAL]corredor_piso_tátil.jpg"
curl -X POST "http://127.0.0.1:8000/detect?mode=auto&use_semantic_segmentation=true" -F "image=@tests/img_exemplo/[IA]corredor_elevador.jpg"
```

## Retorno

O JSON inclui:

- `detection_plan`: plano usado pelo roteador;
- `generalist_findings`: indícios encontrados pelo generalista;
- `models_called`: detectores acionados;
- `detections`: detecções finais com profundidade;
- `navigation`: orientação local quando aplicável.

Exemplo resumido:

```json
{
  "message": "Porta à frente, distância média.",
  "mode": "poi",
  "detection_plan": {
    "use_default_yolo": true,
    "use_open_vocab": true,
    "use_classic_tactile": false
  },
  "generalist_findings": [],
  "models_called": ["default_yolo", "yoloe"],
  "detections": []
}
```

## Benchmark

Use:

```bash
python scripts/benchmark_routed_detection.py
```

O CSV é salvo em:

```text
results/evaluation/routed_detection_benchmark.csv
```

## Limitações

O ARGUS IC não implementa SLAM, mapa 3D, navegação global ou distância métrica exata. O roteamento é experimental e serve para comparar latência e qualidade de mensagens. Modelos como YOLOE, YOLO-World, SegFormer e OCR são opcionais/fallback e não devem quebrar o backend quando ausentes.

## Evolução futura

Os especialistas podem ser substituídos por modelos treinados com datasets próprios, exportados como `best.pt`, por exemplo:

```bash
set ARGUS_YOLO_MODEL_PATH=models/best.pt
set ARGUS_TACTILE_MODEL_PATH=models/tactile_best.pt
```

