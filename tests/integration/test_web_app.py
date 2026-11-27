"""Objetivo: verificar os fluxos da interface Streamlit.

Entradas: interações simuladas, dados de teste e dependências substituídas.
Processamento: exercita envio, conversa e apresentação na interface.
Saídas: asserções de sucesso ou falha para o runner de testes.
"""
import unittest
from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from health_refund_assistant.web import web_app
from health_refund_assistant.conversation.conversation_memory import load_conversation, save_conversation
from streamlit.testing.v1 import AppTest


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.auth_patcher = patch.object(
            web_app,
            "local_user_login",
            return_value="usuario_teste",
        )
        self.auth_patcher.start()

    def tearDown(self):
        self.auth_patcher.stop()

    def test_chat_starts_sem_uploader_permanente(self):
        with (
            patch.object(
                web_app,
                "conversation_path_for_user",
                return_value=Path("/tmp/conversa_chat.json"),
            ),
            patch.object(
                web_app,
                "load_conversation",
                return_value={"messages": [], "evidence": None},
            ),
            patch.object(web_app.st, "file_uploader", return_value=None) as uploader,
        ):
            app = AppTest.from_file(
                str(Path(__file__).resolve().parents[2] / "app.py"),
            )
            app.run()
            self.assertFalse(app.exception)
            self.assertFalse(uploader.called)

    def test_prompt_selector_discovers_versions_in_numerical_order(self):
        extraction_versions = web_app.prompt_versions(
            web_app.PROMPTS_DIR / "vlm_extractor"
        )
        assistant_versions = web_app.prompt_versions(
            web_app.ASSISTANT_PROMPTS_DIR
        )

        self.assertEqual(
            extraction_versions,
            ["v1.0", "v1.1", "v2.0", "v3.0", "v4.0", "v4.1", "v4.2"],
        )
        self.assertEqual(assistant_versions, ["v1.0", "v1.1", "v1.2"])

    def test_chat_saves_analysis_from_agent_result(self):
        response = SimpleNamespace(
            document_fields={
                "valor_total": 100,
                "evidencias_literais": {"valor_total": "Total R$ 100,00"},
            },
            assessment={
                "situacao_pedido": "nao_localizado_nas_exportacoes",
                "situacao_prazo": "indeterminado",
                "data_referencia": "2026-11-25",
                "data_base_prazo": None,
                "origem_data_base_prazo": None,
                "dias_desde_atendimento_ou_emissao": None,
                "aviso_prazo": "Prazo simulado.",
                "campos_incompletos": [],
                "periodo_dos_datasets_cobre_data_base": None,
                "erros_exportacao": [],
                "candidatos": [],
            },
            review={
                "situacao_documental": "revisao_necessaria",
                "justificativa": "Revisar campos.",
                "campos_para_revisao": ["data_emissao"],
                "orientacoes": [],
            },
            answer="Não localizado.",
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            with (
                patch.object(web_app, "conversation_path_for_user", return_value=path),
                patch.object(web_app, "handle_agent_turn", return_value={
                    "answer": "Não localizado.",
                    "evidence": {
                        "documento": response.document_fields,
                        "conciliacao": response.assessment,
                        "revisao_ia": response.review,
                    },
                    "state": {"task": "analisar_documento", "status": "concluido", "missing": []},
                }) as handler,
            ):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py"), default_timeout=30)
                app.run()
                app.chat_input[0].set_value("Este pedido foi pago?").run()
                self.assertFalse(app.exception)
                self.assertEqual(load_conversation(path)["evidence"]["documento"]["valor_total"], 100)
                self.assertEqual(
                    load_conversation(path)["evidence"]["documento"]["evidencias_literais"]["valor_total"],
                    "Total R$ 100,00",
                )
                self.assertEqual(load_conversation(path)["messages"][-1]["content"], "Não localizado.")

    def test_follow_up_is_displayed_and_persisted_without_new_pdf(self):
        assessment = {
            "situacao_pedido": "nao_localizado_nas_exportacoes",
            "situacao_prazo": "indeterminado",
            "data_referencia": "2026-11-25",
            "data_base_prazo": None,
            "origem_data_base_prazo": None,
            "dias_desde_atendimento_ou_emissao": None,
            "aviso_prazo": "Prazo simulado.",
            "campos_incompletos": [],
            "periodo_dos_datasets_cobre_data_base": None,
            "erros_exportacao": [],
            "candidatos": [],
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            save_conversation(
                [{"role": "user", "content": "Primeira pergunta"}],
                {
                    "documento": {"valor_total": 100},
                    "conciliacao": assessment,
                    "revisao_ia": {
                        "situacao_documental": "revisao_necessaria",
                        "justificativa": "Revisar campos.",
                        "campos_para_revisao": ["data_emissao"],
                        "orientacoes": [],
                    },
                },
                path,
            )
            with (
                patch.object(web_app, "conversation_path_for_user", return_value=path),
                patch("health_refund_assistant.conversation.agent.create_assistant_answer", return_value="Ainda não localizado.") as answer,
            ):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py"))
                app.run()
                self.assertFalse(app.exception)
                app.chat_input[0].set_value("E o status?").run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.chat_message), 3)
                self.assertEqual(load_conversation(path)["messages"][-1]["content"], "Ainda não localizado.")
                self.assertEqual(answer.call_args.args[0], "E o status?")

    def test_new_conversation_requires_document(self):
        with (
            patch.object(
                web_app,
                "conversation_path_for_user",
                return_value=Path("/tmp/conversa_teste.json"),
            ),
            patch.object(web_app, "load_conversation", return_value={"messages": [], "evidence": None}),
            patch("health_refund_assistant.conversation.agent.create_assistant_answer") as answer,
        ):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py"))
            app.run()
            app.chat_input[0].set_value("Qual o status?").run()
            self.assertFalse(app.exception)
            answer.assert_not_called()

    def test_follow_up_recalculates_estimate_with_selected_reference_date(self):
        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                value = cls(2026, 3, 30)
                return value if tz is None else value.replace(tzinfo=tz)
        assessment = {
            "situacao_pedido": "localizado",
            "situacao_prazo": "fora_do_prazo_simulado",
            "data_referencia": "2026-03-20",
            "data_base_prazo": "2026-01-01",
            "origem_data_base_prazo": "data_atendimento",
            "dias_desde_atendimento_ou_emissao": 78,
            "aviso_prazo": "Prazo simulado.",
            "campos_incompletos": [],
            "periodo_dos_datasets_cobre_data_base": True,
            "erros_exportacao": [],
            "ids_com_registros_conflitantes": [],
            "candidatos": [{
                "claim_number": "1", "beneficiary": "Teste", "provider": "Teste",
                "portal_status": "Em análise", "financial_status": "em_analise",
                "requested_amount": 100, "paid_amount": None, "payment_date": None,
                "request_date": "2026-03-20", "match_confidence": "forte", "strong": True,
            }],
        }
        review = {
            "situacao_documental": "revisao_necessaria",
            "justificativa": "Revisar campos.",
            "campos_para_revisao": [],
            "orientacoes": [],
        }
        estimate = {
            "data_submissao": "2026-03-20", "data_referencia": "2026-03-30",
            "data_estimada": "2026-03-27", "dias_uteis_restantes": 0,
            "dias_uteis_atraso": 1, "situacao": "prazo_ultrapassado",
        }
        with TemporaryDirectory() as directory:
            path = Path(directory) / "conversa.json"
            save_conversation([], {"documento": {}, "conciliacao": assessment, "revisao_ia": review}, path)
            with (
                patch.object(web_app, "conversation_path_for_user", return_value=path),
                patch.object(web_app, "datetime", FixedDateTime),
                patch("health_refund_assistant.conversation.estimativa_pagamento.request_structured_json", return_value=estimate),
                patch("health_refund_assistant.conversation.agent.create_assistant_answer", return_value="Estimativa.") as answer,
            ):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py"), default_timeout=30)
                app.run()
                app.chat_input[0].set_value("Quanto tempo falta?").run()
                self.assertFalse(app.exception)
                saved = load_conversation(path)["evidence"]["conciliacao"]
                self.assertEqual(saved["estimativa_pagamento"]["dias_uteis_atraso"], 1)
                self.assertEqual(saved["estimativa_pagamento"]["data_referencia"], "2026-03-30")
                self.assertEqual(saved["situacao_prazo"], "nao_aplicavel_pedido_localizado")
                self.assertEqual(answer.call_args.args[1]["conciliacao"], saved)

    def test_old_analysis_without_review_cannot_generate_follow_up(self):
        assessment = {
            "situacao_pedido": "periodo_nao_coberto",
            "situacao_prazo": "indeterminado",
            "data_referencia": "2026-11-25",
            "data_base_prazo": None,
            "origem_data_base_prazo": None,
            "dias_desde_atendimento_ou_emissao": None,
            "aviso_prazo": "Prazo simulado.",
            "campos_incompletos": [],
            "periodo_dos_datasets_cobre_data_base": False,
            "erros_exportacao": [],
            "candidatos": [],
        }
        with (
            patch.object(
                web_app,
                "conversation_path_for_user",
                return_value=Path("/tmp/conversa_teste_old.json"),
            ),
            patch.object(web_app, "load_conversation", return_value={
                "messages": [], "evidence": {"documento": {}, "conciliacao": assessment}
            }),
            patch("health_refund_assistant.conversation.agent.create_assistant_answer") as answer,
        ):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py"))
            app.run()
            app.chat_input[0].set_value("É elegível?").run()
            self.assertFalse(app.exception)
            answer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
