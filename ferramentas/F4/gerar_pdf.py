"""Gera "F4 - Implementação/Guia da F4.pdf" a partir de guia.html (Edge em modo headless)."""
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
HTML = AQUI / "guia.html"
SAIDA = RAIZ / "F4 - Implementação" / "Guia da F4.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def imprimir(destino: Path) -> None:
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([
            str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--user-data-dir={perfil}", f"--print-to-pdf={destino}", HTML.as_uri(),
        ], check=True, capture_output=True, timeout=120)


def numerar(origem: Path, destino: Path) -> int:
    doc = pymupdf.open(origem)
    for i, pagina in enumerate(doc, start=1):
        texto = str(i)
        x = (pagina.rect.width - pymupdf.get_text_length(texto, fontsize=9)) / 2
        pagina.insert_text((x, pagina.rect.height - 30), texto, fontsize=9)
    doc.set_metadata({"title": "Bicus – F4: o que vamos implementar e como", "author": "Grupo Bicus"})
    total = doc.page_count
    doc.save(destino, garbage=3, deflate=True)
    return total


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        bruto = Path(tmp) / "guia.pdf"
        imprimir(bruto)
        paginas = numerar(bruto, SAIDA)
    print(f"{SAIDA} ({paginas} páginas)")
