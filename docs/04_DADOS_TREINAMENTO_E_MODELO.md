# 04 - Dados, treinamento e modelo

## Fontes de dados

A IC pode usar datasets públicos e, quando necessário, um pequeno conjunto próprio de imagens de teste.

Fontes principais:

- COCO: dataset amplo para detecção e reconhecimento de objetos.
- Open Images: dataset público com grande variedade de classes.
- Roboflow: ferramenta opcional para anotação, organização, exportação e versionamento de datasets.
- Imagens próprias controladas: fotos de ambientes internos, desde que sem exposição indevida de pessoas ou dados sensíveis.

## Estratégia recomendada para a IC

A abordagem deve ser incremental:

1. Começar com modelo pré-treinado para validar o fluxo ponta a ponta.
2. Testar imagens internas simples.
3. Registrar quais classes são detectadas corretamente e quais não são.
4. Caso necessário, criar pequena base própria no Roboflow.
5. Treinar ou ajustar um modelo leve apenas se isso contribuir para a demonstração.

## Classes de interesse

Classes úteis para a IC:

- pessoa;
- porta;
- cadeira;
- mesa;
- escada/degrau;
- obstáculo genérico;
- mochila/caixa/objeto no chão, se presente;
- corredor/passagem, se houver método adequado.

Nem todas essas classes precisam estar disponíveis no primeiro modelo. Algumas podem ser tratadas como extensão futura.

## Pré-processamento

O relatório semestral descreve um pipeline de tratamento de imagens que deve orientar o protótipo e a documentação.

Etapas recomendadas:

1. Ler imagem digital.
2. Converter para RGB.
3. Redimensionar para tamanho compatível com o modelo.
4. Aplicar redução de ruído quando adequado, como Gaussian Blur.
5. Aplicar realce de contraste quando adequado, como CLAHE.
6. Normalizar valores de pixel, por exemplo de 0 a 1.
7. Enviar para inferência.
8. Armazenar resultado e metadados do teste.

Nem toda imagem precisa passar por todas as etapas. O pipeline deve ser comparado experimentalmente para verificar se melhora ou prejudica a detecção.

## Estimativa monocular de profundidade

A estimativa monocular de profundidade é obrigatória no protótipo da IC. Ela deve complementar a detecção de objetos para permitir mensagens que indiquem proximidade ou distância aproximada até obstáculos e elementos relevantes.

Modelos possíveis:

- MiDaS;
- Depth Anything;
- outro modelo monocular leve compatível com Python/PyTorch/TensorFlow.

Estratégia recomendada:

1. Rodar o modelo de profundidade na mesma imagem usada para detecção.
2. Gerar um mapa de profundidade relativo.
3. Usar a caixa delimitadora de cada detecção para calcular um valor médio ou mediano de profundidade daquela região.
4. Converter o valor em categorias simples, por exemplo: `próximo`, `médio` e `distante`.
5. Registrar tempo de inferência e exemplos de erro.

A IC não deve tratar esses valores como distância exata em metros sem calibração. Para o feedback auditivo, a forma mais segura é usar termos aproximados: "próximo", "a média distância" e "mais distante".

## Modelos possíveis

### Opção 1 - Modelo pré-treinado

Uso recomendado para primeira prova de conceito.

Vantagens:

- implementação rápida;
- não exige dataset próprio inicialmente;
- permite testar o fluxo completo.

Limitações:

- pode não detectar classes específicas de acessibilidade;
- pode errar em ambientes internos específicos;
- pode não reconhecer portas, corredores ou elementos arquitetônicos dependendo do dataset.

### Opção 2 - YOLO leve

Modelo sugerido quando for necessário treinar ou ajustar detecção.

Possíveis versões:

- YOLOv8n;
- YOLO11n;
- outro modelo leve compatível com Ultralytics.

Vantagens:

- boa velocidade;
- treinamento simplificado;
- compatibilidade com exportação futura;
- comunidade ampla.

### Opção 3 - TensorFlow/PyTorch

Usar quando a tarefa exigir maior flexibilidade experimental ou quando for necessário alinhar o protótipo à documentação inicial da IC.

## Treinamento

Ambiente recomendado:

- Google Colab para treinamento experimental;
- GPU gratuita quando disponível;
- notebooks versionados no repositório;
- exportação de métricas e pesos do modelo.

Boas práticas:

- registrar dataset usado;
- registrar classes;
- registrar tamanho das imagens;
- salvar arquivo de configuração;
- salvar métricas;
- registrar modelo de profundidade utilizado;
- registrar limitações do treinamento e da estimativa monocular;
- não prometer desempenho superior ao que foi testado.

## Métricas mínimas

Para a IC, usar métricas simples e compreensíveis:

- confiança média das detecções;
- tempo de inferência da detecção;
- tempo de inferência da profundidade monocular;
- quantidade de objetos detectados por imagem;
- distribuição de proximidade dos objetos detectados;
- acertos e erros em amostra manual;
- exemplos qualitativos de saída por áudio.

Métricas mais formais, se houver treinamento:

- precision;
- recall;
- mAP;
- IoU;
- matriz de confusão por classe.

## Registro dos experimentos

Criar uma pasta `results/` com arquivos como:

```text
results/
├── experimento_001/
│   ├── README.md
│   ├── imagens_teste.txt
│   ├── metricas.json
│   └── exemplos_saida.md
└── experimento_002/
```

Exemplo de `metricas.json`:

```json
{
  "experiment": "experimento_001",
  "model": "yolov8n-pretrained",
  "dataset": "COCO",
  "num_images": 20,
  "avg_detection_time_ms": 310,
  "avg_depth_time_ms": 180,
  "depth_model": "midas-small",
  "notes": "Teste preliminar em imagens internas. Desempenho bom para pessoa e cadeira, limitado para porta. Profundidade usada apenas como estimativa relativa."
}
```

## Limitações esperadas

Registrar com clareza:

- variação de iluminação afeta o resultado;
- objetos parcialmente ocultos podem não ser detectados;
- classes ausentes no dataset não serão reconhecidas corretamente;
- a posição esquerda/centro/direita é uma aproximação baseada na caixa delimitadora;
- a distância/proximidade é uma estimativa aproximada baseada em profundidade monocular;
- distância real em metros não deve ser afirmada sem calibração e validação;
- o protótipo não substitui bengala, cão-guia ou tecnologias assistivas consolidadas.
