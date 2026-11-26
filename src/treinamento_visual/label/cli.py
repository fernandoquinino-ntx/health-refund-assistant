"""Objetivo: preparar tarefas locais e iniciar o Label Studio.

Entradas: páginas e manifestos OCR locais, argumentos e ambiente do processo.
Processamento: cria referências locais ou inicia a interface com telemetria desativada.
Saídas: tarefas privadas, execução do Label Studio ou mensagem de erro.
"""

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from treinamento_visual.ingest import config

SANDBOX = "/usr/bin/sandbox-exec"
POLITICA_REDE = (
    '(version 1) (allow default) (deny network-outbound) '
    '(allow network-outbound (remote ip "localhost:*"))'
)


def preparar(paginas: Path, ocr: Path, destino: Path) -> int:
    """Cria tarefas sem copiar imagens nem substituir arquivos existentes."""
    try:
        if any(caminho.is_symlink() for caminho in (paginas, ocr, destino, destino.parent)):
            raise ValueError("As pastas e o arquivo de saída não podem ser links simbólicos.")
        if not paginas.is_dir() or not ocr.is_dir():
            raise ValueError("As pastas de páginas e OCR devem existir.")
        tarefas = []
        documentos = sorted(p for p in paginas.iterdir() if p.name.startswith("doc_"))
        if not documentos:
            raise ValueError("Nenhum documento com páginas foi encontrado.")
        for documento in documentos:
            if documento.is_symlink() or not documento.is_dir() or not re.fullmatch(r"doc_[0-9a-f]{64}", documento.name):
                raise ValueError("Diretório de documento inválido.")
            pasta_ocr = ocr / documento.name
            manifesto = pasta_ocr / "manifest.json"
            if pasta_ocr.is_symlink() or manifesto.is_symlink():
                raise ValueError("O manifesto e a pasta OCR não podem ser links simbólicos.")
            registro = json.loads(manifesto.read_text(encoding="utf-8"))
            total = registro["paginas"]
            if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
                raise ValueError("Quantidade de páginas inválida no manifesto.")
            esperadas = {f"pagina_{numero:04d}.png" for numero in range(1, total + 1)}
            if {imagem.name for imagem in documento.glob("pagina_*.png")} != esperadas:
                raise ValueError("As páginas não correspondem ao manifesto.")
            for numero in range(1, total + 1):
                imagem = documento / f"pagina_{numero:04d}.png"
                if imagem.is_symlink() or not imagem.is_file():
                    raise ValueError("Página ausente ou inválida.")
                referencia = imagem.relative_to(paginas).as_posix()
                tarefas.append({"data": {
                    "image": "/data/local-files/?" + urlencode({"d": referencia}),
                    "documento": documento.name,
                    "pagina": numero,
                }})
        destino.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descritor = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
            json.dump(tarefas, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as erro:
        detalhe = str(erro) if isinstance(erro, ValueError) and not isinstance(erro, json.JSONDecodeError) else type(erro).__name__
        print(f"Não foi possível preparar as tarefas ({detalhe}).", file=sys.stderr)
        return 1
    print(f"Tarefas locais preparadas: {len(tarefas)}; documentos: {len(documentos)}.")
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    data_dir = root / "data" / "treinamento" / "label_studio"
    executable = root / ".venv-label-studio" / "bin" / "label-studio"
    arguments = sys.argv[1:]
    if arguments == ["preparar"]:
        return preparar(config.PAGINAS, config.OCR, data_dir / "tarefas.json")
    if sys.platform != "darwin" or not Path(SANDBOX).is_file():
        print("O Label Studio exige o sandbox de rede do macOS.", file=sys.stderr)
        return 1
    environment = os.environ.copy()
    for nome in ("http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        environment.pop(nome, None)
    environment.update(
        LABEL_STUDIO_SENTRY_DSN="",
        LABEL_STUDIO_FRONTEND_SENTRY_DSN="",
        LABEL_STUDIO_COLLECT_ANALYTICS="false",
        LABEL_STUDIO_FEATURE_FLAGS_OFFLINE="true",
        LABEL_STUDIO_LATEST_VERSION_CHECK="false",
        LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED="true",
        LOCAL_FILES_DOCUMENT_ROOT=str(config.PAGINAS.parent),
        LABEL_STUDIO_BASE_DATA_DIR=str(data_dir),
        LABEL_STUDIO_DJANGO_DB="sqlite",
        LABEL_STUDIO_DATABASE_NAME=str(data_dir / "label_studio.sqlite3"),
    )
    if arguments == ["--version"]:
        arguments = ["version"]
    os.execve(
        SANDBOX,
        [SANDBOX, "-p", POLITICA_REDE, str(executable), *arguments, "--internal-host", "127.0.0.1"],
        environment,
    )


if __name__ == "__main__":
    sys.exit(main())
