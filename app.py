"""Objetivo: iniciar a interface do assistente.

Entradas: configuração e interação fornecidas à interface Streamlit.
Processamento: delega a execução ao módulo web da aplicação.
Saídas: interface interativa e resultados apresentados por ela.
"""

from health_refund_assistant.web.web_app import main


if __name__ == "__main__":
    main()
