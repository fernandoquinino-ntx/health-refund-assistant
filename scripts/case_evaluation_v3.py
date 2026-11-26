#!/usr/bin/env python3
"""Ponto de entrada histórico para o avaliador real de extração."""

if __package__:
    from .case_evaluation import main
else:
    from case_evaluation import main


if __name__ == "__main__":
    main()
