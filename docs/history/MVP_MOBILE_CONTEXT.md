# ARGUS — Contexto para o Codex planejar o MVP Mobile da Iniciação Científica

> **Data de consolidação:** 21/09/2026
> **Projeto:** ARGUS — Sistema Integrado de Visão Computacional e Inteligência Artificial para Descrição do Ambiente e Sugestão de Rotas para Pessoas Cegas e com Baixa Visão
> **Foco atual:** retomar o desenvolvimento do aplicativo móvel e produzir um MVP funcional para demonstração ao professor/orientador.
> **Prioridade desta etapa:** integração ponta a ponta entre câmera do smartphone, backend existente e feedback auditivo.

---

## 1. Instrução inicial obrigatória para o Codex

Antes de implementar qualquer alteração:

1. Leia `AGENTS.md`.
2. Leia os documentos da pasta `docs/`, principalmente:
   - `docs/01_CONTEXTO_IC_ARGUS.md`
   - `docs/02_ESCOPO_E_LIMITES.md`
   - `docs/03_ARQUITETURA_TECNICA.md`
   - `docs/04_DADOS_TREINAMENTO_E_MODELO.md`
   - `docs/05_REQUISITOS_E_FLUXOS.md`
   - `docs/06_ROADMAP_E_TAREFAS_CODEX.md`
   - `docs/07_FONTES_E_DECISOES.md`
3. Leia este arquivo por completo.
4. Faça uma auditoria do repositório local antes de assumir o estado de qualquer módulo.
5. Rode os testes existentes e valide o backend antes de criar o aplicativo.
6. **Não comece implementando imediatamente. Primeiro entregue um plano de implementação.**
7. Caso o repositório local possua arquivos, branches, alterações não commitadas ou módulos mais recentes do que os descritos aqui, considere o **código local atual como fonte de verdade para o estado de implementação** e atualize o plano.

O plano inicial do Codex deve informar:

- o que já está funcional;
- o que existe parcialmente;
- o que ainda não existe;
- quais arquivos serão criados ou alterados;
- a ordem das etapas;
- como cada etapa será validada;
- riscos técnicos;
- dependências;
- diferenças encontradas entre documentação e código.

Não expandir o projeto além do necessário para o MVP da IC.

---

## 2. Objetivo imediato

O objetivo agora **não é construir o produto final do ARGUS**.

O objetivo é apresentar um MVP funcional capaz de demonstrar claramente o fluxo:

```text
Câmera do smartphone
        ↓
Aplicativo Flutter
        ↓
Imagem enviada por HTTP
        ↓
Backend Python / FastAPI
        ↓
Detecção de objetos / obstáculos
        ↓
Estimativa monocular de profundidade
        ↓
Filtragem e priorização
        ↓
Orientação/mensagem em português
        ↓
Aplicativo Flutter
        ↓
Text-to-Speech
        ↓
Feedback auditivo ao usuário
```

Para a apresentação ao professor, o mais importante é demonstrar a **integração ponta a ponta** funcionando em um smartphone real.

O MVP deve provar que o sistema consegue:

1. acessar a câmera;
2. capturar imagens do ambiente;
3. enviá-las ao backend;
4. obter detecções;
5. obter informação espacial/proximidade aproximada;
6. receber uma mensagem gerada pelo ARGUS;
7. reproduzir essa mensagem por áudio.

---

# 3. Escopo correto desta etapa

## 3.1 Contexto acadêmico

Este repositório é referente à **Iniciação Científica**, portanto o nome ARGUS pode e deve ser utilizado.

O projeto investiga a viabilidade de uma solução assistiva baseada em visão computacional e inteligência artificial para apoiar pessoas cegas e com baixa visão na compreensão e navegação em **ambientes internos**.

A solução deve ser entendida como **tecnologia assistiva complementar**, e não como substituta de bengala, cão-guia ou outras técnicas formais de orientação e mobilidade.

## 3.2 Características centrais

O sistema deve priorizar:

- smartphone convencional;
- câmera RGB;
- ambientes internos;
- detecção de obstáculos e pontos de interesse;
- posição aproximada na imagem;
- profundidade monocular relativa;
- mensagens curtas;
- feedback auditivo;
- baixo custo;
- arquitetura simples;
- rastreabilidade experimental;
- facilidade de explicação acadêmica.

