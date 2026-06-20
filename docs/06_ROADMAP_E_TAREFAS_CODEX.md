# 06 - Roadmap e tarefas para Codex

## Roadmap recomendado

### Fase 1 - Organização do repositório

Objetivo: preparar uma base limpa e compreensível.

Entregas:

- `README.md` do projeto.
- `AGENTS.md` com instruções para Codex.
- Pastas `app_flutter/`, `backend_python/`, `notebooks/`, `docs/`, `results/`.
- Arquivos `.gitignore` e instruções de ambiente.

### Fase 2 - Backend mínimo

Objetivo: criar uma API Python funcional.

Entregas:

- FastAPI com `/health`.
- Endpoint `/detect` aceitando upload de imagem.
- Validação básica de arquivo.
- Retorno JSON padronizado.
- Script de teste local.

### Fase 3 - Inferência inicial

Objetivo: validar o fluxo com modelo pré-treinado.

Entregas:

- Serviço de visão computacional.
- Uso de modelo pré-treinado.
- Conversão de detecções para classes e caixas.
- Cálculo de zona esquerda/centro/direita.
- Estimativa monocular de profundidade da cena.
- Associação de proximidade/distância aproximada a cada objeto detectado.
- Tempo de processamento da detecção e da profundidade.

### Fase 4 - Mensagem auditiva

Objetivo: transformar resultado visual em informação acessível.

Entregas:

- Serviço de geração de frases em português.
- Regras de priorização considerando posição e proximidade estimada.
- Mensagens curtas e objetivas.
- Testes unitários para geração de texto.

### Fase 5 - Flutter mínimo

Objetivo: criar interface simples de demonstração.

Entregas:

- Tela inicial acessível.
- Botão para capturar ou selecionar imagem.
- Envio para backend.
- Exibição da resposta textual.
- Reprodução via TTS.

### Fase 6 - Experimentos e documentação

Objetivo: apoiar a escrita da IC.

Entregas:

- Pasta `results/` com experimentos.
- Tabela de testes.
- Métricas simples, incluindo tempo de detecção e tempo de profundidade.
- Limitações observadas.
- Imagens de exemplo, quando permitido.

## Tarefas prontas para pedir ao Codex

### Criar backend base

```text
Leia AGENTS.md e os documentos em docs/. Crie a estrutura inicial do backend Python em FastAPI para o projeto ARGUS IC, com endpoint /health e endpoint /detect que aceite upload de imagem e retorne um JSON simulado no formato definido em docs/03_ARQUITETURA_TECNICA.md, incluindo campo de profundidade/proximidade. Mantenha a implementação simples e documentada.
```

### Criar serviço de detecção

```text
Leia AGENTS.md, docs/03_ARQUITETURA_TECNICA.md e docs/04_DADOS_TREINAMENTO_E_MODELO.md. Implemente um serviço Python de detecção de objetos usando um modelo pré-treinado leve. O serviço deve receber uma imagem, retornar classe, confiança, bbox e zona aproximada esquerda/centro/direita. Não implemente SLAM nem navegação complexa. A profundidade monocular será implementada em uma tarefa separada.
```

### Criar serviço de profundidade monocular

```text
Leia AGENTS.md, docs/03_ARQUITETURA_TECNICA.md, docs/04_DADOS_TREINAMENTO_E_MODELO.md e docs/05_REQUISITOS_E_FLUXOS.md. Implemente um serviço Python simples de estimativa monocular de profundidade usando MiDaS, Depth Anything ou modelo equivalente. O serviço deve receber a imagem e as caixas detectadas, calcular um valor relativo de profundidade por objeto e classificar cada item como próximo, médio ou distante. Não trate a saída como distância exata em metros.
```

### Criar gerador de mensagem

```text
Leia docs/05_REQUISITOS_E_FLUXOS.md. Crie um módulo Python que transforme uma lista de detecções com zona e proximidade estimada em uma frase curta em português para feedback auditivo. Priorize obstáculos próximos no centro, pessoas, portas e objetos grandes. Inclua testes unitários simples.
```

### Criar app Flutter mínimo

```text
Leia AGENTS.md e docs/05_REQUISITOS_E_FLUXOS.md. Crie uma tela Flutter simples e acessível que permita capturar/selecionar uma imagem, enviar para o backend /detect, mostrar a mensagem retornada e reproduzi-la com flutter_tts. Não crie funcionalidades fora do escopo da IC.
```

### Criar notebook de experimento

```text
Leia docs/04_DADOS_TREINAMENTO_E_MODELO.md. Crie um notebook de experimento para Google Colab com estrutura para testar um modelo de detecção em imagens internas, registrar tempo de inferência de detecção, tempo de inferência de profundidade monocular, classes detectadas, proximidade estimada e exemplos de mensagens geradas. O foco é documentação e reprodutibilidade da IC.
```

### Criar documentação de resultados

```text
Leia docs/04_DADOS_TREINAMENTO_E_MODELO.md e docs/05_REQUISITOS_E_FLUXOS.md. Crie um template em Markdown para registrar experimentos do ARGUS IC, incluindo dataset, modelo de detecção, modelo de profundidade, imagens testadas, métricas, exemplos de saída e limitações observadas.
```

## Ordem sugerida de implementação

1. Backend simulado.
2. Gerador de mensagem.
3. Detecção real com modelo pré-treinado.
4. Estimativa monocular de profundidade.
5. Integração detecção + profundidade + mensagem.
6. Flutter mínimo.
7. Registro de experimentos.
8. Treinamento ou ajuste fino, apenas se necessário.

## Critério para encerrar uma tarefa

Uma tarefa deve ser considerada concluída quando:

- tem código funcional;
- tem instrução de execução;
- respeita o escopo da IC;
- não introduz dependências desnecessárias;
- possui comentários suficientes para entendimento;
- atualiza a documentação quando altera comportamento.
