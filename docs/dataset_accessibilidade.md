# Dataset de acessibilidade para ARGUS IC

O suporte a elementos de acessibilidade no backend ja existe no mapeamento semantico do pipeline, mas o modelo YOLO generico treinado em COCO provavelmente nao detecta essas classes com boa precisao.

Classes previstas:

- `ramp` -> rampa
- `handrail` -> corrimao
- `tactile_paving` -> piso tatil
- `accessibility_sign` -> sinalizacao de acessibilidade
- `wheelchair_ramp` -> rampa acessivel
- `accessible_entrance` -> entrada acessivel
- `elevator` -> elevador
- `stairs` -> escada
- `step` -> degrau

## Recomendacao para treinamento

Para detectar esses elementos de forma confiavel, recomenda-se criar um dataset proprio de ambientes internos, com imagens controladas e anonimizadas quando houver pessoas.

Fluxo sugerido:

1. Coletar imagens de corredores, entradas, escadas, elevadores e areas com recursos de acessibilidade.
2. Anotar as classes em uma ferramenta como Roboflow.
3. Exportar o dataset em formato compativel com YOLO.
4. Treinar um modelo leve, como YOLOv8n ou YOLO11n, no Google Colab.
5. Exportar o melhor peso como `models/best.pt`.
6. Rodar o backend com `ARGUS_YOLO_MODEL_PATH=models/best.pt`.

## Limites

Mesmo com modelo customizado, a saida deve continuar sendo tratada como apoio experimental. O ARGUS IC nao deve prometer navegacao autonoma, distancia exata ou seguranca operacional sem validacao formal.
