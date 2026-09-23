# Resultados dos experimentos

Saídas geradas permanecem locais e são ignoradas pelo Git. Este README é versionado para explicar como registrar e reproduzir experimentos.

Para cada experimento, crie um diretório com identificação/data e um resumo contendo:

- objetivo e imagem/dataset de origem;
- commit, ambiente, modelos e parâmetros;
- número de execuções e aquecimentos;
- detecções, `depth_source`, tempos e mensagem produzida;
- resultado esperado versus observado e limitações;
- cuidados com anonimização antes de compartilhar imagens ou logs.

`benchmark_api.py` preserva a saída histórica em `results/curl_runner/`; `benchmark_routed_detection.py` escreve em `results/evaluation/`. Nomes de pastas existentes não indicam que resultados foram reexecutados após uma alteração.

Não apresentar fallback como profundidade real nem inferir distância em metros de valores relativos. Para publicar um experimento, revisar e selecionar explicitamente somente material apropriado, sem liberar toda esta pasta no Git.
