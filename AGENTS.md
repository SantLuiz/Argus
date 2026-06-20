# Instruções para Codex - Projeto ARGUS IC

## Identidade do projeto

Este repositório pertence ao projeto **ARGUS - Sistema Integrado de Visão Computacional e Inteligência Artificial para Descrição do Ambiente e Sugestão de Rotas para Pessoas com Deficiência Visual**, desenvolvido no contexto de **Iniciação Científica** da UNIP.

Use o nome **ARGUS** neste repositório, pois o foco aqui é a Iniciação Científica. Não confundir com o TCC, que possui escopo mais prático e deve ser tratado separadamente.

## Prioridade atual

A prioridade deste repositório é apoiar uma pesquisa de IC com foco mais **teórico, experimental e demonstrativo** do que produtivo.

O objetivo prático mínimo é provar a viabilidade da proposta:

> Capturar uma imagem ou fluxo de câmera em ambiente interno, detectar objetos/obstáculos relevantes, estimar sua distância aproximada por profundidade monocular e retornar uma orientação ou descrição em áudio para o usuário.

Não trate este projeto como uma aplicação comercial completa. Evite transformar tarefas simples em sistemas complexos sem necessidade.

## Diretrizes obrigatórias

1. O frontend deve ser pensado em **Flutter**.
2. O backend deve ser pensado em **Python**.
3. A visão computacional deve priorizar tecnologias citadas nos documentos da IC: OpenCV, TensorFlow, scikit-image, datasets COCO e Open Images.
4. Quando for necessário complementar ferramentas de treinamento ou hospedagem, podem ser usadas decisões amadurecidas no TCC: Roboflow, Google Colab, Ultralytics YOLO, PyTorch/TensorFlow, Git/GitHub, Docker e Oracle Cloud Infrastructure, desde que isso não amplie indevidamente o escopo da IC.
5. O sistema deve priorizar **ambientes internos**.
6. A estimativa monocular de profundidade é **requisito obrigatório** do protótipo, pois será usada para orientar o usuário sobre distância aproximada até objetos/obstáculos detectados.
7. A saída principal para o usuário deve ser **auditiva**.
8. O código e a documentação devem ser escritos de forma clara, simples e rastreável.
9. Comentários e documentação podem ficar em português brasileiro.
10. Nomeie funções, classes e arquivos de forma consistente e compreensível.
11. Sempre que houver dúvida entre uma solução simples e uma solução sofisticada, prefira a solução simples compatível com a proposta da IC.

## O que o Codex deve evitar

Não implementar, a menos que seja explicitamente pedido:

- SLAM completo.
- Mapeamento 3D completo do ambiente.
- Tratar a profundidade monocular como medição métrica exata sem calibração ou validação.
- Navegação externa complexa.
- Reconhecimento facial.
- Coleta de dados sensíveis sem anonimização.
- Testes diretos com pessoas com deficiência visual sem aprovação e planejamento ético.
- Arquitetura de microserviços complexa.
- Dependência obrigatória de sensores especializados, como LiDAR, câmera estéreo ou hardware dedicado.
- Uma aplicação final com pretensão de uso real sem validação.

## Documentos que devem ser lidos antes de alterar o projeto

1. `docs/01_CONTEXTO_IC_ARGUS.md`
2. `docs/02_ESCOPO_E_LIMITES.md`
3. `docs/03_ARQUITETURA_TECNICA.md`
4. `docs/04_DADOS_TREINAMENTO_E_MODELO.md`
5. `docs/05_REQUISITOS_E_FLUXOS.md`
6. `docs/06_ROADMAP_E_TAREFAS_CODEX.md`
7. `docs/07_FONTES_E_DECISOES.md`

## Regra de alinhamento com a IC

Antes de propor ou implementar qualquer nova funcionalidade, verifique se ela responde a pelo menos uma destas perguntas:

- Ajuda a demonstrar a viabilidade da detecção de objetos/obstáculos?
- Ajuda a transformar uma detecção visual e sua distância aproximada em informação auditiva compreensível?
- Ajuda a organizar o experimento, registrar resultados ou documentar a pesquisa?
- Ajuda a manter o projeto simples, reproduzível e coerente com a IC?

Se a resposta for não, a funcionalidade provavelmente pertence ao TCC ou a trabalhos futuros, não à IC atual.
