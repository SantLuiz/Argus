# Experimento de visão local no aplicativo

Esta fase avalia a viabilidade técnica de inferência contínua no celular. É um experimento isolado: não altera o fluxo normal do ARGUS, não substitui a captura enviada ao backend, não remove a profundidade monocular e não muda o botão **Modo Porta**.

## Pergunta experimental

Comparar, no Redmi Note 10, dois detectores executados localmente:

| Candidato | Formato previsto | Entrada | Execução comum |
|---|---|---:|---|
| EfficientDet-Lite0 | TFLite INT8 da distribuição oficial | conforme manifesto do modelo | CPU, duas threads |
| YOLOv8n | TFLite FP32 exportado localmente | 320×320 | CPU, duas threads |

O executor usa `tflite_flutter 0.12.1`, processa no máximo um frame por vez, descarta frames enquanto estiver ocupado e limita as tentativas a cinco inferências por segundo. Pré-processamento, tensores de saída e pós-processamento devem seguir o manifesto de cada modelo; as saídas dos candidatos não são intercambiáveis. Para YOLO, o protocolo fixa confiança em 0,50 e NMS por classe com IoU 0,45.

Pesos não são baixados automaticamente como efeito do build normal. Origem, versão, licença, SHA-256, classes, tamanho, tensores e normalização devem constar em `models/mobile/benchmark_manifest.json` quando cada candidato for preparado. Pesos `.tflite`, APKs, logs e resultados gerados permanecem locais e não devem ser versionados.

## Contrato do estado da cena

O experimento mantém apenas um snapshot imutável do último frame processado:

- identificador e instante monotônico de captura do frame;
- para cada detecção: classe, confiança e caixa normalizada;
- coordenadas relativas à imagem já orientada, antes do recorte visual aplicado pelo preview;
- sem rastreamento, fusão ou inferência de movimento entre frames.

O snapshot expira quando sua idade é igual ou superior a um segundo. Resultado vazio substitui e limpa as detecções anteriores. Pausa da câmera, saída da tela ou erro do detector também invalida o estado; resultado tardio de um frame expirado não pode reaparecer na tela.

Bounding boxes servem apenas ao diagnóstico visual e acompanham a preferência de debug. Elas não são um recurso auditivo e não comprovam distância, altura física ou trajetória. A caixa de uma pessoa, por exemplo, não permite concluir sozinha a posição da cabeça; um objeto “silencioso” no último frame não permite inferir que está se movendo.

## Integração futura condicionada a decisão

Depois de escolhido e validado um modelo, uma futura ação **Listar Itens** poderá consultar uma cópia do snapshot ainda válido, sem novo upload:

- toque no controle;
- `Argus listar itens` no modo passivo;
- `listar itens` no push-to-talk.

Respostas previstas:

| Estado | Resposta auditiva prevista |
|---|---|
| Snapshot válido com detecções | Lista curta das classes presentes, sem distância |
| Snapshot válido e vazio | “Nenhum item identificado no momento” |
| Sem resultado recente | “Ainda não há uma análise local atualizada” |
| Detector indisponível | “Reconhecimento local indisponível” |

Essa ação ainda não faz parte do aplicativo normal. Sua integração depende de aprovação explícita do modelo, runtime, classes e orçamento de consumo. A distância continua pertencendo à análise remota com profundidade monocular.

## Inventário local auditado

Inspeção local em 24/09/2026, sem baixar ou modificar modelos:

| Caminho local | Papel | Situação observada |
|---|---|---|
| `models/yolo/yolov8n.pt` | detector geral COCO do backend | peso presente; não é o TFLite do experimento |
| `models/yolo/yoloe-11s-seg.pt` | modelo YOLOE/segmentação usado em experimentos do backend | peso presente; não é candidato móvel desta fase |
| `models/yolo/yolov8s-world.pt` | modelo open-vocabulary do backend | peso presente; não é candidato móvel desta fase |
| `models/torch/hub/checkpoints/midas_v21_small_256.pt` | profundidade monocular MiDaS | peso presente; continua no backend |
| `models/torch/hub/checkpoints/tf_efficientnet_lite3-b733e338.pth` | backbone/cache do MiDaS | peso presente, além de um download parcial homônimo; não confundir com EfficientDet-Lite0 |
| `models/mobile/benchmark_manifest.json` | contrato dos dois candidatos móveis | manifesto presente; artefatos `.tflite` ainda ausentes nesta inspeção |

As imagens de exemplo estão separadas pelo próprio nome: `[REAL]sala_de_aula.jpeg`, `[REAL]quarto.jpg` e `[REAL]corredor_piso_tátil.jpg` são declaradas como reais; `[IA]recepção.jpg`, `[IA]corredor_obstaculos.jpg` e `[IA]corredor_elevador.jpg` são declaradas como sintéticas. Essa convenção é evidência de origem informada no repositório, não auditoria externa da procedência.

## Classes e dados

Os modelos genéricos baseados nas 80 classes comuns do COCO permitem estudar o pipeline, mas não fornecem classes de porta, escada ou piso tátil. Renomear uma classe existente não cria suporte real.

