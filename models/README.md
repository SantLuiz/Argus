# Modelos locais

Esta pasta guarda os pesos e caches locais usados pelo backend ARGUS. Os arquivos grandes nao entram no Git.

Execute, a partir da raiz:

```powershell
.\scripts\prepare_models.ps1
```

Estrutura esperada:

```text
models/
├── yolo/
│   ├── yolov8n.pt
│   ├── yoloe-11s-seg.pt
│   └── yolov8s-world.pt
└── torch/
    └── hub/
```

O backend usa `models/yolo` para Ultralytics e `models/torch` como `TORCH_HOME` do MiDaS. Mantenha essa pasta local antes de demonstracoes para evitar download durante a primeira inferencia.
