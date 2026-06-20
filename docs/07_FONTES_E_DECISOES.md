# 07 - Fontes internas e decisões adotadas

Este documento registra de onde vieram as principais decisões usadas no pacote de contexto para Codex.

## Fontes consideradas

### ARGUS - Relatório Semestral IC

Usado como fonte principal para:

- nome do projeto ARGUS;
- caráter de Iniciação Científica;
- proposta de auxiliar locomoção e compreensão do ambiente;
- uso de visão computacional e aprendizado de máquina;
- divisão em módulos de captação/processamento e feedback por IA;
- foco no primeiro módulo durante o relatório semestral;
- pipeline de pré-processamento com OpenCV, scikit-image, RGB, redimensionamento, Gaussian Blur, CLAHE e normalização;
- uso do formato COCO;
- preocupação com métricas, precisão, tempo de resposta e clareza na comunicação.

### DOCUMENTAÇÃO_PROJETO_IC_IA+INTELIGENCIA_ARTIFICIAL

Usado como fonte principal para:

- justificativa social e acadêmica;
- ideia de ferramenta como guia em locais sem acessibilidade adequada;
- identificação, descrição e sugestão de trajetos por feedback auditivo;
- uso de datasets pré-existentes;
- uso de OpenCV, TensorFlow, COCO, Open Images, Google Speech-to-Text e gTTS;
- integração com aplicação acessível;
- foco na contribuição científica e inclusão social.

### PDF BANCA - DOC TCC

Usado apenas como fonte complementar quando os documentos da IC não detalhavam suficientemente ferramentas de treinamento, hospedagem ou arquitetura amadurecida.

Aproveitado com adaptações:

- Roboflow para anotação e organização de datasets;
- Google Colab para treinamento;
- Ultralytics YOLO como alternativa prática para detecção;
- PyTorch/TensorFlow como frameworks possíveis;
- SQLite/PostgreSQL como possibilidades de persistência;
- Docker, Git e GitHub para reprodutibilidade;
- Oracle Cloud Infrastructure Always Free para hospedagem experimental;
- modelos multimodais como possibilidade futura ou complementar;
- estimativa monocular de profundidade como requisito obrigatório ajustado por decisão posterior do projeto.

Itens do TCC que **não** foram adotados como obrigação da IC:

- Node.js como backend, pois o usuário definiu Python para a IC;
- React/React Native como frontend, pois o usuário definiu Flutter para a IC;
- navegação completa orientada a destino;
- rastreamento contínuo avançado;
- arquitetura mais próxima de produto final.

## Decisões consolidadas

### Decisão 1 - IC mais teórica que prática

A IC deve priorizar pesquisa, revisão de literatura, documentação e prova de viabilidade. O protótipo existe para apoiar a hipótese, não para ser um produto completo.

### Decisão 2 - Flutter no frontend

Mesmo que outros documentos mencionem tecnologias web, neste pacote o frontend da IC foi definido como Flutter por solicitação explícita do usuário.

### Decisão 3 - Python no backend

O backend da IC deve ser Python, preferencialmente com FastAPI por simplicidade. Node.js fica fora da arquitetura principal da IC.

### Decisão 4 - Demonstração mínima

A entrega prática mínima deve mostrar o fluxo:

```text
imagem -> detecção + profundidade monocular -> mensagem -> áudio
```

### Decisão 5 - Ferramentas de treinamento

Priorizar:

- COCO/Open Images para base pública;
- Roboflow para anotação se houver dataset próprio;
- Google Colab para treinamento;
- YOLO leve ou TensorFlow/PyTorch para detecção.

### Decisão 6 - Profundidade monocular obrigatória

Mesmo com a IC sendo mais simples que o TCC, a estimativa monocular de profundidade passa a ser requisito obrigatório. Ela será usada para orientar o usuário sobre distância aproximada até objetos/obstáculos detectados.

Essa decisão não transforma a IC em SLAM, mapeamento 3D ou navegação completa. A profundidade deve ser tratada como estimativa relativa/aproximada e comunicada com termos como `próximo`, `médio`, `distante` ou `aproximadamente`.

### Decisão 7 - Hospedagem

Rodar localmente é suficiente para a IC. OCI Always Free pode ser usada para demonstração remota ou documentação de viabilidade.

### Decisão 8 - Limites éticos

Evitar testes com pessoas com deficiência visual sem protocolo formal. Evitar armazenar imagens sensíveis. O sistema deve ser apresentado como protótipo acadêmico, não como substituto de tecnologias assistivas consolidadas.

## Frase de alinhamento para o projeto

> O ARGUS, no contexto da Iniciação Científica, busca demonstrar a viabilidade de transformar informações visuais de ambientes internos em feedback auditivo acessível, combinando detecção de objetos, estimativa monocular de profundidade, inteligência artificial e uma arquitetura simples baseada em Flutter e Python.
