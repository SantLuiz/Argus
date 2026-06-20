# 05 - Requisitos e fluxos da IC ARGUS

## Requisitos funcionais

### RF01 - Captura ou envio de imagem

O sistema deve permitir que o usuário capture uma imagem pelo app Flutter ou envie uma imagem de teste ao backend.

### RF02 - Processamento da imagem

O backend Python deve receber a imagem e prepará-la para análise por modelo de visão computacional.

### RF03 - Detecção de objetos ou obstáculos

O sistema deve detectar objetos relevantes em ambiente interno, retornando classe, confiança e caixa delimitadora quando aplicável.

### RF04 - Classificação espacial simples

O sistema deve estimar a posição aproximada do objeto na imagem:

- esquerda;
- centro;
- direita.

Opcionalmente:

- superior;
- inferior.

### RF05 - Estimativa monocular de profundidade

O sistema deve executar estimativa monocular de profundidade como requisito obrigatório do protótipo. A profundidade deve ser usada para indicar proximidade ou distância aproximada dos objetos detectados.

A resposta deve incluir, quando possível:

- valor relativo de profundidade;
- categoria de proximidade, como `próximo`, `médio` ou `distante`;
- indicação textual em português para compor a mensagem auditiva.

Não tratar essa informação como distância exata em metros sem calibração e validação.

### RF06 - Geração de mensagem textual

O sistema deve transformar as detecções em uma frase curta em português.

### RF07 - Feedback auditivo

O aplicativo deve reproduzir a mensagem gerada por TTS.

### RF08 - Registro de teste

O sistema deve permitir registrar, ao menos em arquivo, os resultados dos testes:

- data/hora;
- imagem ou nome do arquivo;
- objetos detectados;
- confiança;
- proximidade/distância estimada;
- tempo de processamento;
- mensagem gerada.

## Requisitos não funcionais

### RNF01 - Simplicidade

A implementação deve ser simples o bastante para ser explicada em relatório acadêmico.

### RNF02 - Reprodutibilidade

As etapas de treinamento, inferência e teste devem ser documentadas.

### RNF03 - Baixo custo

Priorizar ferramentas gratuitas, open source ou com camada gratuita.

### RNF04 - Acessibilidade

A interface Flutter deve considerar:

- botões grandes;
- labels semânticos;
- compatibilidade com leitores de tela;
- retorno por áudio;
- mínima dependência de elementos visuais.

### RNF05 - Privacidade

Evitar armazenar imagens com pessoas identificáveis. Se imagens próprias forem usadas, registrar cuidados de anonimização e finalidade acadêmica.

### RNF06 - Transparência

O sistema não deve apresentar suas saídas como infalíveis. Mensagens devem deixar claro quando a distância for aproximada. Usar termos como "detectado", "possível", "próximo", "mais distante" ou "aproximadamente" quando necessário.

## Fluxo principal

```text
1. Usuário abre o app Flutter.
2. App solicita permissão de câmera.
3. Usuário captura imagem ou aciona análise.
4. App envia imagem ao backend Python.
5. Backend processa imagem.
6. Modelo detecta objetos.
7. Modelo de profundidade monocular estima a profundidade da cena.
8. Backend associa proximidade/distância aproximada aos objetos detectados.
9. Backend organiza detecções por prioridade.
10. Backend gera mensagem curta.
11. App recebe mensagem.
12. App reproduz mensagem por áudio.
```

## Fluxo de teste sem app

Para facilitar a IC, deve ser possível testar o backend sem o Flutter.

```text
1. Desenvolvedor envia imagem via Swagger, Postman ou script Python.
2. Backend executa detecção e estimativa monocular de profundidade.
3. Backend retorna JSON com detecções e proximidade estimada.
4. Desenvolvedor registra resultado em `results/`.
```

## Priorização de mensagens

Quando houver muitos objetos, o sistema deve evitar narrar tudo. Priorizar:

1. Obstáculos próximos e diretamente à frente.
2. Pessoas próximas no centro da imagem.
3. Escadas/degraus.
4. Portas/passagens.
5. Objetos laterais.
6. Demais objetos de contexto.

## Exemplo de conversão de detecção para áudio

Entrada:

```json
{
  "detections": [
    {"class_name": "person", "confidence": 0.91, "bbox": [210, 50, 400, 520], "proximity": "próximo"},
    {"class_name": "chair", "confidence": 0.74, "bbox": [20, 250, 160, 500], "proximity": "distante"}
  ]
}
```

Saída textual:

```text
Pessoa próxima à frente, na região central. Cadeira mais distante à esquerda.
```

Áudio:

```text
"Pessoa próxima à frente, na região central. Cadeira mais distante à esquerda."
```

## Critérios de aceite do protótipo

Um protótipo inicial da IC é aceitável se:

- recebe imagem;
- executa detecção;
- executa estimativa monocular de profundidade;
- retorna JSON compreensível com classe, posição e proximidade estimada;
- gera mensagem em português incluindo distância aproximada quando aplicável;
- reproduz ou permite reproduzir essa mensagem em áudio;
- possui documentação de como rodar;
- registra limitações conhecidas.