## 3.3 Fora do escopo do MVP

Não implementar nesta etapa, salvo solicitação explícita:

- SLAM;
- mapa 3D persistente;
- localização absoluta;
- planejamento global de rotas;
- GPS ou navegação externa;
- reconstrução tridimensional completa;
- distância exata em metros sem calibração;
- reconhecimento facial;
- arquitetura de microserviços;
- banco de dados complexo;
- autenticação;
- sistema de contas;
- painel administrativo;
- integração com LiDAR ou câmera estéreo;
- comandos de voz;
- conversação com LLM;
- modelo multimodal externo para descrição ampla do ambiente;
- integração com smartwatches, bengalas eletrônicas ou wearables;
- deploy de produção;
- testes diretos com pessoas com deficiência visual sem planejamento e aprovação ética.

Esses elementos podem continuar documentados como evolução futura.

---

# 4. Ordem de precedência das fontes

Há diferenças entre documentos produzidos em momentos distintos do projeto.

Ao encontrar conflito, utilizar esta ordem:

1. **Código presente no repositório local atual** — fonte de verdade sobre o que está implementado.
2. **Relatório Final da Iniciação Científica (agosto/2026)** — fonte principal sobre a arquitetura efetivamente adotada na IC.
3. `AGENTS.md` e documentação atual da pasta `docs/`.
4. Relatório Semestral da IC.
5. Documentação inicial da IC.
6. Documentação do TCC — utilizar apenas requisitos e conceitos que sejam compatíveis com a IC atual.

### Divergência importante

Documentos anteriores do TCC mencionam:

- frontend em React;
- backend em Node.js.

Essa arquitetura **não deve ser adotada para o MVP atual da IC**.

O Relatório Final da IC registra posteriormente:

- **Flutter** para a aplicação móvel;
- **Python + FastAPI + Uvicorn** para o backend;
- **Ultralytics YOLO** para detecção;
- **MiDaS** para profundidade monocular;
- TTS executado no aplicativo.

Essa é a arquitetura a preservar.

---

# 5. Estado atual confirmado do código

A análise da branch pública `main` do repositório `SantLuiz/Argus` confirma que já existe uma base considerável do backend.

> O Codex deve confirmar novamente essas informações no repositório local antes de planejar alterações.

---

## 5.1 API FastAPI

Arquivo principal observado:

```text
app/main.py
```

O backend utiliza FastAPI e registra pelo menos:

```text
GET /health
POST /detect
```

O endpoint de detecção recebe imagem em `multipart/form-data`.

Parâmetros atualmente observados em `/detect`:

```text
mode
target_class
use_open_vocab
use_semantic_segmentation
use_tactile_specialist
use_classic_tactile
use_ocr
```

Formatos aceitos:

```text
image/jpeg
image/png
image/webp
```

Para o MVP Flutter, inicialmente usar somente o fluxo principal e evitar ativar detectores experimentais sem necessidade.

---

## 5.2 Pipeline de percepção já existente

O arquivo:

```text
app/services/detection_pipeline.py
```

implementa um pipeline cuja intenção principal é:

```text
imagem
→ YOLO
→ MiDaS
→ associação bbox + profundidade
→ pós-processamento
→ navegação local
→ mensagem
→ payload para TTS
```

O pipeline já possui componentes relacionados a:

- YOLO;
- profundidade monocular;
- pós-processamento;
- normalização/priorização;
- navegação local;
- geração de mensagem;
- payload de áudio;
- medição de tempo de processamento;
- modos de exploração/navegação;
- detectores experimentais adicionais.

Também existem mecanismos de fallback para impedir que a ausência do MiDaS derrube completamente o endpoint.

---

## 5.3 YOLO real

Arquivo observado:

```text
app/vision/yolo_detector.py
```

Já existe integração com Ultralytics YOLO.

Modelo padrão:

```text
yolov8n.pt
```

É possível trocar os pesos por variável de ambiente:

```text
ARGUS_YOLO_MODEL_PATH
```

Exemplo:

```text
ARGUS_YOLO_MODEL_PATH=models/best.pt
```

O detector retorna:

- classe;
- confiança;
- bounding box;
- modelo de origem;
- tipo de detecção.

