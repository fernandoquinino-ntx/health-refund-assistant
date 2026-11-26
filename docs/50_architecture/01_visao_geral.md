# Visão geral da arquitetura

A aplicação Streamlit recebe a pergunta, o PDF e uma exportação do plano. O
orquestrador chama a extração visual, valida os dados e compara evidências com a
exportação. Tarefas de IA revisam o documento, estimam processamento quando
aplicável e produzem resposta estruturada; o código confere os contratos e a
estimativa. O resultado é consultivo e requer revisão humana.

A extensão de navegador exporta dados para um arquivo JSON; o usuário o importa
na interface. Ela não é um backend da aplicação. A memória é local e individual,
sem autenticação ou isolamento multiusuário.

Veja [estrutura e código](../70_documentation/04_estrutura_projeto.md),
[contratos JSON](../70_documentation/05_json_catalogo.md) e
[README](../../README.md). As arquiteturas de agente e integração futuras são
propostas separadas, não recursos já implementados.
