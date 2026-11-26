# Checklist de funcionalidades

Consulte o [README](../README.md) para o fluxo e o
[status atual](00_status_auditoria.md) para limitações. Este checklist é um
roteiro de verificação, não uma afirmação de que os itens foram testados:

- [ ] Instalar as dependências e executar a suíte automatizada.
- [ ] Com dados sintéticos e API disponível, importar uma exportação com período,
  anexar um PDF e verificar extração, revisão e resposta.
- [ ] Verificar perguntas posteriores, memória local e exclusão da conversa.
- [ ] Verificar a estimativa de cinco dias úteis apenas quando aplicável.
- [ ] Conferir a extensão no navegador e a interface no ambiente de destino.

Não há autenticação, isolamento multiusuário ou criptografia da memória. Os testes
com mocks não comprovam execução da API, Codespaces, segurança ou elegibilidade.
