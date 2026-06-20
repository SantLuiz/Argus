# 03 - Arquitetura técnica recomendada

## Visão geral

A arquitetura da IC deve ser simples, modular e fácil de explicar no relatório. O objetivo não é construir uma plataforma de produção, mas uma estrutura suficiente para demonstrar o fluxo completo:

> câmera/imagem -> backend Python -> detecção + profundidade monocular -> texto -> áudio.

## Componentes principais

```text
+------------------+        HTTP/JSON        +-----------------------+
| App Flutter      |  ---------------------> | Backend Python        |
|                  |                         | FastAPI sugerido      |
| - câmera/imagem  | <---------------------  | - pré-processamento   |
| - acessibilidade |      resposta JSON      | - inferência          |
| - TTS            |                         | - profundidade mono.  |
|                  |                         | - geração de mensagem |
+------------------+                         +-----------------------+
                                              |
                                              v
                                    +---------------------+
                                    | Modelo de visão     |
                                    | COCO/Open Images    |
                                    | YOLO/TensorFlow     |
                                    | MiDaS/Depth Anything|
                                    +---------------------+
```

## Frontend Flutter

O frontend deve ser responsável por:

- capturar imagem da câmera ou selecionar imagem de teste;
- enviar a imagem para o backend Python;
- receber a resposta com as detecções e o texto final;
- reproduzir o texto por áudio usando TTS;
- oferecer uma interface simples e acessível.

Pacotes Flutter possíveis:

- `camera`: captura de imagem/câmera;
- `http` ou `dio`: comunicação com a API;
- `flutter_tts`: síntese de voz no dispositivo;
- `permission_handler`: permissões de câmera e microfone, se necessário;
- recursos nativos de acessibilidade do Flutter, como `Semantics`.

## Backend Python

O backend deve ser responsável por:

- receber imagens;
- validar formato e tamanho;
- aplicar pré-processamento;
- executar inferência de detecção de objetos;
- executar estimativa monocular de profundidade;
- associar profundidade estimada às caixas dos objetos detectados;
- transformar detecções e proximidade em descrição textual;
- retornar uma resposta JSON simples.

Framework sugerido:

- FastAPI, por ser simples, leve, bem documentado e adequado a APIs Python.

Bibliotecas principais:

- OpenCV: leitura, conversão, redimensionamento e operações de imagem;
- scikit-image: realce, segmentação e extração de características, se necessário;
- NumPy: manipulação numérica;
- TensorFlow ou PyTorch: execução/treinamento de modelos;
- Ultralytics YOLO: alternativa prática para detecção de objetos;
- MiDaS, Depth Anything ou modelo equivalente: estimativa monocular de profundidade;
- Pillow: manipulação auxiliar de imagens.

## Endpoints sugeridos

### `GET /health`

Verifica se o backend está ativo.

Resposta esperada:

```json
{
  "status": "ok",
  "project": "ARGUS IC"
}
```

### `POST /detect`

Recebe uma imagem e retorna detecções e uma frase pronta para áudio.

Resposta sugerida:

```json
{
  "detections": [
    {
      "class_name": "pessoa",
      "confidence": 0.88,
      "bbox": [120, 80, 300, 420],
      "zone": "centro",
      "depth": {
        "relative_value": 0.34,
        "proximity": "near",
        "label_pt": "próximo"
      },
      "priority": "alta"
    }
  ],
  "message": "Pessoa próxima à frente, na região central da imagem.",
  "processing_time_ms": {
    "detection_ms": 245,
    "depth_ms": 180,
    "total_ms": 425
  }
}
```

### `POST /describe`

Opcional. Recebe uma imagem e retorna uma descrição textual mais ampla. Na IC, pode ser uma descrição baseada apenas nas detecções locais, sem necessidade de modelo multimodal externo.

Resposta sugerida:

```json
{
  "message": "Ambiente interno com uma pessoa ao centro e uma mesa à direita."
}
```

## Estimativa monocular de profundidade

A estimativa monocular de profundidade é um módulo obrigatório da arquitetura. Ela deve gerar uma noção aproximada de distância a partir de uma única imagem, sem exigir LiDAR, câmera estéreo ou sensores dedicados.

Fluxo recomendado:

1. Receber a mesma imagem usada na detecção.
2. Gerar um mapa de profundidade com modelo monocular.
3. Para cada caixa delimitadora detectada, extrair a profundidade média ou mediana da região correspondente.
4. Converter o valor relativo em categoria simples: `próximo`, `médio` ou `distante`.
5. Enviar essa categoria para o módulo de geração de mensagem.

Observações importantes:

- a saída da profundidade monocular deve ser tratada como estimativa relativa/aproximada;
- não afirmar distância exata em metros sem calibração;
- registrar o modelo usado, tempo de inferência e limitações;
- manter a implementação simples o suficiente para a IC.

## Geração da mensagem auditiva

A geração de mensagem deve ser simples e objetiva. Evitar excesso de detalhes para não sobrecarregar o usuário.

Regras possíveis:

- Priorizar classes críticas: pessoa, obstáculo, escada/degrau, porta.
- Informar posição aproximada: esquerda, centro, direita.
- Informar distância sempre como estimativa aproximada derivada da profundidade monocular, salvo se houver calibração específica.
- Limitar a frase a uma ou duas sentenças.

Exemplos:

- "Obstáculo próximo à frente, ligeiramente à direita."
- "Porta detectada no centro da imagem, a uma distância média."
- "Mesa distante à esquerda e pessoa ao fundo."

## Banco de dados

Para a IC, banco de dados não é obrigatório. Se necessário, usar SQLite para registrar:

- imagem processada ou caminho do arquivo;
- data/hora;
- classes detectadas;
- confiança média;
- categoria de profundidade/proximidade;
- tempo de processamento;
- mensagem gerada.

PostgreSQL pode ser citado como alternativa futura ou uso em hospedagem, mas não deve ser obrigatório.

## Hospedagem

Durante a IC, o backend pode rodar localmente. Para demonstração remota, usar:

- Oracle Cloud Infrastructure Always Free;
- Docker para empacotar backend;
- GitHub para versionamento;
- Google Colab para treinamento e experimentos com modelos.

## Organização sugerida do repositório

```text
argus-ic/
├── AGENTS.md
├── README.md
├── app_flutter/
│   └── ...
├── backend_python/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── vision/
│   │   └── schemas/
│   ├── models/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── notebooks/
│   └── treinamento_colab.ipynb
├── datasets/
│   └── README.md
├── docs/
│   └── ...
└── results/
    └── README.md
```

## Regra de simplicidade

Se uma tarefa puder ser resolvida com um endpoint, um modelo de detecção, um modelo de profundidade monocular e uma mensagem de áudio, não criar uma arquitetura maior. A arquitetura deve servir à IC, não substituir o foco acadêmico por engenharia excessiva.