### Observação acadêmica

O modelo COCO genérico é útil para objetos comuns, mas classes específicas de acessibilidade podem exigir pesos próprios.

O Relatório Final da IC registra resultados melhores para obstáculos comuns e piso tátil, e resultados menos consistentes para portas e elevadores.

Não transformar a correção dessas classes em pré-requisito para iniciar o aplicativo Flutter.

---

## 5.4 MiDaS real

Arquivo observado:

```text
app/vision/midas_estimator.py
```

Existe implementação real do MiDaS.

Modelo padrão observado:

```text
MiDaS_small
```

A saída é normalizada entre:

```text
0.0 → 1.0
```

Ela representa **profundidade/proximidade relativa**, não distância métrica.

Nunca apresentar mensagens como:

```text
"objeto a 1,8 metro"
```

sem existir uma etapa formal de calibração.

Usar categorias como:

- muito próximo;
- próximo;
- médio;
- distante.

---

## 5.5 Associação de profundidade e posição

O backend já combina a bounding box da detecção com o mapa de profundidade.

Também existe classificação horizontal aproximada:

- esquerda;
- centro;
- direita.

As detecções enriquecidas podem incluir:

- `class_name`;
- `confidence`;
- `bbox`;
- `zone`;
- `depth.relative_value`;
- `depth.proximity`;
- `depth.label_pt`;
- `priority`;
- `semantic_role`;
- `navigation_score`;
- `source_model`.

Isso significa que **o Flutter não deve duplicar a lógica de visão computacional**.

O aplicativo deve ser um cliente leve.

---

## 5.6 Navegação local simples

Arquivo observado:

```text
app/navigation/local_navigator.py
```

Existe uma navegação local baseada apenas no frame atual.

O próprio módulo declara explicitamente que não implementa:

- SLAM;
- mapa 3D;
- rota global.

A lógica atual é compatível com o escopo do MVP.

Exemplos de comportamentos:

- obstáculo muito próximo no centro → `Pare`;
- alvo à esquerda → orientação para virar levemente à esquerda;
- alvo à direita → orientação para virar levemente à direita;
- alvo central → seguir em frente;
- alvo não encontrado → procurar girando lentamente.

---

## 5.7 Geração de mensagem

Arquivo observado:

```text
app/guidance/message_generator.py
```

Já existe geração de mensagens curtas em português.

Exemplos esperados conceitualmente:

```text
"Pessoa muito próxima à frente. Pare."
"Caminho livre em direção à porta."
"Escada à esquerda."
```

Essa mensagem deve ser tratada como a principal saída de interação do aplicativo.

---

## 5.8 Contrato da resposta da API

O schema atual inclui:

```text
detections
raw_detections
message
audio
processing_time_ms
mode
use_open_vocab
detection_plan
generalist_findings
models_called
navigation
image_name
notes
```

O campo `audio` atualmente representa um **payload textual para TTS no cliente**, não um arquivo de áudio.

Estrutura relevante:

```json
{
  "message": "Pessoa próxima à frente.",
  "audio": {
    "text": "Pessoa próxima à frente.",
    "language": "pt-BR",
    "mode": "tts_client"
  }
}
```

### Regra para Flutter

Preferir:

```text
response.audio.text
```

como texto a ser sintetizado.

Se o campo não estiver presente por incompatibilidade de versão, usar `response.message` como fallback.

---

# 6. Estado atual do aplicativo Flutter

## Situação identificada

Na árvore pública atual da branch `main`, **não foi localizado um projeto Flutter completo**.

Não aparecem na raiz pública, por exemplo:

```text
pubspec.yaml
lib/
android/
ios/
app_flutter/
mobile/
```

A documentação prevê o Flutter, mas o código mobile não está visível na branch pública analisada.

### Consequência

O próximo grande bloco de implementação deve ser:

> **criar ou recuperar o cliente Flutter e integrá-lo ao backend existente.**

### Importante

É possível que exista código Flutter:

- somente na máquina local;
- em outra branch;
- em outro repositório;
- ainda não commitado;
- em arquivos que não estavam disponíveis na branch pública consultada.

Por isso o Codex deve iniciar com:

```bash
git status
git branch --all
git log --oneline --decorate -n 30
```

e procurar por:

