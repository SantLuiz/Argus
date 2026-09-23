# Cronograma de mudanças para foco em pontos de interesse, acessibilidade e navegação local

Este documento substitui os prompts longos a partir da etapa 5. Use-o como uma instrução compacta para o agente de código continuar o MVP sem repetir tarefas que já foram feitas.

## Estado atual assumido

Assuma que o projeto já possui, mesmo que em versão inicial:

- backend Python organizado;
- detecção com YOLO ou modelo compatível;
- estimativa monocular de profundidade obrigatória;
- classificação simples de posição horizontal;
- geração inicial de mensagem em português;
- pós-processamento ou regra equivalente para reduzir foco em mochilas, bolsas e objetos carregados por pessoas;
- estrutura inicial para priorização de pontos de interesse e elementos de acessibilidade.

Não refaça essas bases do zero. Apenas ajuste, integre e evolua.

## Objetivo do próximo ciclo

Transformar a detecção genérica em uma detecção orientada à navegação assistida, priorizando:

1. pontos de interesse indoor;
2. elementos de acessibilidade;
3. obstáculos relevantes no caminho;
4. navegação local simples até um alvo detectado;
5. preparação para treinamento/fine-tuning com dataset mais adequado.

O sistema não deve se comportar como um detector geral de objetos. Ele deve responder à pergunta: **“o que ajuda o usuário a se orientar com segurança neste ambiente?”**

---

# Cronograma incremental

## Fase 1 — Consolidar classes e prioridades

### Objetivo
Criar uma tabela central de classes do projeto, separando classes úteis, classes de acessibilidade, obstáculos e classes de baixa prioridade.

### Alterações esperadas

Criar ou revisar:

- `app/detection/class_mapper.py`
- `app/guidance/navigation_priority.py`
- `app/guidance/accessibility_rules.py`

### Classes prioritárias

#### Pontos de interesse principais

- `door` → porta
- `corridor` / `hallway` / `passage` → corredor/passagem
- `stairs` / `stair` / `downstair` / `upstair` / `step` → escada/degrau
- `elevator` → elevador
- `reception` → recepção
- `entrance` → entrada
- `exit` → saída

#### Elementos de acessibilidade

- `ramp` → rampa
- `curb_ramp` → rampa de acesso
- `wheelchair_ramp` → rampa acessível
- `handrail` → corrimão
- `tactile_paving` → piso tátil
- `tactile-paving` → piso tátil
- `tactile paving` → piso tátil
- `left-turn tactile paving` → piso tátil direcional à esquerda
- `right-turn tactile paving` → piso tátil direcional à direita
- `stop tactile paving` → piso tátil de alerta/parada
- `straight tactile paving` → piso tátil direcional
- `accessibility_sign` → sinalização de acessibilidade
- `disability sign` → sinalização de acessibilidade
- `accessible_entrance` → entrada acessível

#### Obstáculos relevantes

- `person` → pessoa
- `chair` → cadeira
- `table` / `dining table` → mesa
- `column` → coluna
- `wall` → parede
- `obstacle` / `objects` → obstáculo

#### Baixa prioridade

- `backpack`
- `handbag`
- `suitcase`
- `bottle`
- `cup`
- `cell phone`
- `laptop`
- `book`
- `umbrella`

### Critério de conclusão

Toda detecção deve sair do pipeline com campos padronizados:

```json
{
  "raw_class_name": "door",
  "normalized_class": "door",
  "label_pt": "porta",
  "category": "poi",
  "priority_score": 0.0
}
```

---

## Fase 2 — Melhorar o gerador de mensagens

### Objetivo
Reduzir mensagens longas e inúteis. A saída deve ser curta, segura e adequada para áudio.

### Alterações esperadas

Revisar:

- `app/guidance/message_generator.py`

### Regras

