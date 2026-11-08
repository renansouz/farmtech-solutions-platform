"""Inferência REAL com a YOLOv5 treinada no notebook da Fase 6.

Requer checkout local da YOLOv5 e o checkpoint `best.pt` do experimento
fase6_60_final (ou o modelo escolhido pelo grupo). NÃO inventa detecções.

Uso:
    python src/fase6_vision/detector.py --imagem foto.jpg
    python src/fase6_vision/detector.py --imagem foto.jpg --salvar-oracle
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
CLASSES_DISPONIVEIS = ("garrafa", "caneca")
CATEGORIAS = {
    "garrafa": "Recipiente / insumo (verificar rótulo antes de manusear)",
    "caneca": "Utensílio / recipiente de coleta",
}
EXTENSOES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def resolver_caminho(valor: str | Path) -> Path:
    path = Path(valor).expanduser()
    return (path if path.is_absolute() else ROOT / path).resolve()


def configuracao_modelo(pesos: str | Path | None = None, repositorio: str | Path | None = None):
    """Falha de modo explícito caso o checkpoint ou a implementação não existam."""
    caminho_pesos = resolver_caminho(pesos or os.getenv("YOLO_WEIGHTS", "models/fase6_60_final_best.pt"))
    caminho_repo = resolver_caminho(repositorio or os.getenv("YOLOV5_REPO", "yolov5"))
    if not caminho_pesos.is_file():
        raise FileNotFoundError(
            f"Checkpoint YOLO não encontrado: {caminho_pesos}. "
            "Recupere o best.pt do treino fase6_60_final e configure YOLO_WEIGHTS no .env."
        )
    if not (caminho_repo / "detect.py").is_file():
        raise FileNotFoundError(
            f"YOLOv5 não encontrada em {caminho_repo}. "
            "Faça o checkout do repositório ultralytics/yolov5 e configure YOLOV5_REPO."
        )
    return caminho_pesos, caminho_repo


def interpretar_labels(arquivo: Path, largura: int, altura: int) -> list[dict]:
    """Converte labels YOLO (classe cx cy largura altura confiança) em pixels."""
    if not arquivo.exists():
        return []  # Uma imagem pode legitimamente não ter objetos detectados.
    deteccoes = []
    for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
        partes = linha.split()
        if len(partes) != 6:
            raise ValueError(f"Label inválida (linha {numero}): esperados 6 campos")
        indice = int(partes[0])
        if not 0 <= indice < len(CLASSES_DISPONIVEIS):
            raise ValueError(f"Classe {indice} não corresponde ao modelo customizado de 2 classes")
        cx, cy, w, h, confianca = map(float, partes[1:])
        if not (0 <= confianca <= 1 and all(0 <= n <= 1 for n in (cx, cy, w, h))):
            raise ValueError(f"Valores fora do intervalo no label da linha {numero}")
        x1 = max(0, min(largura, round((cx - w / 2) * largura)))
        y1 = max(0, min(altura, round((cy - h / 2) * altura)))
        x2 = max(0, min(largura, round((cx + w / 2) * largura)))
        y2 = max(0, min(altura, round((cy + h / 2) * altura)))
        classe = CLASSES_DISPONIVEIS[indice]
        deteccoes.append({
            "classe": classe,
            "confianca": round(confianca, 5),
            "box": [x1, y1, x2, y2],
            "categoria": CATEGORIAS[classe],
        })
    return deteccoes


def analisar_imagem(
    caminho_imagem: str | Path,
    *,
    pesos: str | Path | None = None,
    repositorio: str | Path | None = None,
    confianca_minima: float = 0.25,
    timeout: int = 180,
) -> dict:
    """Executa detect.py no modelo customizado e retorna resultados + imagem anotada.

    `imagem_anotada` contém bytes para uso no Streamlit; não é serializável em JSON.
    """
    imagem = Path(caminho_imagem).expanduser().resolve()
    if not imagem.is_file() or imagem.suffix.lower() not in EXTENSOES:
        raise ValueError("Informe um arquivo de imagem existente (.jpg, .png, .bmp ou .webp).")
    if not 0 < confianca_minima <= 1:
        raise ValueError("A confiança mínima deve ficar no intervalo (0, 1].")
    if imagem.stat().st_size > 15 * 1024 * 1024:
        raise ValueError("A imagem deve ter no máximo 15 MB.")
    with Image.open(imagem) as original:
        largura, altura = original.size
        original.verify()
    pesos_path, repo_path = configuracao_modelo(pesos, repositorio)

    with tempfile.TemporaryDirectory(prefix="farmtech_yolo_") as tmp:
        pasta_tmp = Path(tmp)
        entrada = pasta_tmp / f"entrada{imagem.suffix.lower()}"
        shutil.copy2(imagem, entrada)
        pasta_saida = pasta_tmp / "resultados"
        cmd = [
            sys.executable, str(repo_path / "detect.py"),
            "--weights", str(pesos_path),
            "--source", str(entrada),
            "--img", "320",  # Notebook Fase 6: --img 320.
            "--conf-thres", str(confianca_minima),
            "--device", os.getenv("YOLO_DEVICE", "cpu"),
            "--save-txt", "--save-conf",
            "--project", str(pasta_saida),
            "--name", "inferencia", "--exist-ok",
        ]
        try:
            processo = subprocess.run(
                cmd, cwd=repo_path, text=True, capture_output=True,
                timeout=timeout, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("YOLOv5 excedeu o tempo limite de inferência") from exc
        if processo.returncode != 0:
            detalhe = "\n".join((processo.stderr or processo.stdout).splitlines()[-18:])
            raise RuntimeError(f"YOLOv5 falhou (código {processo.returncode}):\n{detalhe}")

        saida = pasta_saida / "inferencia"
        arquivo_labels = saida / "labels" / "entrada.txt"
        deteccoes = interpretar_labels(arquivo_labels, largura, altura)
        arquivo_anotado = saida / entrada.name
        if not arquivo_anotado.is_file():
            raise RuntimeError("YOLOv5 concluiu sem produzir a imagem anotada esperada")
        return {
            "arquivo": imagem.name,
            "modelo": pesos_path.name,
            "largura": largura,
            "altura": altura,
            "deteccoes": deteccoes,
            "imagem_anotada": arquivo_anotado.read_bytes(),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detector YOLOv5 REAL da FarmTech (2 classes)")
    parser.add_argument("--imagem", "--image", required=True, type=Path)
    parser.add_argument("--pesos", type=Path, help="Override de YOLO_WEIGHTS")
    parser.add_argument("--repositorio", type=Path, help="Override de YOLOV5_REPO")
    parser.add_argument("--confianca", type=float, default=0.25)
    parser.add_argument("--salvar-oracle", action="store_true", help="Persistir detecções reais")
    parser.add_argument("--saida", type=Path, help="Salvar a imagem anotada")
    args = parser.parse_args(argv)
    try:
        result = analisar_imagem(
            args.imagem, pesos=args.pesos, repositorio=args.repositorio,
            confianca_minima=args.confianca,
        )
        if args.saida:
            if args.saida.suffix.lower() != args.imagem.suffix.lower():
                raise ValueError("A extensão de --saida deve corresponder à imagem de entrada")
            args.saida.parent.mkdir(parents=True, exist_ok=True)
            args.saida.write_bytes(result["imagem_anotada"])
        if args.salvar_oracle:
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from src.fase3_database.conexao import conectar_oracle, garantir_tabelas
            from src.fase3_database.deteccoes_oracle import salvar_deteccoes
            with conectar_oracle() as conn:
                garantir_tabelas(conn)
                gravadas = salvar_deteccoes(
                    conn, args.imagem.name, result["deteccoes"], result["modelo"]
                )
            result["registros_oracle"] = gravadas
        # Resposta estruturada; jamais imprime detecções aleatórias.
        print(json.dumps({k: v for k, v in result.items() if k != "imagem_anotada"},
                         ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"[ERRO] Falha na inferência real: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
