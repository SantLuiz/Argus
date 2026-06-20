# 02 - Escopo e limites da IC ARGUS

## Escopo principal

O escopo da IC é desenvolver uma base teórica e um protótipo experimental simples para um sistema de apoio à compreensão ambiental por pessoas com deficiência visual.

O sistema deve ser capaz de:

1. Capturar ou receber uma imagem de ambiente interno.
2. Aplicar processamento de imagem ou inferência de modelo.
3. Identificar objetos, obstáculos ou elementos relevantes.
4. Estimar a profundidade monocular da cena para indicar distância aproximada ou nível de proximidade dos objetos detectados.
5. Organizar a informação em uma frase curta.
6. Retornar essa frase por áudio.

## Ambiente de atuação

Priorizar ambientes internos, como:

- corredores;
- salas;
- portas;
- mesas;
- cadeiras;
- pessoas;
- objetos no caminho;
- recepções;
- escadas ou degraus quando houver dados suficientes.

Ambientes externos podem aparecer na revisão de literatura, mas não devem ser o foco prático da IC.

## Classes iniciais recomendadas

As classes podem variar conforme o dataset usado, mas para manter coerência com a IC e com as discussões do projeto, priorizar:

- pessoa;
- porta;
- mesa;
- cadeira;
- escada/degrau, se disponível;
- obstáculo genérico, se houver anotação própria;
- corredor ou passagem, se houver abordagem por classificação/segmentação;
- elevador/recepção apenas se existir base de dados própria ou anotação manual.

Para um protótipo simples, não é obrigatório detectar todas as classes. É melhor detectar poucas classes com clareza do que muitas classes com baixa confiabilidade.

## Escopo mínimo de implementação

A primeira versão aceitável pode conter:

- Upload de imagem pelo Flutter ou endpoint de teste no backend.
- API Python recebendo imagem.
- Inferência com modelo pré-treinado ou treinado de forma simples.
- Estimativa monocular de profundidade associada aos objetos detectados.
- Conversão das detecções e da proximidade estimada em texto em português.
- Leitura do texto por TTS no aplicativo.

Exemplo de saída:

> "Pessoa próxima à frente, mesa mais distante à direita e possível passagem livre à esquerda."

## Não escopo atual

Não faz parte da IC neste momento:

- Produto final pronto para uso real.
- Navegação autônoma completa.
- SLAM completo.
- Mapeamento 3D completo.
- Reconstrução 3D precisa do ambiente a partir da profundidade monocular.
- Medição métrica exata de distância sem calibração, validação ou margem de erro.
- Localização absoluta do usuário.
- Rastreamento robusto de destino até chegada.
- Cálculo de rota externo com GPS.
- Reconhecimento facial.
- Identificação nominal de pessoas.
- Testes com pessoas com deficiência visual sem protocolo formal.
- Arquitetura com múltiplos microserviços.
- Integração obrigatória com hardware especializado.

## Como tratar sugestão de rotas na IC

A documentação original menciona sugestão de trajetos acessíveis. Na IC, essa ideia deve ser tratada de forma teórica ou simplificada.

Formas aceitáveis:

- Descrever conceitualmente como rotas poderiam ser sugeridas.
- Simular rotas em um mapa simples e previamente definido.
- Priorizar frases de orientação local, como "obstáculo próximo à frente", "objeto distante à direita" ou "caminho livre à esquerda".
- Registrar a sugestão de rota completa como extensão futura.

Evitar implementar algoritmos complexos de navegação, mapeamento ou planejamento global de caminho.

## Estimativa monocular de profundidade

Mesmo mantendo a IC simples, a estimativa monocular de profundidade é requisito obrigatório do protótipo, pois permite enriquecer o feedback auditivo com noções de distância.

Formas aceitáveis de uso:

- gerar mapa de profundidade a partir de uma única imagem;
- associar a profundidade média/mediana da região da caixa delimitadora ao objeto detectado;
- classificar a proximidade em categorias como `próximo`, `médio` e `distante`;
- informar a distância como aproximada, evitando tom de precisão absoluta;
- registrar limitações do método em cada experimento.

A profundidade monocular deve ser usada como apoio à orientação auditiva, não como substituto de sensores especializados nem como garantia de segurança.

## Critérios para aceitar uma funcionalidade

Uma funcionalidade é adequada para a IC se:

- contribui para a prova de viabilidade;
- pode ser explicada academicamente;
- reduz incertezas técnicas do projeto;
- não exige uma infraestrutura grande;
- pode ser testada em ambiente controlado;
- gera resultado mensurável ou demonstrável.

Uma funcionalidade deve ser adiada se:

- exige muitos sensores;
- aumenta muito a complexidade;
- depende de coleta sensível;
- parece mais adequada ao TCC;
- transforma a IC em um produto final.
