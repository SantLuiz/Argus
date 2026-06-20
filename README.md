# Backend Python - ARGUS IC

Backend inicial do ARGUS IC para demonstrar o fluxo:

```text
imagem -> deteccao -> profundidade monocular relativa -> mensagem -> audio no app
```

Esta primeira versao usa servicos simulados e determinísticos para manter o prototipo simples. Os pontos de troca para modelos reais ficam em `app/vision/detection.py` e `app/vision/depth.py`.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Endpoints:

- `GET /health`
- `POST /detect` com campo de arquivo `image`

Exemplo com PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/detect" `
  -Method Post `
  -Form @{ image = Get-Item ".\imagem_teste.jpg" }
```

Exemplo com cURL:

```bash
curl -X POST "http://127.0.0.1:8000/detect" -F "image=@imagem_teste.jpg"
```

## Teste local por script

```bash
python scripts/test_detect_image.py caminho/para/imagem.jpg
```

## Testes automatizados

```bash
pytest
```

## Modelo customizado para acessibilidade

O pipeline reconhece classes de acessibilidade como `tactile_paving`, `handrail`, `wheelchair_ramp`, `accessible_entrance`, `elevator`, `stairs` e `step` quando essas classes forem retornadas pelo modelo de deteccao.

O YOLO generico treinado em COCO provavelmente nao detecta esses elementos com boa precisao. Para esse caso, crie um dataset especifico, por exemplo no Roboflow, treine um modelo customizado e salve os pesos como:

```text
models/best.pt
```

Para usar o modelo customizado:

```bash
set ARGUS_YOLO_MODEL_PATH=models/best.pt
uvicorn app.main:app --reload
```

Mais detalhes em `docs/dataset_accessibilidade.md`.

## Observacao sobre profundidade

A profundidade retornada nesta base inicial e uma estimativa relativa simulada. Ela nao representa distancia em metros. A substituicao por MiDaS, Depth Anything ou outro modelo monocular deve preservar a mesma ideia de saida: valor relativo e categoria `near`, `medium` ou `far`.
