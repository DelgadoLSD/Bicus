# -*- coding: utf-8 -*-
"""Troca só a figura do modelo conceitual revisado (sem os tipos). Uso: python aplicar_v6.py <docx>"""
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aplicar_v3 as A  # noqa: E402

doc = Document(sys.argv[1])
h = A.paragrafo_titulo(doc, "Funções de dados (ALI e AIE)")
img = A.com_imagem(h._p)
ext = next(img.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"))
largura = int(ext.get("cx")) / 360000
A.trocar_imagem(doc, img, A.G2.gerar_modelo(), largura)
doc.save(sys.argv[1]); print("ok, largura mantida: %.1f cm" % largura)
