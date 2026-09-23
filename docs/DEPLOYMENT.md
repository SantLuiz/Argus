# Backend em Docker e acesso remoto

Este guia substitui os dois documentos anteriores `10_*`. O endereço do servidor é configurado na tela do app; não existe etapa de build com URL fixa.

## Docker Compose

Requer Docker e Compose. Na raiz:

```powershell
Copy-Item .env.example .env
docker compose config
docker compose up -d --build
docker compose logs --tail 100
```

O exemplo faz o processo escutar `0.0.0.0:8000` **dentro do contêiner**, mas publica somente `127.0.0.1:8000` no host. Ajuste as quatro variáveis `ARGUS_BACKEND_HOST`, `ARGUS_BACKEND_PORT`, `ARGUS_PUBLISHED_HOST` e `ARGUS_PUBLISHED_PORT` no `.env` antes de executar. A interpolação do Compose exige valores definidos.

`.env` é usado pelo Compose para interpolar o YAML; apenas variáveis declaradas em `environment` são enviadas ao processo. Para personalizar pesos, acrescente as variáveis de modelo em `environment` e monte o diretório de pesos correspondente. O Compose atual não monta modelos nem cache persistente automaticamente.

O Dockerfile instala dependências, copia `app/` e executa como usuário `argus`. Pesos não entram na imagem. No fluxo local sem Docker, rode `scripts/prepare_models.ps1` e mantenha `models/` preservado. Em Docker, monte `models/` como volume e encaminhe `ARGUS_YOLO_MODEL_PATH`, `ARGUS_YOLOE_MODEL_PATH`, `ARGUS_YOLO_WORLD_MODEL_PATH`, `ARGUS_TACTILE_MODEL_PATH` e `TORCH_HOME` para caminhos dentro do contêiner. Faça uma inferência real antes da demonstração.

Validação:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
.\.venv\Scripts\python.exe scripts/test_detect_image.py 'tests/img_exemplo/[IA]corredor_elevador.jpg' --url http://127.0.0.1:8000/detect
```

Confirme `depth_source=midas` quando houver detecções. Pare com `docker compose down`. Não confundir `/ready` com teste dos pesos: o carregamento é sob demanda.

## Acesso pelo celular

Em rede local sem Docker, o script Python pode usar `-HostAddress 0.0.0.0`; configure no celular o IP real da máquina e a porta. Em Docker, a publicação padrão em loopback não fica acessível diretamente pela rede; altere `ARGUS_PUBLISHED_HOST` conscientemente se precisar dessa forma de acesso.

Para demonstração remota, a arquitetura prevista usa Tailscale no servidor e no celular, com acesso privado na mesma rede Tailscale. Instale e autentique a ferramenta separadamente, confirme a sintaxe da versão instalada com `tailscale serve --help` e encaminhe o serviço HTTP local por Serve. O script `run_backend_mvp.ps1 -EnableTailscaleServe` contém a integração local utilizada pelo projeto.

No app, preencha protocolo HTTPS, hostname privado fornecido pela ferramenta e porta correspondente. Não passe caminho `/detect` no campo host. Teste `/health`, `/ready` e uma análise pelo endereço que o celular realmente acessa.

## Hospedagem experimental

OCI permanece uma opção de experimento, não infraestrutura provisionada por este repositório. Verifique arquitetura, memória, disponibilidade e custo da conta antes de provisionar. O build da imagem e as dependências de ML precisam ser validados na arquitetura escolhida; um teste Windows não comprova execução em ARM.

Registre no experimento: ambiente, versões, modelos, imagem usada, latência, fonte de profundidade, mensagem e falhas. Consulte [pendências](PENDENCIAS.md) para o estado de validação do contêiner.
