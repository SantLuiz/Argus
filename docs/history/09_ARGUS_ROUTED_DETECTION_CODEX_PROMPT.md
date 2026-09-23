# Prompt para Codex — Arquitetura de Detecção Roteada com Modelos Generalistas e Especialistas

Leia primeiro o `AGENTS.md` e os documentos da pasta `docs` antes de alterar qualquer arquivo. Analise a estrutura atual do backend Python e preserve o que já existe: YOLO padrão, pós-processamento, estimativa monocular de profundidade, priorização semântica, geração de mensagens e modos de detecção já implementados.

## Objetivo desta tarefa

Implementar uma arquitetura de roteamento inteligente de modelos para o ARGUS IC, usando **YOLOE/YOLO-World** e **SegFormer/ADE20K** como modelos generalistas para identificar indícios de pontos de interesse e, a partir disso, chamar detectores especializados apenas quando necessário.

## Pontos de interesse prioritários

- Portas;
- Elevadores;
- Escadas;
- Recepções;
- Pisos táteis;
- Rampas.

## Restrições importantes

- Não implemente Flutter.
- Não implemente treinamento customizado agora.
- Não implemente SLAM.
- Não implemente mapa 3D.
- Não implemente navegação global.
- Preserve o pipeline existente sempre que possível.
- O sistema deve continuar funcionando mesmo se YOLOE, YOLO-World, SegFormer ou OCR não estiverem disponíveis.

---

## Arquitetura desejada

```text
Frame da câmera ou imagem
↓
GeneralistSceneAnalyzer
↓
DetectionPlan
↓
Detectores especializados necessários
↓
DetectionMerger
↓
Estimativa monocular de profundidade
↓
NavigationPriority
↓
LocalNavigator, quando houver alvo
↓
MessageGenerator
```

---

## 1. Criar `GeneralistSceneAnalyzer`

Crie um módulo responsável por analisar rapidamente a cena e identificar indícios dos pontos de interesse.

Arquivo sugerido:

```text
app/routing/generalist_scene_analyzer.py
```

Ele deve usar, quando disponível:

1. **YOLOE** como primeira opção de generalista open-vocabulary.
2. **YOLO-World** como fallback caso YOLOE não esteja disponível ou falhe.
3. **SegFormer pré-treinado em ADE20K** como generalista estrutural/semântico para entender elementos como chão, parede, porta, escada e área livre.

O objetivo do `GeneralistSceneAnalyzer` **não é gerar a resposta final ao usuário**. Ele deve apenas identificar indícios e decidir quais especialistas chamar.

### Classes/prompts do YOLOE/YOLO-World

```text
door
elevator
elevator door
stairs
staircase
reception desk
reception area
tactile paving
tactile floor
guiding block
warning block
ramp
accessibility ramp
wheelchair ramp
handrail
accessibility sign
entrance
exit
hallway
corridor
```

### Classes/áreas úteis do SegFormer/ADE20K

```text
floor
wall
door
stairs
ceiling
column
passage
corridor
path
sidewalk, se disponível
floor mat, se disponível
```

---

## 2. Criar `DetectionPlan`

Crie uma estrutura padronizada para representar quais detectores serão chamados.

Arquivo sugerido:

```text
app/routing/detection_plan.py
```

Campos sugeridos:

```json
{
  "mode": "auto",
  "target_class": null,
  "use_default_yolo": true,
  "use_open_vocab": false,
  "use_semantic_segmentation": false,
  "use_tactile_specialist": false,
  "use_classic_tactile": false,
  "use_ocr": false,
  "use_stair_ramp_heuristics": false,
  "use_local_navigation": false,
  "target_classes": [],
  "poi_candidates": [],
  "reason": []
}
```

---

## 3. Criar ou refatorar `SceneRouter`

Crie ou refatore o `SceneRouter` para usar o `GeneralistSceneAnalyzer`.

Arquivo sugerido:

```text
app/routing/scene_router.py
```

### Regras gerais

#### a) Sempre permitir modo leve

- Usar YOLO padrão para obstáculos comuns;
- Manter profundidade monocular obrigatória nas detecções finais;
- Não rodar especialistas desnecessários.

#### b) Se o `GeneralistSceneAnalyzer` encontrar indício de PORTA

- Ativar especialista/open-vocabulary para `door`, `elevator door`, `entrance` e `exit`;
- Ativar `LocalNavigator` se `target_class="door"`;
- Priorizar mensagens como:
  - “Porta identificada à frente.”
  - “Porta à direita, distância média.”

#### c) Se encontrar indício de ELEVADOR

- Ativar especialista/open-vocabulary para `elevator` e `elevator door`;
- Ativar OCR opcional para procurar textos/símbolos como “elevador”, “elevator”, setas, números ou placas;
- Priorizar mensagens como:
  - “Elevador identificado à frente.”
  - “Possível elevador à direita.”

#### d) Se encontrar indício de ESCADA

