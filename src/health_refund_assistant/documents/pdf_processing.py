import argparse
import hashlib
import json
import re
import shutil
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.json_contracts import validar_contrato_json
from ..core.paths import (
    FAILED_DIR,
    INCOMING_DIR,
    NOTES_STATE_PATH,
    PROCESSED_DIR,
)
from .pdf_converter import converter_primeira_pagina_pdf_base64
from .vlm_extractor import DEFAULT_MODEL, VLMExtractor


CAMINHO_PADRAO_ENTRADA = INCOMING_DIR
CAMINHO_PADRAO_PROCESSADAS = PROCESSED_DIR
CAMINHO_PADRAO_FALHAS = FAILED_DIR
CAMINHO_PADRAO_NOTAS_EXTRAIDAS = NOTES_STATE_PATH


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def novo_id() -> str:
    return uuid.uuid4().hex


def carregar_status(caminho: Path) -> Dict[str, Any]:
    if not caminho.exists():
        return {
            "schema_version": 3,
            "model": None,
            "prompt_version": None,
            "pdfs": {},
            "duplicatas": [],
        }

    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError(f"O arquivo de status deve conter um objeto JSON: {caminho}")

    dados["schema_version"] = 3
    if not isinstance(dados.setdefault("pdfs", {}), dict):
        raise ValueError("A propriedade 'pdfs' do status deve ser um objeto JSON.")
    if not isinstance(dados.setdefault("duplicatas", []), list):
        raise ValueError("A propriedade 'duplicatas' do status deve ser uma lista JSON.")
    dados.setdefault("model", None)
    dados.setdefault("prompt_version", None)
    return dados


