# -*- coding: utf-8 -*-
"""Troca a tabela de alterações do modelo por texto corrido. Uso: python aplicar_v4.py <docx>"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aplicar_v3 as A  # noqa: E402

G1, C2 = A.G1, A.C2
doc = Document(sys.argv[1])
h = A.paragrafo_titulo(doc, "Funções de dados (ALI e AIE)")
fonte = A.Paragraph(A.proximos(h._p, "w:p")[0], doc._body) if hasattr(A, "Paragraph") else None
from docx.text.paragraph import Paragraph  # noqa: E402
fonte = Paragraph(A.proximos(h._p, "w:p")[0], doc._body)
A.trocar_texto(fonte, "Modelo conceitual revisado a partir do modelo preliminar da Concepção. "
                      "Cada classe é um ALI; a API de geocodificação é a AIE.")
tabela = A.proximos(h._p, "w:tbl")[0]
assert A.texto_de(tabela).startswith("Alteração em relação ao modelo preliminar")
novos = [G1.paragrafo(doc, "", "Alterações em relação ao modelo preliminar da Concepção",
                      size=11, after=4, align=WD_ALIGN_PARAGRAPH.LEFT)._p]
for prefixo, texto in C2.MODELO_ALTERACOES_TEXTO:
    novos.append(G1.paragrafo(doc, texto, prefixo, size=10, after=4)._p)
for el in novos:
    tabela.addprevious(el)
novos[0].getparent()  # noqa
tabela.getparent().remove(tabela)
doc.save(sys.argv[1])
print("ok")