1. Não listar todos os objetos detectados.
2. Priorizar no máximo duas informações por mensagem.
3. Obstáculo muito próximo no centro da imagem tem prioridade máxima.
4. Elementos de acessibilidade devem ser mencionados quando úteis.
5. Pontos de interesse devem ser mencionados antes de objetos genéricos.
6. Objetos de baixa prioridade só devem aparecer se estiverem isolados, muito próximos e no caminho.
7. Usar sempre distância relativa, não distância métrica absoluta.

### Exemplos bons

- “Porta à frente, distância média.”
- “Obstáculo próximo à frente.”
- “Pessoa próxima à esquerda.”
- “Elevador à direita.”
- “Piso tátil identificado à frente.”
- “Corrimão à direita.”
- “Caminho livre em direção à porta.”

### Exemplos ruins

- “Pessoa, mochila, bolsa, garrafa e celular detectados.”
- “Backpack próximo.”
- “Foram encontrados 13 objetos.”
- “Objeto detectado com confiança 0.84.”

### Critério de conclusão

O endpoint ou script principal deve retornar uma mensagem de guidance baseada em prioridade semântica, proximidade, posição e risco.

---

## Fase 3 — Criar modos de operação

### Objetivo
Separar o comportamento do sistema em modo exploração e modo navegação.

### Alterações esperadas

Criar ou revisar:

- `app/pipeline.py`
- `app/navigation/local_navigator.py`
- `app/navigation/target_selector.py`
- `app/navigation/navigation_state.py`
- `app/main.py`

### Modo 1 — Exploration mode

Uso: quando o usuário ainda não escolheu destino.

Comportamento:

- informar os pontos de interesse mais relevantes;
- destacar elementos de acessibilidade;
- alertar obstáculos próximos;
- não tentar guiar até um alvo específico.

Exemplo:

```text
“Identifiquei uma porta à frente, uma escada à direita e piso tátil próximo.”
```

### Modo 2 — Navigation mode

Uso: quando o usuário selecionou um destino, por exemplo `door`, `elevator` ou `reception`.

Comportamento:

- buscar o melhor alvo da classe selecionada;
- orientar o usuário em direção ao alvo;
- interromper a orientação se houver obstáculo próximo no centro;
- não prometer rota completa, apenas orientação local baseada no frame atual.

Exemplos:

```text
“Porta à frente, siga em frente.”
“Elevador à esquerda, vire levemente à esquerda.”
“Alvo não encontrado. Gire lentamente para procurar.”
“Obstáculo próximo à frente. Pare.”
```

### API esperada

Permitir parâmetros opcionais:

```text
POST /detect?mode=exploration
POST /detect?mode=navigation&target_class=door
POST /detect?mode=navigation&target_class=elevator
```

### Retorno esperado

```json
{
  "message": "Porta à frente, siga em frente.",
  "mode": "navigation",
  "navigation": {
    "target_class": "door",
    "target_found": true,
    "direction": "forward",
    "distance_label": "distância média"
  },
  "detections": []
}
```

### Critério de conclusão

O pipeline deve conseguir funcionar nos dois modos sem duplicar lógica.

---

## Fase 4 — Implementar navegação local simples

### Objetivo
Criar uma navegação inicial até ponto de interesse usando apenas detecção, posição horizontal e profundidade monocular.

### Não fazer

- Não implementar SLAM.
- Não implementar mapa 3D.
- Não implementar localização global.
- Não prometer rota completa.
- Não depender de Flutter.

### Como escolher o alvo

Para `target_class`, escolher a detecção com melhor combinação de:

- classe normalizada compatível;
- maior confiança;
- maior prioridade semântica;
- posição mais central;
- estabilidade entre frames, se já houver histórico;
- profundidade coerente;
- tamanho da bounding box.

### Direções permitidas

- `slight_left` → “vire levemente à esquerda”
- `forward` → “siga em frente”
- `slight_right` → “vire levemente à direita”
- `stop` → “pare”
- `search` → “gire lentamente para procurar”

### Regra de segurança

Se houver obstáculo muito próximo no centro, sobrescrever a navegação.

Exemplo:

- Não dizer: “Siga em frente até a porta.”
- Dizer: “Obstáculo próximo à frente. Pare.”

