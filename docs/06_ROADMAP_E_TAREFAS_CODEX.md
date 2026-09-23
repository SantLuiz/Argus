# 06 — Roadmap e manutenção do protótipo

## Entregue em código

- Backend FastAPI com health, readiness, upload, pipeline roteado e resposta para áudio.
- YOLO e MiDaS integrados; profundidade monocular continua obrigatória para a demonstração.
- App Flutter Android com câmera, configurações persistidas, TTS e controles acessíveis.
- Modos de voz e transcrição implementados, **com falha de reconhecimento ainda aberta no aparelho**.
- Testes Python/Dart, scripts de execução/build e documentação da codebase.

Código existente não equivale a validação experimental concluída. Leia [PENDENCIAS.md](PENDENCIAS.md) antes de afirmar que uma função funciona no dispositivo.

## Próximas etapas

1. Validar uma análise real de ambiente interno: registrar modelos, origem da profundidade, mensagem e tempo.
2. Validar acesso do celular ao backend e leitura da resposta por TTS.
3. Percorrer toda a interface com TalkBack, fonte ampliada e feedback por áudio.
4. Retomar o diagnóstico da voz quando solicitado, correlacionando logs Dart e nativos; não trocar motor de STT por suposição.
5. Registrar experimentos comparativos de detecção/profundidade e suas limitações.
6. Considerar treinamento customizado somente quando os dados do experimento mostrarem necessidade.

## Como preparar tarefas para modelos menores

Cada tarefa deve indicar objetivo, caminhos exatos, função afetada, mudança esperada, dependências e comando/resultado de aceite. Use o mapa de [CODEBASE.md](CODEBASE.md) para localizar os arquivos. Não solicitar genericamente “melhorar a arquitetura”.

Exemplo de tarefa de documentação: “Abra `docs/PENDENCIAS.md`, seção V01. Acrescente o horário, modo e texto da reprodução controlada; diferencie resultado nativo, transcrição Dart e ação executada. Aceite: cada conclusão possui log associado e nenhuma hipótese é descrita como causa confirmada.”

## Critério de conclusão

Uma tarefa termina quando atende ao pedido, mantém os limites da IC, passa nas verificações adequadas e atualiza a documentação. Declare o que não pôde ser validado. Não apagar testes ou reduzir critérios para obter uma execução verde.

Planos antigos foram preservados em [history/](history/README.md) apenas para rastreabilidade.