```text
pubspec.yaml
*.dart
android/
ios/
lib/
app_flutter/
flutter/
mobile/
```

Se existir uma versão local mais recente, não recriá-la do zero sem necessidade.

---

# 7. Inconsistência documental que deve ser corrigida

O `README.md` público ainda descreve partes do backend como uma versão inicial com serviços simulados.

Entretanto, o código atual contém:

- `YoloDetector`;
- `MidasEstimator`;
- `DetectionPipeline`;
- navegação local;
- geração de mensagens;
- múltiplos detectores complementares.

Portanto:

1. não assumir que o README representa todo o estado atual;
2. validar o comportamento executando o código;
3. depois do MVP, atualizar README/documentação para refletir o estado real.

---

# 8. MVP Mobile — requisitos obrigatórios

O MVP deverá ser desenvolvido primeiro para **Android**.

## RF-MVP-01 — Inicialização

O aplicativo deve:

- iniciar sem erro;
- apresentar uma tela principal simples;
- informar o estado do sistema.

Estados úteis:

```text
Backend desconectado
Conectando
Pronto
Analisando
Erro
```

---

## RF-MVP-02 — Permissão de câmera

Na primeira utilização:

- solicitar permissão de câmera;
- explicar a necessidade da permissão de forma simples;
- tratar negação sem crash.

---

## RF-MVP-03 — Preview da câmera

Exibir a câmera traseira em tempo real.

O preview é essencial para a demonstração, mesmo que o usuário final do projeto não dependa visualmente dele.

---

## RF-MVP-04 — Iniciar e parar análise

A tela deve possuir controles grandes e semanticamente identificados para:

```text
Iniciar análise
Parar análise
```

Ao iniciar:

1. capturar frame;
2. enviar para `/detect`;
3. aguardar resposta;
4. processar a mensagem;
5. repetir.

### Importante

Não enviar frames enquanto uma requisição anterior ainda estiver sendo processada.

Evitar acumular fila de imagens.

---

## RF-MVP-05 — Frequência controlada

Para o MVP, não é necessário processar 30 FPS.

A prioridade é estabilidade.

Estratégia inicial sugerida:

```text
1 frame a cada 0,7–1,5 segundo
```

ou:

```text
próximo frame somente após o backend responder
```

O Codex deve medir o tempo real do backend e escolher a cadência mais simples que mantenha a demonstração fluida.

---

## RF-MVP-06 — Compressão da imagem

Antes de enviar, evitar frames desnecessariamente grandes.

Meta inicial aceitável:

```text
JPEG
640x480, 640x640 ou resolução próxima
qualidade moderada
```

Não degradar a imagem ao ponto de comprometer a detecção.

---

## RF-MVP-07 — Comunicação com backend

O app deve enviar:

```text
multipart/form-data
campo: image
```

Endpoint inicial:

```text
POST /detect?mode=exploration
```

O endereço do backend não deve ficar espalhado pelo código.

Criar configuração central, por exemplo:

```text
ARGUS_API_BASE_URL
```

Durante desenvolvimento, permitir alterar facilmente entre:

```text
http://10.0.2.2:8000
http://<IP-DO-PC>:8000
```

---

## RF-MVP-08 — Health check

Ao iniciar, o app deve conseguir verificar:

```text
GET /health
```

O health check deve informar rapidamente se:

- backend está acessível;
- endereço configurado está incorreto;
- computador e celular não estão na mesma rede;
- serviço não está rodando.

---

## RF-MVP-09 — TTS no dispositivo

Usar TTS no Flutter.

Idioma padrão:

```text
pt-BR
```

O aplicativo deve reproduzir:

```text
response.audio.text
```

com fallback para:

```text
response.message
```

### Não esperar áudio vindo do backend

O backend produz a mensagem.

O smartphone produz a fala.

---

## RF-MVP-10 — Controle de repetição do áudio

Este ponto é essencial.

Se o mesmo resultado for retornado repetidamente, o app não deve falar a mesma mensagem a cada frame.

Implementar estratégia simples de:

- deduplicação;
- cooldown;
- prioridade.

Exemplo:

```text
"Pessoa próxima à frente."
```

não deve ser repetido 5 vezes em 5 segundos.

### Exceção

Mensagens críticas, especialmente contendo instruções como:

