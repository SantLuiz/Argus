# ARGUS — Iniciação Científica

Protótipo acadêmico da UNIP que transforma imagens de ambientes internos em descrições auditivas. O aplicativo Flutter captura a imagem; a API Python detecta objetos, estima profundidade monocular relativa e devolve uma mensagem em português para leitura no celular.

O objetivo é demonstrar viabilidade experimental. A profundidade não representa distância exata em metros e a orientação local não implementa uma rota global.

## Comece por aqui

- [Instalação, execução e build do APK](docs/DEVELOPMENT.md).
- [Mapa da codebase e guia para outras IAs](docs/CODEBASE.md).
- [API, modelos e configuração do backend](docs/README_TECNICO.md).
- [Voz, controles e acessibilidade](docs/11_VOZ_ACESSIBILIDADE_MOBILE.md).
- [Docker e acesso remoto](docs/DEPLOYMENT.md).
- [Pendências e limites da validação](docs/PENDENCIAS.md).
- [Índice completo da documentação](docs/README.md).

## Estrutura

```text
app/                  API Python: rotas, visão, profundidade e mensagem
app_flutter/          Aplicativo Flutter e projeto nativo Android
scripts/              Execução, build e utilitários de experimento
tests/                Testes Python e imagens de exemplo
models/               Pesos locais (não versionados)
results/              Resultados locais; somente o README é versionado
docs/                 Guias atuais, fundamentos da IC e histórico
AGENTS.md             Instruções para agentes que alteram o projeto
requirements.txt      Dependências Python fixadas
Dockerfile            Imagem do backend
docker-compose.yml    Execução em contêiner
```

O backend permanece no pacote `app/`, na raiz, para manter os imports e comandos `python -m app.server` e `uvicorn app.main:app`. O único aplicativo móvel é `app_flutter/`.

## Execução rápida no Windows

Requer Python 3.12, Flutter, Android SDK e JDK 17. Consulte o guia de desenvolvimento para preparar essas ferramentas.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\run_backend_mvp.ps1 -SkipDependencyInstall
```

O script executa testes e inicia o backend em primeiro plano. Os padrões locais são `127.0.0.1` e porta `8000`; altere com `-HostAddress` e `-Port`. Para acessar pelo celular na mesma rede, use `-HostAddress 0.0.0.0` e informe o IP da máquina nas configurações do app. `0.0.0.0` é endereço de escuta do servidor, não endereço para preencher no celular.

Em outro terminal:

```powershell
cd app_flutter
flutter pub get
flutter run
```

O projeto Android já está incluído: não é necessário executar `flutter create`. Configure protocolo, host e porta em **Configurações**. O endereço é salvo no aparelho, sem recompilar o APK.

Para gerar o APK com análise estática e testes, execute `./scripts/build_apk_mvp.ps1` na raiz.

## Estado atual

O código inclui câmera em tela cheia, controles sobrepostos, configurações persistidas, TTS, análise de imagem e modos de voz manual/passivo. **O reconhecimento de comandos continua falhando no Redmi Note 10 (Android 12/MIUI 14)** e foi adiado a pedido do responsável. Os testes automatizados não comprovam funcionamento do STT no aparelho.

TalkBack, contraste, escala de fonte e navegação por áudio ainda exigem validação manual completa. Não declarar conformidade total de acessibilidade apenas pela existência de componentes semânticos.

## Validação automatizada

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
cd app_flutter
flutter analyze
flutter test
```

Esses testes cobrem contratos e lógica isolada. Uma demonstração completa exige câmera, modelos reais, rede, TTS e teste no dispositivo. Pesos, caches, APKs, logs e ambientes locais não são publicados no GitHub.
