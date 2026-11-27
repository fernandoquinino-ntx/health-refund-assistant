"""Objetivo: executar operações locais do projeto sem scripts shell.

Entradas: diretório raiz, opções de ambiente e arquivos locais.
Processamento: cria ambientes, baixa modelos, inicia serviços e monta artefatos.
Saídas: processos iniciados, diretórios criados e mensagens simples.
"""

import json
import hashlib
import shutil
import subprocess
import sys
import os
import zipfile
import signal
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def executar(comando: list[str], *, verificar: bool = True) -> subprocess.CompletedProcess[str]:
    processo = subprocess.run(
        comando,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if verificar and processo.returncode != 0:
        detalhe = processo.stderr.strip() or processo.stdout.strip() or "comando falhou"
        raise RuntimeError(detalhe)
    return processo


def criar_ambiente(nome: str, requirements: str | None = None, app_editavel: bool = False) -> int:
    ambiente = ROOT / nome
    if not ambiente.is_dir():
        executar([sys.executable, "-m", "venv", str(ambiente)])
    python = ambiente / "bin" / "python"
    if app_editavel:
        executar([str(python), "-m", "pip", "install", "-e", str(ROOT)])
    if requirements:
        executar([str(python), "-m", "pip", "install", "-r", str(ROOT / requirements)])
    print(f"Ambiente pronto: {ambiente}")
    return 0


def setup_app() -> int:
    return criar_ambiente(".venv", app_editavel=True)


def setup_training() -> int:
    return criar_ambiente(".venv-treinamento", "requirements/treinamento.txt")


def setup_conversion() -> int:
    return criar_ambiente(".venv-conversao", "requirements/conversao.txt")


def setup_label() -> int:
    return criar_ambiente(".venv-label-studio", "requirements/label-studio.txt")


def setup_codespace() -> int:
    setup_app()
    setup_training()
    setup_conversion()
    setup_label()

    python_conversion = ROOT / ".venv-conversao" / "bin" / "python"
    modelo = ROOT / "models" / "smolvlm-hf"
    modelo.mkdir(parents=True, exist_ok=True)
    executar([
        str(python_conversion),
        "-c",
        (
            "from huggingface_hub import snapshot_download;"
            "snapshot_download("
            "repo_id='HuggingFaceTB/SmolVLM-256M-Instruct',"
            "local_dir='models/smolvlm-hf',"
            "local_dir_use_symlinks=False,"
            "allow_patterns=['*.json','*.txt','*.jinja','*.model','*.safetensors','*.index.json'])"
        ),
    ])

    tools = ROOT / "tools"
    llama = tools / "llama.cpp"
    if not (llama / ".git").is_dir():
        tools.mkdir(parents=True, exist_ok=True)
        executar(["git", "clone", "--depth", "1", "https://github.com/ggerganov/llama.cpp", str(llama)])
    executar(["git", "-C", str(llama), "checkout", "--detach", "a8ad690ca9239ea35db4de47e00cf632d01895fd"])

    build = llama / "build"
    if not (build / "bin" / "llama-server").is_file():
        executar(["cmake", "-S", str(llama), "-B", str(build), "-DLLAMA_CURL=OFF", "-DGGML_NATIVE=OFF"])
        executar([
            "cmake", "--build", str(build), "-j",
            str(os.cpu_count() or 2),
            "--target", "llama-server", "llama-quantize",
        ])
    print("Codespace preparado: aplicação, treino, conversão e llama.cpp.")
    return 0


def build_extension() -> int:
    source = ROOT / "src" / "extension"
    output = ROOT / "build" / "extension"
    manifest_path = source / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Manifest da extensão não encontrado.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != 3:
        raise RuntimeError("A extensão deve usar Manifest V3.")
    version = str(manifest.get("version", "")).strip()
    if not version:
        raise RuntimeError("A versão da extensão não está definida no manifest.")

    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)
    arquivos = {
        "manifest.json",
        "10_popup/popup.html",
        "10_popup/popup.js",
        "20_background/background.js",
        "30_content/bridge.js",
        "40_collector/collector.js",
        "60_schemas/export.schema.json",
    }
    for origem in arquivos:
        source_file = source / origem
        if not source_file.is_file():
            raise RuntimeError(f"Arquivo obrigatório da extensão ausente: {origem}")
        destination_file = output / origem
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)

    built_manifest = json.loads(
        (output / "manifest.json").read_text(encoding="utf-8")
    )
    referenced_files = [
        built_manifest["background"]["service_worker"],
        built_manifest["action"]["default_popup"],
        *(script for item in built_manifest["content_scripts"] for script in item["js"]),
    ]
    missing = [path for path in referenced_files if not (output / path).is_file()]
    if missing:
        raise RuntimeError(
            "Manifest referencia arquivos ausentes no pacote: " + ", ".join(missing)
        )

    package = ROOT / "build" / f"care-plus-reembolsos-{version}.zip"
    package.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(output.rglob("*")):
            if file.is_file():
                archive.write(file, file.relative_to(output).as_posix())

    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    (ROOT / "build" / f"care-plus-reembolsos-{version}.sha256").write_text(
        f"{digest}  {package.name}\n",
        encoding="utf-8",
    )
    print(f"Extensão construída em: {output}")
    print(f"Pacote Chrome compatível: {package}")
    print(f"SHA-256: {digest}")
    return 0