- Ativar open-vocabulary para `stairs` e `staircase`;
- Ativar SegFormer/ADE20K para confirmar região estrutural de escada, se disponível;
- Ativar heurísticas simples para degraus, se implementável com OpenCV;
- Escadas próximas devem ter prioridade de segurança;
- Mensagens:
  - “Escada próxima à frente.”
  - “Escada à esquerda.”

#### e) Se encontrar indício de RECEPÇÃO

- Ativar open-vocabulary para `reception desk`, `reception area` e `front desk`;
- Ativar OCR opcional para placas com “recepção”, “reception” ou “atendimento”;
- Mensagens:
  - “Recepção identificada à frente.”
  - “Possível recepção à direita.”

#### f) Se encontrar indício de PISO TÁTIL

- Ativar `TactilePavingDetector`;
- Ativar `ClassicTactileDetector` com OpenCV como fallback;
- Opcionalmente manter open-vocabulary focado em `tactile paving`, `guiding block` e `warning block`;
- Mensagens:
  - “Piso tátil identificado à frente.”
  - “Possível piso tátil à esquerda.”

#### g) Se encontrar indício de RAMPA

- Ativar open-vocabulary para `ramp`, `accessibility ramp` e `wheelchair ramp`;
- Ativar SegFormer para analisar continuidade do chão e inclinação visual, se aplicável;
- Ativar OCR opcional para sinalização de acessibilidade;
- Mensagens:
  - “Rampa identificada à frente.”
  - “Possível rampa acessível à direita.”

---

## 4. Detectores especialistas sugeridos

Implemente ou prepare interfaces para os seguintes especialistas.

### a) `TactilePavingDetector`

Arquivo:

```text
app/detection/tactile_paving_detector.py
```

Responsabilidade:

Detectar piso tátil usando modelo específico configurável, como `best.pt` próprio ou modelo exportado futuramente.

### b) `ClassicTactileDetector`

Arquivo:

```text
app/detection/classic_tactile_detector.py
```

Responsabilidade:

Fallback com OpenCV para possível piso tátil amarelo ou de alto contraste.

Usar:

- HSV;
- contornos;
- validação simples de padrão/textura.

Marcar resultados como baixa ou média confiança, nunca alta por padrão.

### c) `OCRSignDetector`

Arquivo:

```text
app/detection/ocr_sign_detector.py
```

Responsabilidade:

Preparar suporte opcional para OCR em placas de elevador, recepção, saída/entrada e acessibilidade.

Pode usar:

- EasyOCR;
- PaddleOCR;
- Tesseract.

Mas deixe opcional por configuração. Não quebre o projeto se OCR não estiver instalado.

### d) `StairRampHeuristicDetector`

Arquivo:

```text
app/detection/stair_ramp_heuristic_detector.py
```

Responsabilidade:

Preparar heurísticas simples para escadas/rampas usando linhas, bordas e regiões do chão. Essa etapa pode ser básica e experimental.

### e) `SemanticSegmentationDetector`

Arquivo:

```text
app/detection/semantic_segmentation_detector.py
```

Responsabilidade:

Usar SegFormer/ADE20K para identificar regiões como chão, parede, porta, escada e área transitável.

Não precisa substituir o detector principal. Deve ser usado como evidência complementar.

---

## 5. Combinação dos resultados

Atualize ou crie `DetectionMerger`.

Arquivo sugerido:

```text
app/detection/detection_merger.py
```

### Regras

- Combinar detecções do YOLO padrão, YOLOE/YOLO-World, SegFormer, especialistas e heurísticas;
- Remover duplicidades por IoU;
- Preservar `source_model`;
- Preservar `confidence`;
- Marcar `detection_type`:
  - `object_detection`;
  - `semantic_segmentation`;
  - `tactile_specialist`;
  - `ocr`;
  - `heuristic`;
- Quando dois modelos detectarem o mesmo ponto, aumentar a confiança agregada ou marcar como `corroborated=true`;
- Priorizar detecções confirmadas por mais de uma fonte.

### Formato padrão da detecção

```json
{
  "class_name": "door",
  "display_name": "porta",
  "confidence": 0.78,
  "bbox": {
    "x1": 100,
    "y1": 80,
    "x2": 300,
    "y2": 500
  },
  "source_model": "yoloe",
  "detection_type": "object_detection",
  "corroborated": false
}
```

---

## 6. Integração com profundidade monocular

A profundidade monocular continua obrigatória nas detecções finais.

Para cada detecção final, adicionar:

- `depth_score`;
- `depth_label`;
- `position`.

Exemplo:

```json
{
  "class_name": "door",
  "display_name": "porta",
  "confidence": 0.82,
  "position": "à frente",
  "depth_label": "distância média",
  "source_model": "yoloe",
  "corroborated": true
}
```

---

## 7. Prioridade semântica

Atualize `NavigationPriority` para favorecer:

### Prioridade máxima

