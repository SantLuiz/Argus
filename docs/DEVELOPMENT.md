# Desenvolvimento local

Execute os comandos a partir da raiz do repositório, exceto quando indicado `cd app_flutter`. O ambiente de referência é Windows/PowerShell com Python 3.12. Em Linux/macOS, o Python do ambiente virtual fica em `.venv/bin/python`; os scripts `.ps1` exigem PowerShell.

## Backend

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\prepare_models.ps1
.\scripts\run_backend_mvp.ps1 -SkipDependencyInstall
```

O script procura `.venv`, depois tenta criar o ambiente com o runtime local do Codex ou Python do PATH. Ativa o perfil MVP, roda `pytest tests` e inicia Uvicorn. Não é necessário instalar o Codex em outra máquina; Python no PATH é suficiente.

| Opção | Efeito |
|---|---|
| `-HostAddress 0.0.0.0 -Port 8000` | Aceita conexões pela rede local nessa porta |
| `-SkipDependencyInstall` | Reutiliza dependências já instaladas |
| `-SkipTests` | Pula os testes; use apenas depois de validá-los separadamente |
| `-Detached` | Inicia processo oculto e grava PID/logs em `logs/` |
| `-EnableTailscaleServe` | Tenta configurar Serve na instalação autenticada de Tailscale |

Em primeiro plano, pare com `Ctrl+C`. Em segundo plano, confira o PID informado pelo script e use `Stop-Process -Id <PID>`.

Alternativa sem script:

```powershell
$env:ARGUS_MVP_PROFILE = 'true'
$env:ARGUS_BACKEND_HOST = '127.0.0.1'
$env:ARGUS_BACKEND_PORT = '8000'
.\.venv\Scripts\python.exe -m app.server
```

O Python lê variáveis de ambiente; não carrega `.env` automaticamente. O arquivo `.env.example` serve de referência e é lido pelo Docker Compose após ser copiado para `.env`.

### Modelos locais

Antes de uma demonstração, rode:

```powershell
.\scripts\prepare_models.ps1
```

O script baixa e aquece os pesos em `models/`: `models/yolo/yolov8n.pt`, `models/yolo/yoloe-11s-seg.pt`, `models/yolo/yolov8s-world.pt` e o cache do MiDaS em `models/torch`. Esses arquivos são locais e não entram no Git.

`run_backend_mvp.ps1` aponta automaticamente `ARGUS_YOLO_MODEL_PATH`, `ARGUS_YOLOE_MODEL_PATH`, `ARGUS_YOLO_WORLD_MODEL_PATH`, `ARGUS_TACTILE_MODEL_PATH` e `TORCH_HOME` para essa estrutura quando as variáveis ainda não foram definidas. Se precisar testar outro peso, defina a variável antes de subir o backend.

### Testar a API

Com o servidor ativo:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
.\.venv\Scripts\python.exe scripts/test_detect_image.py 'tests/img_exemplo/[IA]corredor_elevador.jpg' --url http://127.0.0.1:8000/detect
```

Os endereços acima são exemplos locais. No celular, use o IP/host alcançável da máquina. A primeira inferência pode ser lenta mesmo com modelos locais, pois o processo ainda precisa carregar os pesos para a memória. `/ready` não aquece nem comprova disponibilidade dos pesos.

## Flutter e Android

Instale Flutter com Dart compatível com `pubspec.lock`, Android SDK e JDK 17. Execute `flutter doctor` e resolva as pendências do toolchain Android. O projeto nativo já está em `app_flutter/android/`.

Toolchain validado nesta reorganização: Flutter 3.47.5, Dart 3.13.4 e Python 3.12.14. O build debug passou; a suíte Python teve 51 testes aprovados e a Flutter, 9. Esses números registram esta revisão e não substituem a execução após novas mudanças.

```powershell
cd app_flutter
flutter pub get
flutter analyze
flutter test
flutter run
```

Permita câmera e microfone no dispositivo. Preencha **Configurações** com protocolo (`http`/`https`), host sem caminho, porta opcional e timeouts. Para um backend local, PC e aparelho precisam ter conectividade entre si e o firewall deve permitir a porta escolhida.

### APK

Na raiz:

```powershell
.\scripts\build_apk_mvp.ps1
.\scripts\build_apk_mvp.ps1 -Mode release
```

O script procura Flutter e SDK em `.tools/`; se ausentes, usa Flutter do PATH e `ANDROID_HOME`/`ANDROID_SDK_ROOT`. Também aceita caminhos explícitos:

```powershell
.\scripts\build_apk_mvp.ps1 -FlutterPath 'C:\flutter\bin\flutter.bat' -AndroidSdkPath 'C:\Android\Sdk' -JavaHome 'C:\Java\jdk-17'
```

`-Offline` usa o cache de pacotes Dart e evita nova resolução durante analyze/test/build. Isso não garante Gradle offline: dependências Android ausentes ainda podem exigir rede. `-SkipAnalyze` e `-SkipTests` existem para execuções já validadas.

O APK sai em `app_flutter/build/app/outputs/flutter-apk/app-debug.apk` ou `app-release.apk`; o script imprime caminho e SHA256. **Release ainda usa assinatura de debug**, conforme `android/app/build.gradle.kts`; não é um pacote preparado para publicação em loja. Uma assinatura diferente da instalação anterior impede atualização direta. A instalação e o teste no celular ficam com o responsável.

Os caches e a chave de debug ficam em `.tools/`; `ARGUS_ANDROID_USER_HOME` permite escolher outro diretório Android. Não versionar chaves nem `local.properties`.

## Utilitários e experimentos

| Script em `scripts/` | Uso |
|---|---|
| `prepare_models.ps1` | Baixa/aqueça os modelos locais em `models/` |
| `test_detect_image.py` | Envia imagem à API; exige `--url` ou `ARGUS_DETECT_URL` |
| `test_yolo_image.py` | Executa YOLO local: `python scripts/test_yolo_image.py <imagem>` |
| `benchmark_api.py` | Compara configurações pela API; defina `ARGUS_DETECT_URL`; imagem e repetições ficam nas constantes iniciais |
| `benchmark_routed_detection.py` | Compara roteamento diretamente no pipeline |
| `evaluate_navigation_detection.py` | Avalia diretório de imagens; consulte `--help` |
| `test_scene_router.py`, `test_generalist_scene_analyzer.py` | Inspeção do planejamento de detectores |
| `test_poi_detection.py`, `test_tactile_detection.py` | Experimentos com pontos de interesse e piso tátil |
| `routed_detection_common.py` | Funções compartilhadas dos scripts de experimento |
| `text_to_qrcode.py` | Gera QR de texto/referências para material acadêmico |

Execute experimentos comparativos fora do perfil MVP quando precisar dos especialistas opcionais. Os scripts `test_*.py` em `scripts/` são utilitários manuais; a suíte automatizada é `pytest tests`.

## Antes de publicar alterações

1. Rode `python -m pytest tests -q`, `flutter analyze` e `flutter test`.
2. Revise `git status --short`, `git diff` e, após selecionar arquivos, `git diff --cached`.
3. Confira se não há `.env`, credenciais, APK, pesos, logs ou imagens novas sem revisão.
4. Faça commit com escopo claro e envie à branch remota escolhida, sem force push.
5. Registre limitações: testes unitários não validam STT, TalkBack ou qualidade dos modelos em um dispositivo real.