### Critério de conclusão

Com `target_class=door`, o sistema deve retornar uma orientação local coerente quando uma porta estiver visível.

---

## Fase 5 — Avaliação e benchmark

### Objetivo
Medir se o sistema melhorou para navegação, não apenas se detecta muitos objetos.

### Alterações esperadas

Criar:

- `scripts/evaluate_navigation_detection.py`
- `results/evaluation/navigation_detection_report.csv`

### Entrada

Uma pasta de imagens de teste.

### Saída CSV

Campos obrigatórios:

- `image_name`
- `raw_detection_count`
- `filtered_detection_count`
- `poi_detected`
- `accessibility_detected`
- `obstacles_detected`
- `suppressed_generic_objects`
- `message`
- `detection_time_ms`
- `depth_time_ms`
- `total_time_ms`

### Resumo no terminal

- total de imagens;
- média de objetos brutos;
- média de objetos filtrados;
- classes mais detectadas;
- classes mais suprimidas;
- tempo médio por imagem;
- mensagens mais comuns.

### Critério de conclusão

O relatório deve permitir comparar o detector genérico contra o pipeline orientado à navegação.

---

# Recomendação de datasets e estratégia de treinamento

## Diagnóstico

O YOLO treinado em COCO é útil para pessoas, cadeiras e mesas, mas não é suficiente para os pontos de interesse do projeto. Classes como porta, elevador, corrimão, rampa e piso tátil exigem dataset mais específico ou fine-tuning.

## Recomendação prática

### Dataset principal recomendado para início

**Roboflow Universe — blind_aid_yolov8n**

Motivo:

- possui cerca de 7,9 mil imagens;
- é voltado a auxílio visual;
- inclui classes úteis ao projeto, como `door`, `elevator`, `escalator`, `handrail`, `downstair` e variações de `tactile paving`;
- já está em formato adequado para treinamento/exportação em YOLO;
- é um bom ponto de partida para fine-tuning, mesmo exigindo revisão de qualidade das anotações.

Uso recomendado:

1. Baixar/exportar em formato YOLO.
2. Verificar classes disponíveis.
3. Selecionar somente classes úteis ao ARGUS.
4. Treinar um modelo leve, como YOLOv8n ou YOLO11n.
5. Testar em imagens internas reais do campus.
6. Complementar com dados próprios se houver baixa precisão.

### Dataset complementar para obstáculos indoor

**Roboflow Universe — Indoor Obstacles**

Motivo:

- possui cerca de 6,3 mil imagens;
- inclui classes como `Chair`, `Table`, `Door`, `Person`, `Stair` e `objects`;
- ajuda a reforçar obstáculos e pontos internos básicos.

Uso recomendado:

- utilizar como complemento, não como dataset principal;
- revisar nomes de classes e normalizar para o padrão do projeto.

### Dataset específico para piso tátil

**Roboflow Universe — tactile_paving**

Motivo:

- possui 439 imagens;
- licença CC BY 4.0;
- tem classes específicas ligadas a piso tátil, como `GO` e `STOP`;
- útil para validar a ideia de detecção de piso tátil, embora seja pequeno.

Uso recomendado:

- usar como dataset auxiliar;
- converter classes para algo mais semântico no projeto, como `tactile_paving_directional` e `tactile_paving_warning`;
- não depender apenas dele para generalização.

### Dataset/pesquisa para piso tátil em primeira pessoa

**Tenji10K**

Motivo:

- dataset de piso tátil com cerca de 10 mil frames em primeira pessoa;
- foi proposto justamente para detecção e rastreamento de piso tátil;
- pode ser muito alinhado ao caso de uso, caso esteja acessível para download.

Uso recomendado:

- verificar disponibilidade real dos arquivos;
- usar como referência acadêmica e, se possível, como base para treino/avaliação.

### Dataset para segmentação de cena e caminho

**ADE20K**

Motivo:

- dataset de segmentação semântica com cenas internas e externas;
- possui anotações em nível de pixel;
- é útil para futuro módulo de caminho livre/corredor/piso/parede/porta;
- não é a melhor primeira opção para YOLO de bounding boxes, mas é útil para segmentação.

Uso recomendado:

- deixar para uma etapa posterior;
- avaliar se um modelo de segmentação treinado em ADE20K pode ajudar a identificar piso, parede, passagem e região livre.

### Rampas

A detecção de rampas é o ponto com menor cobertura pública clara. Existem datasets e pesquisas voltadas a `curb ramp`, mas normalmente em ambiente externo e imagens de rua. Para o escopo indoor/campus, a recomendação é:

1. iniciar com classes de datasets públicos que já tenham `ramp`, `curb ramp` ou `wheelchair ramp`, quando disponíveis;
2. coletar imagens próprias de rampas reais no campus;
3. anotar como `ramp` ou `wheelchair_ramp`;
4. treinar com poucas classes, evitando um dataset grande e confuso.

## Classes essenciais para o primeiro fine-tuning

Para economizar esforço, treinar primeiro apenas:

- `door`
- `person`
- `stairs` / `step`
- `elevator`
- `handrail`
- `tactile_paving`
- `ramp`
- `chair`
- `table`
- `obstacle`

Não começar com muitas classes. Aumentar depois.

## Regras de anotação

1. Pessoa com mochila deve ser anotada como `person`; a mochila não deve ser anotada separadamente, salvo se estiver isolada e criando obstáculo.
2. Porta parcialmente aberta ainda deve ser anotada como `door`.
3. Piso tátil deve ser anotado mesmo quando aparecer parcialmente.
4. Corrimão deve ser anotado quando for relevante para orientação ou acessibilidade.
5. Rampa deve ser anotada como `ramp`; se for claramente acessível para cadeira de rodas, usar `wheelchair_ramp` apenas se essa distinção for útil.
6. Corredor/passagem pode ser mais adequado para segmentação do que detecção por bounding box.
7. Evitar classes muito vagas se elas não forem úteis para a mensagem de áudio.

## Estratégia de treino recomendada

1. Começar com YOLOv8n ou YOLO11n.
2. Usar modelo pré-treinado como base.
3. Treinar no Colab.
4. Exportar `best.pt`.
5. Substituir o modelo atual no backend.
6. Comparar contra o modelo genérico usando `evaluate_navigation_detection.py`.
7. Registrar métricas em `docs/resultados_mvp.md`.

## Métricas mínimas

- `precision`
- `recall`
- `mAP50`
- `mAP50-95`
- matriz de confusão
- tempo médio por imagem
- qualidade subjetiva da mensagem gerada

---

# Prompt único para usar no Codex

Copie e cole o prompt abaixo no Codex depois de adicionar este arquivo ao repositório.

```text
Leia primeiro o arquivo docs/08_CRONOGRAMA_MUDANCAS_POI_DATASETS.md e use-o como fonte principal para o próximo ciclo de implementação.

Não repita a criação da estrutura básica do backend, detector YOLO, estimativa monocular de profundidade, pós-processamento inicial ou regras já existentes. Assuma que essas partes já existem e devem apenas ser integradas, ajustadas ou refatoradas quando necessário.

Implemente o cronograma incremental descrito no documento, seguindo esta ordem:

1. consolidar classes e prioridades;
2. melhorar o gerador de mensagens;
3. criar modos exploration/navigation;
4. implementar LocalNavigator para navegação local simples;
5. criar script de avaliação e benchmark;
6. preparar o projeto para aceitar um modelo YOLO customizado treinado com datasets de pontos de interesse e acessibilidade.

Mantenha o foco em ambiente interno, pontos de interesse, elementos de acessibilidade e orientação por áudio em português brasileiro. Não implemente Flutter agora. Não implemente SLAM, mapa 3D ou navegação global.

Ao final, liste os arquivos alterados, explique as decisões técnicas e mostre exemplos de uso do endpoint /detect nos modos exploration e navigation.
```