def salvar_status(caminho: Path, dados: Dict[str, Any]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    validar_contrato_json(dados, "notes_state.schema.json", caminho.name)
    caminho_temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    with caminho_temporario.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    caminho_temporario.replace(caminho)


def ja_processado(
    registro: Optional[Dict[str, Any]],
    model: str,
    prompt_version: str,
    forcar: bool,
) -> bool:
    if forcar or not registro:
        return False
    return (
        registro.get("processado") is True
        and registro.get("sucesso") is True
        and registro.get("model") == model
        and registro.get("prompt_version") == prompt_version
    )


def calcular_sha256(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _caminhos_iguais(primeiro: Any, segundo: Path) -> bool:
    if not isinstance(primeiro, str):
        return False
    try:
        return Path(primeiro).resolve() == segundo.resolve()
    except OSError:
        return False


def _encontrar_registro_da_origem(
    status: Dict[str, Any], caminho_pdf: Path, sha256: str
) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    for chave, registro in status["pdfs"].items():
        mesma_origem = _caminhos_iguais(
            registro.get("caminho_origem"), caminho_pdf
        ) or _caminhos_iguais(registro.get("caminho"), caminho_pdf)
        if not mesma_origem:
            continue

        hash_registrado = registro.get("sha256")
        if hash_registrado is None and isinstance(registro.get("caminho"), str):
            caminho_existente = Path(registro["caminho"])
            if caminho_existente.is_file():
                hash_registrado = calcular_sha256(caminho_existente)
                registro["sha256"] = hash_registrado
        if hash_registrado == sha256:
            return chave, registro
    return None, None


def _encontrar_duplicata_exata(
    status: Dict[str, Any],
    sha256: str,
    caminho_origem: Path,
    excluir_chave: Optional[str],
) -> Optional[str]:
    for chave, registro in status["pdfs"].items():
        if chave == excluir_chave or registro.get("sucesso") is not True:
            continue

        hash_registrado = registro.get("sha256")
        if hash_registrado is None and isinstance(registro.get("caminho"), str):
            caminho_existente = Path(registro["caminho"])
            if caminho_existente.is_file():
                hash_registrado = calcular_sha256(caminho_existente)
                registro["sha256"] = hash_registrado
        if hash_registrado == sha256:
            return str(registro.get("document_id", chave))

    for duplicata in status["duplicatas"]:
        mesma_origem = _caminhos_iguais(
            duplicata.get("caminho_origem"), caminho_origem
        )
        if duplicata.get("sha256") == sha256:
            if mesma_origem:
                return str(duplicata.get("duplicado_de", ""))
            return str(duplicata.get("duplicado_de", ""))
    return None


def _normalizar_identificador(valor: Any) -> str:
    if not isinstance(valor, (str, int)):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto_ascii = texto.encode("ascii", "ignore").decode("ascii").upper()
    return re.sub(r"[^A-Z0-9]", "", texto_ascii)


def _chave_nota(resultado: Dict[str, Any]) -> Optional[tuple[str, str]]:
    identificador_prestador = _normalizar_identificador(
        resultado.get("cnpj_cpf_prestador")
    )
    numero_documento = _normalizar_identificador(
        resultado.get("numero_documento")
    )
    if not identificador_prestador or not numero_documento:
        return None
    return identificador_prestador, numero_documento


def _encontrar_duplicata_por_nota(
    status: Dict[str, Any],
    resultado: Dict[str, Any],
    excluir_chave: Optional[str],
) -> Optional[str]:
    chave_nota = _chave_nota(resultado)
    if chave_nota is None:
        return None

    for chave, registro in status["pdfs"].items():
        if chave == excluir_chave or registro.get("sucesso") is not True:
            continue
        resultado_existente = registro.get("resultado")
        if not isinstance(resultado_existente, dict):
            continue
        if _chave_nota(resultado_existente) == chave_nota:
            return str(registro.get("document_id", chave))
    return None


def _limpar_componente_nome(valor: Any, fallback: str) -> str:
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto_ascii = texto.encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^A-Za-z0-9_-]+", "-", texto_ascii).strip("-_")
    return limpo[:48] or fallback


def _nome_pdf_processado(resultado: Dict[str, Any], document_id: str) -> str:
    data_emissao = resultado.get("data_emissao")
    try:
        data_nome = datetime.strptime(str(data_emissao), "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )
    except ValueError:
        data_nome = _limpar_componente_nome(data_emissao, "sem-data")

    numero = _limpar_componente_nome(
        resultado.get("numero_documento"), "sem-numero"
    )
    prefixo = "" if numero.upper().startswith(("NF-", "NFS-", "RPS-")) else "NF-"
    return f"{data_nome}_{prefixo}{numero}_{document_id[:8]}.pdf"


def _mover_pdf(caminho_pdf: Path, pasta_destino: Path, nome_destino: str) -> Path:
    pasta_destino.mkdir(parents=True, exist_ok=True)
    destino = pasta_destino / nome_destino
    if caminho_pdf.resolve() == destino.resolve():
        return caminho_pdf
    if destino.exists():
        raise FileExistsError(f"O arquivo de destino já existe: {destino}")
    return Path(shutil.move(str(caminho_pdf), str(destino)))


def _origem_duplicata_ja_registrada(
    status: Dict[str, Any], caminho_pdf: Path, sha256: str
) -> bool:
    return any(
        duplicata.get("sha256") == sha256
        and _caminhos_iguais(duplicata.get("caminho_origem"), caminho_pdf)
        for duplicata in status["duplicatas"]
    )


def _registrar_duplicata(
    status: Dict[str, Any],
    caminho_pdf: Path,
    sha256: str,
    duplicado_de: str,
    tipo: str,
    pasta_processadas: Path,
    manter_originais: bool,
    model: str,
    prompt_version: str,
    resultado: Optional[Dict[str, Any]] = None,
) -> None:
    document_id = novo_id()
    caminho_final = caminho_pdf
    if not manter_originais:
        caminho_final = _mover_pdf(
            caminho_pdf,
            pasta_processadas / "duplicatas",
            f"duplicata_{document_id[:8]}.pdf",
        )

    status["duplicatas"].append(
        {
            "document_id": document_id,
            "nome_arquivo_original": caminho_pdf.name,
            "nome_arquivo": caminho_final.name,
            "caminho_origem": str(caminho_pdf),
            "caminho": str(caminho_final),
            "sha256": sha256,
            "duplicado_de": duplicado_de,
            "tipo_duplicidade": tipo,
            "registrado_em": agora_iso(),
            "model": model,
            "prompt_version": prompt_version,
            "resultado": resultado,
        }
    )


def processar_pdfs(
    pasta_pdfs: Path,
    caminho_status: Path,
    model: str,
    prompt_version: Optional[str] = None,
    forcar: bool = False,
    pasta_processadas: Path = CAMINHO_PADRAO_PROCESSADAS,
    pasta_falhas: Path = CAMINHO_PADRAO_FALHAS,
    reprocessar_falhas: bool = False,
    manter_originais: bool = False,
) -> Dict[str, Any]:
    pasta_pdfs.mkdir(parents=True, exist_ok=True)
    status = carregar_status(caminho_status)

    fontes = [
        caminho
        for caminho in pasta_pdfs.rglob("*")
        if caminho.is_file() and caminho.suffix.lower() == ".pdf"
    ]
    if reprocessar_falhas and pasta_falhas.exists():
        fontes.extend(
            caminho
            for caminho in pasta_falhas.rglob("*")
            if caminho.is_file() and caminho.suffix.lower() == ".pdf"
        )
    fontes = sorted(set(fontes))
    if not fontes:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em {pasta_pdfs}"
            + (f" ou {pasta_falhas}" if reprocessar_falhas else "")
        )

    extrator = VLMExtractor(model=model, prompt_version=prompt_version)
    status["model"] = extrator.model
    status["prompt_version"] = extrator.prompt_version
    status["duplicatas"] = status.get("duplicatas", [])

    for pdf in fontes:
        sha256 = calcular_sha256(pdf)
        chave_existente, registro_existente = _encontrar_registro_da_origem(
            status, pdf, sha256
        )

        if (
            registro_existente
            and ja_processado(
                registro_existente,
                extrator.model,
                extrator.prompt_version,
                forcar,
            )
        ):
            if _caminhos_iguais(registro_existente.get("caminho"), pdf):
                print(f"⏭️  {pdf.name}: já processado")
            else:
                _registrar_duplicata(
                    status,
                    pdf,
                    sha256,
                    str(
                        registro_existente.get(
                            "document_id", chave_existente
                        )
                    ),
                    "arquivo_identico",
                    pasta_processadas,
                    manter_originais,
                    extrator.model,
                    extrator.prompt_version,
                )
                salvar_status(caminho_status, status)
                print(f"♻️  {pdf.name}: cópia já processada")
            continue

        if _origem_duplicata_ja_registrada(status, pdf, sha256):
            print(f"⏭️  {pdf.name}: duplicata já registrada")
            continue

        duplicado_de = _encontrar_duplicata_exata(
            status, sha256, pdf, chave_existente
        )
        if duplicado_de is not None:
            _registrar_duplicata(
                status,
                pdf,
                sha256,
                duplicado_de,
                "arquivo_identico",
                pasta_processadas,
                manter_originais,
                extrator.model,
                extrator.prompt_version,
            )
            salvar_status(caminho_status, status)
            print(f"♻️  {pdf.name}: cópia idêntica de {duplicado_de}")
            continue

        document_id = (
            str(registro_existente.get("document_id") or chave_existente)
            if registro_existente
            else novo_id()
        )
        resultado: Dict[str, Any]
        try:
            imagem = converter_primeira_pagina_pdf_base64(str(pdf))
            resultado = extrator.extrair_dados_nf_visual(imagem)
            sucesso = resultado.get("_meta", {}).get("status") == "OK"
        except Exception as erro:
            resultado = {
                "numero_documento": None,
                "prestador": None,
                "cnpj_cpf_prestador": None,
                "valor_total": None,
                "data_emissao": None,
                "descricao_servico": None,
                "registro_profissional": None,
                "imagem_legivel": False,
                "observacao_visual": f"ERRO_PROCESSAMENTO: {erro}",
                "_meta": {
                    "status": "ERRO_PROCESSAMENTO",
                    "model": extrator.model,
                    "prompt_version": extrator.prompt_version,
                    "latencia_seg": 0,
                },
            }
            sucesso = False

        if sucesso:
            duplicado_de = _encontrar_duplicata_por_nota(
                status, resultado, chave_existente
            )
            if duplicado_de is not None:
                _registrar_duplicata(
                    status,
                    pdf,
                    sha256,
                    duplicado_de,
                    "mesmo_prestador_e_numero_documento",
                    pasta_processadas,
                    manter_originais,
                    extrator.model,
                    extrator.prompt_version,
                    resultado,
                )
                if chave_existente is not None:
                    status["pdfs"].pop(chave_existente, None)
                salvar_status(caminho_status, status)
                print(f"♻️  {pdf.name}: possível duplicata de {duplicado_de}")
                continue

        if manter_originais:
            caminho_final = pdf
        elif sucesso:
            caminho_final = _mover_pdf(
                pdf,
                pasta_processadas,
                _nome_pdf_processado(resultado, document_id),
            )
        else:
            caminho_final = _mover_pdf(
                pdf, pasta_falhas, f"falha_{document_id[:8]}.pdf"
            )

        chave_registro = chave_existente or document_id
        registro = {
            "document_id": document_id,
            "nome_arquivo_original": (
                registro_existente.get("nome_arquivo_original", pdf.name)
                if registro_existente
                else pdf.name
            ),
            "nome_arquivo": caminho_final.name,
            "caminho_origem": (
                registro_existente.get("caminho_origem", str(pdf))
                if registro_existente
                else str(pdf)
            ),
            "caminho": str(caminho_final),
            "sha256": sha256,
            "processado": True,
            "sucesso": sucesso,
            "estado": "processado" if sucesso else "falha",
            "processado_em": agora_iso(),
            "model": extrator.model,
            "prompt_version": extrator.prompt_version,
            "resultado": resultado,
        }
        status["pdfs"][chave_registro] = registro
        salvar_status(caminho_status, status)

        simbolo = "✅" if sucesso else "❌"
        print(f"{simbolo} {pdf.name}: {caminho_final.name}")

    return status


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Processa PDFs de notas fiscais usando a API OpenAI."
    )
    parser.add_argument(
        "--entrada",
        "--pasta-pdfs",
        dest="entrada",
        type=Path,
        default=CAMINHO_PADRAO_ENTRADA,
        help="Pasta de entrada (padrão: data/incoming). --pasta-pdfs é compatível.",
    )
    parser.add_argument(
        "--processadas",
        type=Path,
        default=CAMINHO_PADRAO_PROCESSADAS,
        help="Pasta para PDFs processados (padrão: data/processed).",
    )
    parser.add_argument(
        "--falhas",
        type=Path,
        default=CAMINHO_PADRAO_FALHAS,
        help="Pasta para PDFs com falha (padrão: data/failed).",
    )
    parser.add_argument(
        "--saida",
        "--status",
        dest="status",
        type=Path,
        default=CAMINHO_PADRAO_NOTAS_EXTRAIDAS,
        help="Arquivo JSON de estado e extrações.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--prompt-version",
        help="Versão fixa do prompt; por padrão usa a mais recente.",
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Reprocessa PDFs da entrada já concluídos.",
    )
    parser.add_argument(
        "--reprocessar-falhas",
        action="store_true",
        help="Inclui PDFs de data/failed na execução.",
    )
    parser.add_argument(
        "--manter-originais",
        action="store_true",
        help="Não move nem renomeia PDFs; útil para comparar prompts em testes.",
    )
    args = parser.parse_args()

    processar_pdfs(
        pasta_pdfs=args.entrada,
        caminho_status=args.status,
        model=args.model,
        prompt_version=args.prompt_version,
        forcar=args.forcar,
        pasta_processadas=args.processadas,
        pasta_falhas=args.falhas,
        reprocessar_falhas=args.reprocessar_falhas,
        manter_originais=args.manter_originais,
    )


if __name__ == "__main__":
    main()
