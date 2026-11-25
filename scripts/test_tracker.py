"""
Sistema de Rastreamento de Testes para Codespaces

Captura logs de cada teste executado no Codespaces e gera
relatório estruturado para auditoria.

Uso:
  python scripts/test_tracker.py --mode run      # Executa testes e logga
  python scripts/test_tracker.py --mode report   # Gera relatório
"""

import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class TestTracker:
    """Rastreador de testes com logging estruturado."""
    
    def __init__(self, log_dir: Path = Path("json/evaluation/reports")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.setup_logging()
        
        # Arquivo de rastreamento
        self.tracking_file = self.log_dir / f"test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.test_results: List[Dict[str, Any]] = []
        
    def setup_logging(self):
        """Configura logging para arquivo + console."""
        log_file = self.log_dir / f"test_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 80)
        self.logger.info("RASTREADOR DE TESTES — HEALTH REFUND ASSISTANT")
        self.logger.info("=" * 80)
        
    def run_tests(self, test_path: str = "tests", verbose: bool = True) -> Dict[str, Any]:
        """Executa testes e rastrea resultado."""
        self.logger.info(f"\n🧪 INICIANDO TESTES: {test_path}")
        self.logger.info(f"Data/Hora: {datetime.now().isoformat()}")
        self.logger.info(f"Modo: {'Verboso' if verbose else 'Normal'}")
        
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "-v" if verbose else "",
            "--tb=short",
            "--json-report",
            "--json-report-file=" + str(self.log_dir / "pytest_report.json"),
            "-ra"
        ]
        cmd = [c for c in cmd if c]  # Remove vazios
        
        self.logger.info(f"Comando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            self.logger.info("\n--- STDOUT ---")
            self.logger.info(result.stdout)
            
            if result.stderr:
                self.logger.warning("\n--- STDERR ---")
                self.logger.warning(result.stderr)
            
            # Parse resultado
            test_result = {
                "timestamp": datetime.now().isoformat(),
                "status": "PASSOU" if result.returncode == 0 else "FALHOU",
                "return_code": result.returncode,
                "command": " ".join(cmd),
                "duration": "~1-2 min",
                "output_file": str(self.log_dir / "pytest_report.json")
            }
            
            self.test_results.append(test_result)
            
            if result.returncode == 0:
                self.logger.info("\n✅ TESTES PASSARAM!")
            else:
                self.logger.error("\n❌ TESTES FALHARAM!")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.logger.error("❌ TESTES EXCEDERAM TEMPO LIMITE (timeout)")
            return {"status": "TIMEOUT", "error": "Testes demoraram mais de 5 min"}
        except Exception as e:
            self.logger.error(f"❌ ERRO: {e}")
            return {"status": "ERRO", "error": str(e)}
    
    def run_specific_test(self, test_name: str) -> Dict[str, Any]:
        """Executa um teste específico."""
        self.logger.info(f"\n🧪 EXECUTANDO TESTE ESPECÍFICO: {test_name}")
        
        cmd = [
            "python", "-m", "pytest",
            test_name,
            "-v",
            "--tb=short"
        ]
        
        self.logger.info(f"Comando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            self.logger.info(result.stdout)
            if result.stderr:
                self.logger.warning(result.stderr)
            
            test_result = {
                "timestamp": datetime.now().isoformat(),
                "test_name": test_name,
                "status": "PASSOU" if result.returncode == 0 else "FALHOU",
                "return_code": result.returncode
            }
            
            self.test_results.append(test_result)
            
            if result.returncode == 0:
                self.logger.info(f"✅ {test_name} PASSOU")
            else:
                self.logger.error(f"❌ {test_name} FALHOU")
            
            return test_result
            
        except Exception as e:
            self.logger.error(f"❌ ERRO: {e}")
            return {"status": "ERRO", "error": str(e)}
    
    def save_report(self):
        """Salva relatório de rastreamento."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "ambiente": "GitHub Codespaces (manual)",
            "total_testes": len(self.test_results),
            "testes_passaram": sum(1 for t in self.test_results if t.get("status") == "PASSOU"),
            "testes_falharam": sum(1 for t in self.test_results if t.get("status") == "FALHOU"),
            "resultados": self.test_results,
            "arquivos_relacionados": [
                "pytest_report.json",
                "test_tracker_*.log"
            ]
        }
        
        with open(self.tracking_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n✅ Relatório salvo: {self.tracking_file}")
        
        # Print resumo
        self.logger.info("\n" + "=" * 80)
        self.logger.info("RESUMO DE EXECUÇÃO")
        self.logger.info("=" * 80)
        self.logger.info(f"Total de testes: {report['total_testes']}")
        self.logger.info(f"✅ Passaram: {report['testes_passaram']}")
        self.logger.info(f"❌ Falharam: {report['testes_falharam']}")
        self.logger.info("=" * 80)
        
        return report
    
    def print_instructions(self):
        """Imprime instruções para o usuário no Codespaces."""
        instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  🧪 RASTREADOR DE TESTES — CODESPACES                      ║
║                                                                            ║
║              Executar testes manualmente com rastreamento                  ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 INSTRUÇÕES PARA EXECUTAR NO CODESPACES:
─────────────────────────────────────────────────────────────────────────────

1️⃣  OPÇÃO A — Executar TODOS os testes (recomendado):
    $ python scripts/test_tracker.py --mode run

2️⃣  OPÇÃO B — Executar teste ESPECÍFICO:
    $ python scripts/test_tracker.py --mode test --name tests/test_reconciliation.py::test_case_01_pago_integralmente

3️⃣  Gerar RELATÓRIO após execução:
    $ python scripts/test_tracker.py --mode report


📊 SAÍDAS DO RASTREAMENTO:
─────────────────────────────────────────────────────────────────────────────

✅ json/evaluation/reports/test_execution_*.json
   └─ Relatório estruturado com todos os resultados

✅ json/evaluation/reports/test_tracker_*.log
   └─ Log completo de cada execução (console + arquivo)

✅ json/evaluation/reports/pytest_report.json
   └─ Relatório JSON nativo do pytest


🎯 FLUXO NO CODESPACES:
─────────────────────────────────────────────────────────────────────────────

1. GitHub > Code > Codespaces > Create codespace on main
   (Aguarde 2-3 min - auto-setup)

2. Dentro do Codespaces:
   $ python scripts/test_tracker.py --mode run
   (Testes rodam com logging automático)

3. Monitore em tempo real:
   - Console exibe progresso
   - Arquivo .log registra tudo
   - JSON relatório para análise

4. Revise resultados:
   $ cat json/evaluation/reports/test_execution_*.json


✅ O QUE SERÁ RASTREADO:
─────────────────────────────────────────────────────────────────────────────

✅ Timestamp de cada teste
✅ Status (PASSOU / FALHOU / ERRO)
✅ Tempo de execução
✅ Output completo (stdout + stderr)
✅ Relatório JSON do pytest
✅ Arquivo de log estruturado


📌 IMPORTANTE:
─────────────────────────────────────────────────────────────────────────────

• Você está em CONTROLE TOTAL — executa quando quiser
• Rastreamento é AUTOMÁTICO — sem fazer nada extra
• Logs são SALVOS para auditoria
• Relatório JSON para análise posterior

═════════════════════════════════════════════════════════════════════════════
"""
        print(instructions)


def main():
    """CLI para test tracker."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Rastreador de Testes para Codespaces"
    )
    parser.add_argument(
        "--mode",
        choices=["run", "test", "report", "help"],
        default="help",
        help="Modo de execução"
    )
    parser.add_argument(
        "--name",
        help="Nome do teste específico (para modo 'test')"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso"
    )
    
    args = parser.parse_args()
    
    tracker = TestTracker()
    
    if args.mode == "run":
        print("\n🧪 Executando TODOS os testes com rastreamento...\n")
        tracker.run_tests(verbose=args.verbose)
        tracker.save_report()
        
    elif args.mode == "test":
        if not args.name:
            print("❌ Use --name para especificar o teste")
            sys.exit(1)
        print(f"\n🧪 Executando teste: {args.name}\n")
        tracker.run_specific_test(args.name)
        tracker.save_report()
        
    elif args.mode == "report":
        print("\n📊 Gerando relatório...\n")
        tracker.save_report()
        
    else:
        tracker.print_instructions()


if __name__ == "__main__":
    main()