| Categoria sugerida | Situação para este experimento | Limite e dados necessários |
|---|---|---|
| 1. Escada — subida | Não coberta pelo COCO comum | Exige cenas internas anotadas com direção/estrutura; uma bbox de escada não demonstra que ela sobe a partir da posição do usuário |
| 2. Escada — descida | Não coberta pelo COCO comum | Deve ser classe/estado separado da subida e exige exemplos do ponto de vista do usuário; não pode ser derivada apenas da mesma bbox |
| 3. Porta | Prioridade da evolução interna; não coberta pelo COCO comum | Precisa representar aberta, fechada e entreaberta, oclusões e diferentes ambientes; Open Images é um ponto de partida, não valida o domínio ARGUS |
| 4. Obstáculo em altura de cabeça | Não é uma classe única | Requer classe do objeto, geometria/câmera calibrada ou anotação explícita da zona de risco; bbox isolada não comprova altura física nem posição da cabeça |
| 5. Piso tátil / faixa de pedestre | São conceitos distintos e não cobertos pelo COCO comum | Separar piso tátil de alerta/direcional de faixa externa. Faixa de pedestre fica adiada porque o foco atual é ambiente interno |
| 6. Obstáculo dinâmico silencioso | Algumas classes, como bicicleta, existem no COCO, mas “silencioso” e movimento não | Exige sequência temporal/rastreamento e definição operacional de risco; snapshot de um frame não permite inferir movimento nem nível de ruído. Fica adiado nesta fase |
| 7. Degrau isolado / desnível abrupto | Não coberto pelo COCO comum | Exige dados próprios com distinção de pequenas irregularidades, perspectiva e risco; bbox não mede desnível físico |

O peso YOLO genérico pode ser trocado por configuração e há experimentos open-vocabulary no backend; isso não equivale a um modelo móvel validado para portas.

As imagens sintéticas ajudam na inspeção de fluxos, mas não podem fundamentar alegações de precisão em ambientes reais. Antes de treinar porta ou outras categorias, registrar fonte, licença, população de cenas, política de anonimização, rótulos e separação entre imagens reais e geradas. Esta fase não autoriza coleta nem treinamento.

### Candidato de dados para portas

O [Open Images V7](https://storage.googleapis.com/openimages/web/factsfigures_v7.html) oferece cerca de 16 milhões de bounding boxes em 600 classes e inclui `Door` entre as classes boxable. A [página oficial de download](https://storage.googleapis.com/openimages/web/download_v7.html) permite filtrar classes e splits, o que possibilita uma auditoria de um subconjunto antes de qualquer treinamento.

As anotações são CC BY 4.0. As imagens são listadas como CC BY 2.0, mas o próprio projeto alerta que a licença deve ser verificada individualmente. Uma próxima fase pode filtrar `Door`, preservar ID/autoria/licença por imagem, revisar manualmente interiores e estados da porta e montar splits sem vazamento de ambiente. Não baixar nem treinar esse conjunto nesta fase. Open Images não fornece automaticamente os estados aberta/fechada/entreaberta exigidos; esses rótulos precisariam de revisão/anotação própria.

## Protocolo no Redmi

Ambiente alvo: Redmi Note 10, Android 12, MIUI 14. Registre versão do APK, ABI, versão do Flutter/runtime, modelo e SHA-256. Mantenha brilho fixo, aparelho fora do carregador e condições iniciais semelhantes de bateria e temperatura.

Compare três condições:

1. preview de câmera sem inferência;
2. preview com EfficientDet-Lite0;
3. preview com YOLOv8n.

Faça 30 segundos de aquecimento e três rodadas de cinco minutos por condição. Registre, quando disponível:

- latência captura → resultado, p50 e p95;
- inferências por segundo e frames descartados;
- memória;
- tempo de frame da interface;
- bateria e temperatura no início/fim;
- falhas, encerramentos e crescimento de fila.

Repita uma comparação com debug/caixas ligado e desligado. Valide também funcionamento offline, rotação, pausa/retomada, câmera indisponível e chegada de resultado depois da expiração. STT não participa deste teste.

Um candidato técnico inicial deve manter p95 captura → resultado abaixo de um segundo, sem fila crescente nem travamento nas três rodadas. Esse limiar apenas permite recomendar uma próxima integração experimental; não comprova precisão, acessibilidade, segurança ou prontidão de produto. Não extrapole uma rodada curta para autonomia de um dia.

Resultados devem ficar em `results/mobile_benchmark/` e conter valores medidos ou `não medido`. Emulador pode validar contrato e layout, mas não representa desempenho do Redmi. A instalação e medição física permanecem pendentes até o responsável executá-las; não fabricar números ausentes.

## Critérios para a decisão seguinte

O relatório deve separar viabilidade do pipeline de qualidade semântica do modelo. A decisão final pertence ao responsável e precisa definir:

- runtime e modelo móvel definitivo, incluindo a opção de rejeitar ambos;
- peso capaz de detectar portas e origem dos dados;
- ordem e definição das categorias posteriores;
- frequência de inferência e limites aceitáveis de bateria/aquecimento;
- pesos incluídos no APK ou download prévio controlado.

Até essa decisão, a captura remota, o Modo Porta e a profundidade monocular permanecem como estão no aplicativo normal.
