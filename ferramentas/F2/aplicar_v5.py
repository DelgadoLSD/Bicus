# -*- coding: utf-8 -*-
"""Troca o texto longo de alterações do modelo por um parágrafo curto. Uso: python aplicar_v5.py <docx>"""
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aplicar_v3 as A  # noqa: E402

TEXTO = ("Em relação ao modelo preliminar da Concepção, o modelo foi revisado para ficar coerente "
         "com os requisitos: Prestador passou a ser subclasse de Usuário; foram incluídos atributos "
         "que faltavam, como senha, aceite dos termos, situação da conta e quem cancelou a "
         "solicitação; a associação \"mantém\" foi removida; e foram indicadas as multiplicidades. "
         "Os tipos compostos e os valores das enumerações estão na tabela a seguir.")
doc = Document(sys.argv[1])
rotulo = next(p for p in doc.paragraphs
              if p.text.strip() == "Alterações em relação ao modelo preliminar da Concepção")
remover = [rotulo._p]
for irmao in rotulo._p.itersiblings():
    if irmao.tag != A.qn("w:p") or not A.texto_de(irmao).strip():
        break
    remover.append(irmao)
assert len(remover) == 10, len(remover)
novo = A.G1.paragrafo(doc, TEXTO, size=10, after=6)._p
rotulo._p.addprevious(novo)
for el in remover:
    el.getparent().remove(el)
doc.save(sys.argv[1])
print("ok")
