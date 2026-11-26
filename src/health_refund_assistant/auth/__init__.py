"""Objetivo: expor autenticação local simples do assistente.

Entradas: identificador e PIN local.
Processamento: delega criação e validação ao módulo de autenticação.
Saídas: usuário autorizado ou recusa segura.
"""

from .local_auth import add_local_user, validate_local_user

__all__ = ["add_local_user", "validate_local_user"]