```text
Pare
```

podem interromper a fala atual e receber prioridade.

---

## RF-MVP-11 — Interface acessível

Usar:

- botões grandes;
- contraste adequado;
- labels semânticos;
- `Semantics`;
- compatibilidade com TalkBack;
- texto de status simples;
- mínima dependência de ícones sem descrição.

Toda ação importante deve possuir descrição textual.

---

## RF-MVP-12 — Última resposta

Para facilitar a apresentação e debug, exibir:

- última mensagem;
- tempo total de processamento;
- quantidade de detecções;
- estado da conexão.

Essa informação pode ficar em uma área visual secundária.

O feedback auditivo continua sendo a saída principal.

---

## RF-MVP-13 — Tratamento de erros

Não encerrar o aplicativo em caso de:

- backend offline;
- timeout;
- imagem inválida;
- ausência de detecções;
- erro temporário do modelo;
- permissão negada;
- perda da rede.

Exibir estado claro e permitir nova tentativa.

---

# 9. MVP — modo navegação

O backend já possui suporte a:

```text
mode=navigation
target_class=<classe>
```

O endpoint exige `target_class` quando `mode=navigation`.

Esse recurso é útil para uma segunda etapa do MVP, mas **não deve bloquear a primeira integração câmera → detecção → TTS**.

### Ordem sugerida

Primeiro:

```text
mode=exploration
```

Depois, se o fluxo estiver estável:

```text
mode=navigation
```

com seleção simples de destino.

Exemplos de destino potencial:

- porta;
- escada;
- elevador;
- recepção;
- piso tátil.

Antes de criar a lista, conferir:

```text
app/detection/class_mapper.py
app/navigation/target_selector.py
```

para saber quais valores de `target_class` são realmente normalizados pelo backend.

---

# 10. Funcionalidades que não devem bloquear a apresentação

Os seguintes módulos podem existir no backend, porém **não são necessários para o primeiro MVP Flutter**:

- open vocabulary;
- segmentação semântica;
- OCR;
- detector especialista de piso tátil;
- heurística de escada/rampa;
- descrição ampla via IA multimodal;
- navegação por destino sofisticada.

O primeiro objetivo é consumir o pipeline padrão existente.

Depois da integração básica, funcionalidades adicionais podem ser habilitadas individualmente.

---

# 11. Arquitetura Flutter recomendada

Não criar uma arquitetura excessiva.

Estrutura simples sugerida:

```text
mobile_flutter/
├── pubspec.yaml
├── lib/
│   ├── main.dart
│   ├── config/
│   │   └── app_config.dart
│   ├── models/
│   │   └── detection_response.dart
│   ├── services/
│   │   ├── argus_api_service.dart
│   │   └── tts_service.dart
│   ├── screens/
│   │   └── camera_screen.dart
│   └── widgets/
│       └── system_status.dart
└── android/
```

Não introduzir:

- Redux;
- BLoC complexo;
- Clean Architecture completa;
- múltiplas camadas abstratas;
- injeção de dependência pesada.

Se `setState`, `ValueNotifier` ou solução equivalente resolver o MVP de forma clara, preferir isso.

---

# 12. Dependências Flutter candidatas

Avaliar versões atuais e compatibilidade antes de adicionar.

Pacotes esperados:

```text
camera
http OU dio
flutter_tts
permission_handler
```

Possíveis complementos somente se realmente necessários:

```text
path_provider
image
```

Usar **somente um** cliente HTTP.

---

# 13. Android — pontos que precisam ser considerados

O Codex deve revisar:

```text
android/app/src/main/AndroidManifest.xml
```

