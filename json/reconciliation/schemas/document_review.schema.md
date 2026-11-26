# Revisão consultiva do documento

O [schema](./document_review.schema.json) define a saída da tarefa de revisão por
IA. A entrada inclui a imagem da primeira página, a pergunta, os campos extraídos
e as evidências calculadas. O resultado indica incertezas e campos para revisão;
não é decisão contratual nem confirmação de pagamento.

A aplicação valida a estrutura e exige `nao_e_possivel_avaliar` quando faltam
campos essenciais ou a imagem foi considerada ilegível. Essas verificações não
comprovam que o conteúdo gerado esteja correto.