- Obstáculo muito próximo à frente;
- Escada muito próxima;
- Pessoa muito próxima no centro.

### Alta prioridade

- Piso tátil;
- Porta;
- Elevador;
- Rampa;
- Escada;
- Recepção;
- Entrada/saída;
- Corrimão;
- Sinalização de acessibilidade.

### Baixa prioridade

- Mochila;
- Bolsa;
- Mala;
- Garrafa;
- Celular;
- Laptop;
- Acessórios junto de pessoas.

---

## 8. Modos de operação

Atualize o pipeline para aceitar os seguintes modos.

### `mode="fast"`

- YOLO padrão;
- Sem generalistas pesados;
- Foco em latência.

### `mode="poi"`

- YOLO padrão;
- YOLOE ou YOLO-World;
- SegFormer opcional;
- Especialistas conforme pontos encontrados.

### `mode="tactile"`

- `TactilePavingDetector`;
- `ClassicTactileDetector`;
- Open-vocabulary focado em piso tátil;
- Profundidade monocular.

### `mode="auto"`

- `GeneralistSceneAnalyzer` decide o plano;
- Não rodar todos os modelos sempre;
- Chamar especialistas apenas quando houver indício ou `target_class`.

---

## 9. Endpoint `/detect`

Atualize o endpoint para aceitar:

- `mode=fast|poi|tactile|auto`;
- `target_class` opcional;
- `use_open_vocab=true/false`;
- `use_semantic_segmentation=true/false`;
- `use_tactile_specialist=true/false`;
- `use_classic_tactile=true/false`;
- `use_ocr=true/false`.

### Exemplos

```text
POST /detect?mode=auto
POST /detect?mode=auto&target_class=door
POST /detect?mode=poi&target_class=elevator
POST /detect?mode=tactile
POST /detect?mode=poi&use_semantic_segmentation=true
```

### Retorno esperado

```json
{
  "message": "...",
  "detection_plan": {},
  "generalist_findings": [],
  "detections": [],
  "navigation": {}
}
```

---

## 10. Mensagens esperadas

Gerar mensagens curtas, úteis e adequadas para áudio:

- “Porta identificada à frente, distância média.”
- “Elevador à direita.”
- “Escada próxima à frente. Atenção.”
- “Recepção identificada à esquerda.”
- “Piso tátil identificado à frente.”
- “Possível piso tátil à direita.”
- “Rampa identificada à frente.”
- “Obstáculo próximo à frente. Pare.”
- “Alvo não encontrado. Gire lentamente para procurar.”

Regras:

- Não listar todos os objetos detectados.
- Não falar mochilas, bolsas e acessórios junto de pessoas.
- Não prometer navegação global.

---

## 11. Configuração

Centralize as configurações em `app/config.py` ou arquivo equivalente:

```python
OPEN_VOCAB_MODEL_PRIORITY = ["yoloe", "yolo_world"]
ENABLE_SEMANTIC_SEGMENTATION = False
ENABLE_OCR = False
ENABLE_TACTILE_SPECIALIST = True
ENABLE_CLASSIC_TACTILE = True
DEFAULT_MODE = "auto"
OPEN_VOCAB_PROMPTS = [...]
POI_CLASSES = [...]
ACCESSIBILITY_CLASSES = [...]
```

---

## 12. Scripts de teste

Crie ou atualize:

```text
scripts/test_generalist_scene_analyzer.py
scripts/test_scene_router.py
scripts/test_poi_detection.py
scripts/test_tactile_detection.py
scripts/benchmark_routed_detection.py
```

O benchmark deve comparar:

- `fast`;
- `poi`;
- `tactile`;
- `auto`;
- `auto` com OCR;
- `auto` com SegFormer.

### Métricas

- Tempo total;
- Modelos chamados;
- Pontos de interesse detectados;
- Piso tátil detectado;
- Detecções corroboradas por mais de uma fonte;
- Mensagem final gerada.

Salvar em:

```text
results/evaluation/routed_detection_benchmark.csv
```

---

## 13. Documentação

Crie:

```text
docs/routed_detection_architecture.md
```

Explicando:

- Por que existe o `GeneralistSceneAnalyzer`;
- Papel do YOLOE/YOLO-World;
- Papel do SegFormer/ADE20K;
- Papel dos especialistas;
- Quando cada especialista é chamado;
- Como testar cada modo;
- Limitações conhecidas;
- Por que o sistema não roda todos os modelos sempre;
- Como no futuro substituir especialistas por modelos treinados próprios.

---

## 14. Requisitos finais

Ao terminar:

1. Liste os arquivos criados e alterados.
2. Explique como testar cada modo.
3. Mostre exemplos de JSON.
4. Informe quais dependências novas foram adicionadas.
5. Informe quais modelos são opcionais ou fallback.
6. Garanta que o pipeline continue funcionando mesmo se YOLOE, YOLO-World, SegFormer ou OCR não estiverem disponíveis.