Permissões necessárias:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
```

Durante desenvolvimento local, caso o backend seja acessado por HTTP em uma LAN, verificar as restrições Android relacionadas a tráfego HTTP não criptografado.

Se for necessário habilitar `cleartext` para o MVP de laboratório, documentar claramente que isso existe apenas para desenvolvimento/teste local.

Não expor o backend sem autenticação à Internet pública.

---

# 14. Backend para acesso pelo celular

Quando executado somente em:

```text
127.0.0.1
```

o backend não pode ser acessado pelo celular.

Para teste em dispositivo físico na mesma rede, executar, por exemplo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Depois usar no Flutter:

```text
http://<IPv4-do-PC>:8000
```

O Codex deve incluir no plano:

- descoberta do IPv4 local;
- teste de `/health` pelo celular;
- Windows Firewall;
- rede privada/confiável;
- VPNs/adaptadores que possam interferir.

---

# 15. Estratégia de captura recomendada

Existem duas abordagens principais.

## Opção A — captura periódica com `takePicture()`

Mais simples para o MVP.

Fluxo:

```text
captura
→ JPEG
→ POST
→ resposta
→ pequena espera
→ próxima captura
```

Vantagens:

- menor complexidade;
- arquivo JPEG pronto;
- integração simples com multipart.

Desvantagens:

- menor fluidez;
- pode existir pequeno atraso entre capturas.

## Opção B — `startImageStream()`

Mais adequada a visão computacional contínua.

Porém exige:

- lidar com YUV/BGRA;
- conversão;
- compressão;
- controle de FPS;
- mais processamento no celular.

### Recomendação para o primeiro MVP

Começar pela alternativa mais simples que consiga demonstrar fluxo contínuo de maneira estável.

Migrar para image stream somente se a captura periódica realmente comprometer a demonstração.

---

# 16. Estado do modelo e limitações conhecidas

Resultados registrados na IC indicam:

### Funcionamento satisfatório

- obstáculos comuns;
- pessoas;
- cadeiras;
- mesas;
- mochilas;
- piso tátil;
- extração de posição;
- combinação com profundidade;
- geração de informações estruturadas;
- integração entre componentes do backend.

### Pontos mais fracos

- portas;
- elevadores;
- objetos pequenos;
- elementos distantes;
- oclusão;
- diferentes condições visuais.

### Profundidade

É relativa.

Não afirmar precisão métrica.

### Desempenho

O relatório final considerou o tempo suficiente para validação experimental, mas o comportamento no ciclo contínuo do smartphone ainda precisa ser medido.

---

# 17. Privacidade

Para o MVP:

- processar imagens transitoriamente;
- evitar salvar frames por padrão;
- não enviar imagens a serviços externos sem necessidade;
- não registrar rostos identificáveis;
- se imagens forem persistidas para experimento, documentar finalidade e anonimização.

---

# 18. Plano de implementação que o Codex deve propor

A sugestão abaixo é uma referência. O Codex deve ajustá-la após auditar o repositório.

## Fase 0 — Auditoria

- verificar `git status`;
- verificar branches;
- localizar possível código Flutter;
- executar `pytest`;
- iniciar FastAPI;
- testar `/health`;
- testar `/detect` com imagem real;
- registrar resposta JSON;
- medir tempo;
- confirmar se YOLO e MiDaS carregam corretamente;
- confirmar existência e estado de `models/best.pt`;
- verificar documentação desatualizada.

### Resultado

Relatório curto:

```text
Funcional
Parcial
Ausente
Quebrado
Não verificado
```

---

## Fase 1 — Criar/recuperar projeto Flutter

- criar projeto Android;
- configurar dependências;
- configurar permissões;
- criar tela inicial;
- implementar health check.

### Critério de aceite

App instalado em smartphone real e mostrando backend conectado.

---

## Fase 2 — Integração HTTP com imagem estática

Antes da câmera contínua:

- selecionar ou capturar uma imagem;
- enviar a `/detect`;
- desserializar JSON;
- exibir `message`;
- exibir tempo de processamento.

### Critério de aceite

Uma imagem do telefone percorre o backend e a resposta aparece no Flutter.

---

## Fase 3 — Feedback auditivo

- integrar `flutter_tts`;
- idioma `pt-BR`;
- reproduzir `audio.text`;
- fallback em `message`;
- controlar fila.

### Critério de aceite

Resposta do ARGUS é falada pelo smartphone.

---

## Fase 4 — Câmera contínua controlada

- preview;
- botão iniciar;
- botão parar;
- captura sequencial;
- impedir requisições simultâneas;
- limitar frequência;
- compressão;
- cancelar loop ao sair da tela.

### Critério de aceite

Câmera → backend → resposta → áudio ocorre repetidamente sem travar.

---

## Fase 5 — Inteligência de áudio

- deduplicação;
- cooldown;
- prioridade para alertas;
- evitar sobreposição;
- `stop()` antes de alerta crítico.

### Critério de aceite

O app não repete mensagens constantemente e continua alertando eventos importantes.

---

## Fase 6 — Modo navegação opcional

Se houver tempo:

- alternar entre exploração e navegação;
- selecionar um destino simples;
- enviar `mode=navigation`;
- enviar `target_class`;
- falar `navigation.instruction`.

### Critério de aceite

Alvo aparece → app orienta esquerda/centro/direita.

---

## Fase 7 — Polimento para apresentação

- layout simples;
- Semantics;
- estados claros;
- tratamento de erros;
- README;
- roteiro de demonstração;
- registrar limitações.

---

# 19. Testes obrigatórios do MVP

## Backend

Executar:

```bash
pytest
```

Testar manualmente:

```text
GET /health
POST /detect
```

Cenários:

- pessoa;
- cadeira;
- mesa;
- obstáculo central;
- cena sem detecção;
- erro de modelo;
- imagem inválida.

---

## Flutter

Testar:

- primeira execução;
- câmera permitida;
- câmera negada;
- backend offline;
- IP incorreto;
- rede desconectada;
- backend lento;
- nenhuma detecção;
- mensagem repetida;
- alerta crítico;
- pausar análise;
- voltar ao app depois de minimizá-lo;
- rotação/orientação se aplicável.

---

## Integração real

Obrigatoriamente testar em:

```text
smartphone Android físico
+
PC executando FastAPI
+
mesma LAN/Wi-Fi
```

Emulador pode ser usado para desenvolvimento, mas não substitui o teste de apresentação.

---

# 20. Métricas úteis para a apresentação

Não é necessário construir um sistema analítico complexo.

Registrar:

- tempo de detecção;
- tempo de profundidade;
- tempo total do backend;
- tempo aproximado entre captura e início da fala;
- número de frames analisados;
- erros de requisição;
- exemplos de mensagens;
- classes detectadas.

Esses dados podem apoiar tanto a apresentação quanto a documentação acadêmica.

---

# 21. Critérios de aceite do MVP para o professor

Considerar o MVP pronto para apresentação quando for possível demonstrar:

1. abrir o app no Android;
2. permitir câmera;
3. ver preview;
4. confirmar conexão com o backend;
5. iniciar análise;
6. apontar para uma cena interna;
7. enviar imagem automaticamente;
8. backend detectar pelo menos objetos comuns;
9. combinar detecção com posição/profundidade relativa;
10. receber uma mensagem;
11. reproduzir a mensagem por TTS;
12. repetir o ciclo sem travar;
13. interromper a análise;
14. explicar claramente as limitações.

O aplicativo não precisa estar pronto para uso por público real.

---

# 22. Roteiro ideal de demonstração

Sugestão:

1. Executar backend no notebook.
2. Mostrar rapidamente `/health`.
3. Abrir app ARGUS.
4. Mostrar estado `Conectado`.
5. Iniciar câmera.
6. Apontar para uma cadeira/pessoa/mesa.
7. Acionar/iniciar análise.
8. Ouvir mensagem.
9. Aproximar objeto ou mudar sua posição.
10. Ouvir atualização.
11. Se o modo navegação estiver pronto, selecionar um alvo e demonstrar esquerda/direita/frente.
12. Encerrar mostrando tempos de processamento.
13. Explicar:
   - profundidade é relativa;
   - protótipo usa câmera RGB;
   - processamento principal está no backend;
   - TTS ocorre no smartphone;
   - objetivo da IC é validar viabilidade técnica.

---

# 23. Pontos que o Codex deve conferir no repositório antes de codificar

### Código

- [ ] existe algum `pubspec.yaml` local?
- [ ] existe branch Flutter?
- [ ] `/health` funciona?
- [ ] `/detect` funciona?
- [ ] YOLO baixa/carrega pesos?
- [ ] MiDaS baixa/carrega pesos?
- [ ] fallback está sendo acionado?
- [ ] `models/best.pt` existe?
- [ ] `pytest` passa?
- [ ] quais classes `class_mapper` reconhece?
- [ ] quais modos estão definidos em `navigation_state.py`?
- [ ] o endpoint já possui limite de tamanho?
- [ ] existe timeout configurado?
- [ ] há logs suficientes?
- [ ] a documentação atual condiz com a implementação?

### Mobile

- [ ] código Flutter existe localmente?
- [ ] Android SDK/Flutter doctor estão corretos?
- [ ] smartphone pode ser usado por USB/Wi-Fi?
- [ ] PC e celular estarão na mesma rede na apresentação?
- [ ] backend será executado localmente ou remotamente?

---

# 24. Questões não bloqueantes

Não interromper o planejamento por perguntas que possam ser resolvidas pela inspeção do código.

Se precisar assumir valores, utilizar defaults simples e documentados.

Exemplos:

- backend inicialmente local;
- Android como plataforma primária;
- `mode=exploration` como modo padrão;
- TTS em `pt-BR`;
- câmera traseira;
- frequência baixa e sequencial;
- sem persistência de imagem.

Somente pedir decisão humana se houver impacto relevante no escopo ou arquitetura.

---

# 25. Contexto dos códigos disponíveis

Foi possível localizar e analisar o backend público atual.

Portanto, já existe contexto de código suficiente para planejar a integração.

Entretanto, **não há visibilidade sobre arquivos não commitados, branches privadas ou código existente apenas na máquina de desenvolvimento**.

Se houver uma versão mais recente localmente, ela deve ser incorporada à auditoria inicial do Codex.

Arquivos públicos relevantes identificados:

```text
app/main.py
app/routes/detect.py
app/schemas/detection.py
app/services/detection_pipeline.py
app/vision/yolo_detector.py
app/vision/midas_estimator.py
app/vision/depth.py
app/guidance/message_generator.py
app/navigation/local_navigator.py
AGENTS.md
docs/03_ARQUITETURA_TECNICA.md
docs/05_REQUISITOS_E_FLUXOS.md
docs/06_ROADMAP_E_TAREFAS_CODEX.md
```

---

# 26. Fontes acadêmicas e documentais utilizadas para consolidar este contexto

Foram considerados:

- `ARGUS - Relatório Semestral IC.pdf`
- `Relatório Final - Pesquisa IC_Luiz Santana e Welber William + Declaração Uso IA.pdf`
- `DOCUMENTAÇÃO_PROJETO_IC_IA+INTELIGENCIA_ARTIFICIAL.pdf`
- `[PDF BANCA] DOC TCC.pdf`
- documentação atual do repositório ARGUS;
- código público atual do repositório.

O livro **Processamento Digital de Imagens**, de Gonzalez e Woods, continua como base conceitual importante para processamento de imagens, mas não altera a arquitetura de software deste MVP.

---

# 27. Comando sugerido para iniciar a tarefa no Codex

Depois de adicionar este arquivo ao repositório, utilizar uma solicitação semelhante a:

```text
Leia AGENTS.md, este arquivo de contexto e toda a documentação relevante em docs/.