def start_local_vlm() -> int:
    approval_path = ROOT / "json" / "training" / "visual" / "modelo_aprovado.json"
    if not approval_path.is_file():
        print("Modelo local não ativado: aprovação inexistente.", file=sys.stderr)
        return 0
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("aprovado") is not True:
        print("Modelo local não ativado: aprovação recusada.", file=sys.stderr)
        return 0

    model = ROOT / "models" / "gguf" / "smolvlm-256m-health-refund-Q4_K_M.gguf"
    mmproj = ROOT / "models" / "gguf" / "smolvlm-256m-health-refund-mmproj.gguf"
    lora = ROOT / "models" / "gguf" / "smolvlm-256m-private-lora.gguf"
    server = ROOT / "tools" / "llama.cpp" / "build" / "bin" / "llama-server"
    if not all(path.is_file() for path in (model, mmproj, server)):
        print("Modelo local não ativado: GGUF, mmproj ou servidor ausente.", file=sys.stderr)
        return 0

    command = [
        str(server),
        "--model", str(model),
        "--mmproj", str(mmproj),
        "--host", "127.0.0.1",
        "--port", "8081",
    ]
    if lora.is_file():
        command.extend(["--lora", str(lora)])
    log = open("/tmp/health-refund-vlm.log", "a", encoding="utf-8")
    subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    print("Servidor visual local iniciado em http://127.0.0.1:8081/v1")
    return 0


def start_assistant() -> int:
    stop_assistant_process()
    python = ROOT / ".venv" / "bin" / "python"
    if not python.is_file():
        return setup_app()
    log = open("/tmp/health-refund-assistant.log", "a", encoding="utf-8")
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    subprocess.Popen(
        [
            str(python),
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address",
            "0.0.0.0",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    print("Assistente iniciado na porta 8501.")
    return 0


def stop_assistant_process() -> int:
    """Stop only a prior Streamlit process for this application's app.py."""
    result = executar(["ps", "-eo", "pid=,args="], verificar=False)
    stopped = 0
    for line in result.stdout.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) != 2:
            continue
        pid_text, command = fields
        if "streamlit" not in command or "app.py" not in command:
            continue
        if "--server.port" not in command or "8501" not in command:
            continue
        if str(ROOT) not in command and str(ROOT / "app.py") not in command:
            continue
        try:
            os.kill(int(pid_text), signal.SIGTERM)
            stopped += 1
        except (ProcessLookupError, PermissionError, ValueError):
            continue
    if stopped:
        time.sleep(1)
        print(f"Processos anteriores do assistente encerrados: {stopped}.")
    return stopped


def restart_assistant() -> int:
    """Restart the application from the current checkout and its latest code."""
    stop_assistant_process()
    return start_assistant()


def converter_modelo() -> int:
    approval_path = ROOT / "json" / "training" / "visual" / "modelo_aprovado.json"
    if not approval_path.is_file():
        print("Conversão bloqueada: aprovação inexistente.")
        return 0
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("aprovado") is not True:
        print("Conversão bloqueada: adaptador não aprovado.")
        return 0

    source = ROOT / "models" / "smolvlm-hf"
    output = ROOT / "models" / "gguf"
    llama = ROOT / "tools" / "llama.cpp"
    convert = llama / "convert_hf_to_gguf.py"
    quantize = llama / "build" / "bin" / "llama-quantize"
    python_conversion = ROOT / ".venv-conversao" / "bin" / "python"
    if not all(path.exists() for path in (source, convert, python_conversion)):
        print("Conversão bloqueada: modelo base, conversor ou ambiente ausente.")
        return 0

    output.mkdir(parents=True, exist_ok=True)
    executar([
        str(python_conversion),
        str(convert),
        str(source),
        "--outfile", str(output / "smolvlm-256m-health-refund-f16.gguf"),
        "--outtype", "f16",
        "--model-name", "smolvlm-256m-health-refund",
    ])
    executar([
        str(python_conversion),
        str(convert),
        str(source),
        "--outfile", str(output / "smolvlm-256m-health-refund-mmproj.gguf"),
        "--mmproj",
    ])
    if quantize.is_file():
        executar([
            str(quantize),
            str(output / "smolvlm-256m-health-refund-f16.gguf"),
            str(output / "smolvlm-256m-health-refund-Q4_K_M.gguf"),
            "Q4_K_M",
        ])
    print("Conversão GGUF concluída.")
    return 0
