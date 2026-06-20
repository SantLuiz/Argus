# 01 - Contexto da Iniciação Científica ARGUS

## Visão geral

O projeto ARGUS é uma Iniciação Científica em Ciência da Computação voltada à aplicação de visão computacional e inteligência artificial em tecnologia assistiva. A proposta investiga como imagens capturadas por câmera podem ser processadas para identificar elementos relevantes do ambiente, estimar distância aproximada por profundidade monocular e converter essas informações em descrições ou orientações auditivas para pessoas com deficiência visual.

A motivação central é que muitos ambientes foram projetados para pessoas com percepção visual plena. Mesmo com recursos como placas em braile, piso tátil e sistemas de audiodescrição, a disponibilidade e a qualidade desses recursos ainda são irregulares. Nesse cenário, uma solução móvel baseada em câmera e IA pode atuar como apoio à compreensão do ambiente.

## Natureza da IC

Esta IC deve ser entendida como uma pesquisa de viabilidade, não como uma entrega final de produto. O foco principal é:

- fundamentação teórica;
- revisão de literatura;
- definição de arquitetura conceitual;
- estudo de técnicas de processamento de imagens e aprendizado de máquina;
- protótipo demonstrativo simples;
- estimativa monocular de profundidade como requisito obrigatório para apoiar a noção de distância até objetos;
- análise de limitações e possibilidades futuras.

A parte prática deve existir, mas de forma proporcional ao estágio de IC. Como a parte mais complexa de navegação assistida será desenvolvida no TCC, aqui o protótipo deve ter a função de demonstrar que a ideia é possível.

## Objetivo geral ajustado para a IC

Desenvolver e documentar uma proposta tecnológica baseada em visão computacional e inteligência artificial capaz de identificar objetos ou obstáculos em ambientes internos, estimar sua distância aproximada por profundidade monocular e transformar essas informações em feedback auditivo acessível, demonstrando a viabilidade da abordagem para apoio à mobilidade e compreensão ambiental de pessoas com deficiência visual.

## Objetivos específicos

- Levantar os principais desafios enfrentados por pessoas cegas ou com baixa visão em ambientes internos e urbanos.
- Estudar tecnologias assistivas já existentes e suas limitações.
- Analisar técnicas de processamento digital de imagens, detecção de objetos e aprendizado de máquina aplicáveis ao problema.
- Definir uma arquitetura simples com frontend Flutter e backend Python.
- Utilizar datasets públicos, como COCO e Open Images, e eventualmente bases anotadas no Roboflow.
- Implementar ou preparar um protótipo capaz de detectar objetos/obstáculos em imagens de ambiente interno.
- Integrar estimativa monocular de profundidade para classificar objetos por proximidade ou distância aproximada.
- Converter o resultado da detecção e da profundidade em uma mensagem curta e objetiva em português.
- Emitir essa mensagem por áudio ao usuário.
- Registrar limitações, métricas básicas e possíveis extensões futuras.

## Diferença entre IC e TCC

| Aspecto | IC ARGUS | TCC |
|---|---|---|
| Nome | Usa o nome ARGUS | Não usar ARGUS como nome principal |
| Foco | Pesquisa, teoria, viabilidade e protótipo simples | Desenvolvimento mais prático e completo |
| Frontend | Flutter | Pode seguir arquitetura própria do TCC |
| Backend | Python | Pode seguir arquitetura amadurecida do TCC |
| Navegação | Demonstração simples e conceitual, com distância aproximada por profundidade monocular | Navegação assistida mais estruturada |
| Rotas | Sugestão conceitual ou baseada em ambiente previamente mapeado | Fluxo mais completo de destino, rastreamento e orientação |
| Validação | Técnica e experimental | Técnica/funcional mais detalhada |

## Princípio orientador

A IC deve demonstrar que a proposta é plausível: **detectar algo relevante no ambiente interno, estimar sua proximidade/distância por profundidade monocular e comunicar isso por áudio**. Todo o restante deve ser tratado como extensão, discussão teórica ou preparação para trabalhos futuros.