Quero retomar o ARGUS com foco na Iniciação Científica. A prioridade agora é entregar um MVP Android em Flutter para apresentar ao professor, integrado ao backend Python já existente.

Antes de escrever código:
1. audite completamente o estado atual do repositório;
2. rode os testes;
3. valide o backend e o endpoint /detect;
4. procure código Flutter existente em qualquer branch ou arquivo local;
5. identifique divergências entre documentação e implementação;
6. monte um plano detalhado, incremental e de baixo risco para chegar ao MVP câmera -> backend -> mensagem -> TTS.

No plano, informe:
- o que já está pronto;
- o que falta;
- arquivos que pretende criar/alterar;
- dependências;
- etapas;
- critérios de aceite;
- testes;
- riscos;
- o que pode ser deixado para depois.

Não implemente SLAM, navegação externa, microserviços ou funcionalidades que não sejam necessárias para a demonstração da IC.
Não comece a implementação antes de me apresentar o plano.
```

---

# 28. Princípio final

Para esta fase:

> **Um fluxo simples, estável e demonstrável vale mais do que uma arquitetura sofisticada incompleta.**

A prioridade é fazer funcionar, de ponta a ponta:

```text
CAMERA
→ FLUTTER
→ FASTAPI
→ YOLO
→ MIDAS
→ ORIENTAÇÃO
→ TTS
```

Depois disso, o projeto pode evoluir incrementalmente.
