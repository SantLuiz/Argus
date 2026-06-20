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
