"""Objetivo: verificar o controlador conversacional de tarefas de reembolso.

Entradas: mensagens, anexos simulados e estado anterior.
Processamento: classifica intenção, solicita entradas e executa o fluxo.
Saídas: asserções sobre estado, mensagens e evidências.
"""

import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

from health_refund_assistant.conversation.agent import (
    extrair_referencia_nota,
    handle_agent_turn,
    identificar_tarefa,
)
from health_refund_assistant.web.web_app import reset_agent_session
from health_refund_assistant.core.prompt_library import (
    analisar_secoes_prompt,
    carregar_respostas_agente,
    validar_prompt_padrao,
)


class AgentTaskTests(unittest.TestCase):
    def test_respostas_de_encaminhamento_vem_do_prompt_versionado(self):
        respostas = carregar_respostas_agente("v1.1")
        self.assertIn("aguardando_exportacao_pagamento", respostas)
        self.assertIn("categoria_nao_mapeada", respostas)

    def test_prompt_ativo_tem_entrada_tarefa_saida_guardrails(self):
        from pathlib import Path
        texto = (
            Path(__file__).resolve().parents[3]
            / "prompts/agente_conversacional/v1.0.md"
        ).read_text(encoding="utf-8")
        secoes = analisar_secoes_prompt(texto)
        self.assertEqual(
            set(secoes),
            {"Tarefa", "Entrada esperada", "Saída esperada", "Guardrails"},
        )
        self.assertTrue(validar_prompt_padrao(texto))

    def test_reset_limpa_exportacao_pendente(self):
        state = {
            "conversation": {"messages": ["antiga"], "evidence": {"x": 1}},
            "pending_pdf": b"pdf",
            "pending_image": b"imagem",
            "pending_export_paths": ["exportacao.json"],
        }
        reset_agent_session(state)
        self.assertEqual(state["conversation"]["messages"], [])
        self.assertIsNone(state["conversation"]["evidence"])
        self.assertNotIn("pending_pdf", state)
        self.assertNotIn("pending_image", state)
        self.assertNotIn("pending_export_paths", state)

    def test_classifica_pagamento_recebido(self):
        self.assertEqual(
            identificar_tarefa("Já recebi o reembolso da nota 1049"),
            "confirmar_pagamento",
        )
        self.assertEqual(extrair_referencia_nota("nota 1049"), "1049")

    def test_solicita_documento_para_confirmar_pagamento(self):
        result = handle_agent_turn(
            "Já recebi o reembolso da nota 1049",
            None,
            None,
        )
        self.assertEqual(result["state"]["status"], "aguardando_exportacao")
        self.assertIn("exportação", result["answer"].lower())

    def test_documento_sem_exportacao_solicita_exportacao(self):
        result = handle_agent_turn(
            "Analise esta nota",
            None,
            None,
            pdf_bytes=b"%PDF-test",
            export_paths=[],
        )
        self.assertEqual(
            result["state"]["status"],
            "aguardando_exportacao",
        )
        self.assertIn("exportação", result["answer"].lower())

    def test_documento_com_exportacao_conclui_fluxo(self):
        response = Mock()
        response.document_fields = {"numero_documento": "1049"}
        response.assessment = {"situacao_pedido": "localizado"}
        response.review = {"situacao_documental": "revisao_necessaria"}
        response.answer = "A análise foi concluída."
        with patch(
            "health_refund_assistant.conversation.agent.handle_request",
            return_value=response,
        ):
            result = handle_agent_turn(
                "Analise esta nota",
                None,
                None,
                pdf_bytes=b"%PDF-test",
                export_paths=[Path("exportacao.json")],
                reference_date=date(2026, 11, 26),
            )
        self.assertEqual(result["state"]["status"], "concluido")
        self.assertEqual(result["answer"], "A análise foi concluída.")
        self.assertEqual(result["evidence"]["documento"]["numero_documento"], "1049")

    def test_seguimento_usa_evidencia_existente(self):
        evidence = {
            "documento": {"numero_documento": "1049"},
            "conciliacao": {"situacao_pedido": "localizado"},
            "revisao_ia": {"situacao_documental": "revisao_necessaria"},
        }
        with patch(
            "health_refund_assistant.conversation.agent.create_assistant_answer",
            return_value="O pedido está localizado.",
        ):
            result = handle_agent_turn(
                "Qual é o status?",
                {"task": "consultar_status", "status": "concluido"},
                evidence,
            )
        self.assertEqual(result["answer"], "O pedido está localizado.")

    def test_tarefa_fora_do_catalogo_pede_esclarecimento(self):
        result = handle_agent_turn(
            "Conte uma piada sobre qualquer assunto",
            None,
            None,
        )
        self.assertEqual(result["state"]["task"], "categoria_nao_mapeada")
        self.assertEqual(result["state"]["status"], "aguardando_confirmacao")
        self.assertIn("tarefa", result["answer"].lower())


if __name__ == "__main__":
    unittest.main()
