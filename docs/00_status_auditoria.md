# Status do assistente

Atualizado em 25/11/2026.

## Fluxo implementado

- Interface de conversa com pergunta e anexo PDF; uma exportação do plano é exigida
  para analisar um documento novo.
- Extração por VLM com contrato JSON, avaliação e conciliação em Python, revisão
  consultiva por IA e resposta estruturada em JSON. As saídas precisam de revisão
  humana e podem conter erros.
- Memória persistente **local e individual** das últimas 50 mensagens e da última
  análise. Perguntas posteriores usam as evidências armazenadas, sem atualizar o
  status automaticamente. A barra lateral permite apagar a memória.

## Limitações e pendências

- Não há autenticação, isolamento multiusuário, criptografia da memória ou garantia
  contra prompt injection. Use somente ambiente privado e dados sintéticos para testes.
- A aplicação usa 30 dias como prazo **simulado**. As regras D-2 e 365 dias citadas
  em documentos anteriores não estão implementadas no fluxo atual. A elegibilidade
  contratual é indeterminada, pois as regras do plano não foram verificadas.
- A disponibilidade de `gpt-6-luna` pela API e a execução real no Codespaces
  precisam ser verificadas com o provedor e o ambiente do grupo.
- Apagar a memória não apaga exportações importadas nem dados enviados à API.
- Relatórios de avaliação real e rastreamento de testes da UI não são gerados por
  esta funcionalidade de memória.
- O antigo `scripts/case_evaluation_v3.py` gerava afirmações fixas, sem executar
  o modelo; seus relatórios não comprovam resultados reais. Agora o comando chama
  o avaliador real de extração.

Para executar e consultar as instruções de privacidade, veja o
[README](../README.md). Os [casos de memória](70_documentation/06_casos_teste_memory.md)
são propostas: não comprovam autenticação ou isolamento implementados.
