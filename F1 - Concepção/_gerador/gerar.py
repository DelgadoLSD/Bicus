# -*- coding: utf-8 -*-
"""
Gera os artefatos da Concepção (F1) do Bicus a partir de conteudo.py.

Uso:  python gerar.py            (gera .md, diagramas e .docx)
Depois, atualizar_sumario.ps1 abre o .docx no Word e preenche o sumário.
"""
import math
import re
import sys
from pathlib import Path

import pymupdf
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import conteudo as C

RAIZ = Path(__file__).resolve().parent.parent          # .../F1 - Concepção
DIAG = RAIZ / "diagramas"
DOCX = RAIZ / "Bicus - F1 Concepção.docx"


def mark(v):
    return "(X)" if v else "( )"


def nf_code(f, i):
    return f"NF{f['cod'][1:]}.{i + 1}"


def uc_ids():
    return {f"UC{i + 1}": uc["nome"] for i, uc in enumerate(C.CASOS_DE_USO)}


# ---------------------------------------------------------------------------
# Validação das referências cruzadas e da rastreabilidade
# ---------------------------------------------------------------------------

def validar():
    fs = {f["cod"] for f in C.RF}
    nfs = {nf_code(f, i) for f in C.RF for i in range(len(f["nfs"]))}
    ss = {f"S{i + 1}" for i in range(len(C.SUPLEMENTARES))}
    erros = []

    textos = []
    for f in C.RF:
        textos.append((f["cod"], f["desc"]))
        for i, nf in enumerate(f["nfs"]):
            textos.append((nf_code(f, i), nf[1]))
    for i, s in enumerate(C.SUPLEMENTARES):
        textos.append((f"S{i + 1}", " ".join(s[1])))
    for origem, t in textos:
        for m in re.findall(r"\bNF\d+\.\d+\b", t):
            if m not in nfs:
                erros.append(f"{origem}: referência inexistente {m}")
        for m in re.findall(r"(?<![N\w])F\d+\b", t):
            if m not in fs:
                erros.append(f"{origem}: referência inexistente {m}")
        for m in re.findall(r"\bS\d+\b", t):
            if m not in ss:
                erros.append(f"{origem}: referência inexistente {m}")

    todas_refs = [r for uc in C.CASOS_DE_USO for r in uc["refs"]]
    todas_refs += [r for c in C.CONCEITOS for r in c[6]]
    todas_refs += [r for q in C.CONSULTAS for r in q[1]]
    for r in todas_refs:
        if r not in fs | ss:
            erros.append(f"organização: referência inexistente {r}")
    nao_rastreados = sorted(fs - set(todas_refs), key=lambda x: int(x[1:]))
    if nao_rastreados:
        erros.append("requisitos sem caso de uso/conceito/consulta: " + ", ".join(nao_rastreados))

    conceitos = {c[0] for c in C.CONCEITOS}
    if conceitos != set(C.CLASSES):
        erros.append(f"modelo conceitual e lista de conceitos divergem: "
                     f"{conceitos ^ set(C.CLASSES)}")
    for a, b, _ in C.ASSOCIACOES:
        if a not in C.CLASSES or b not in C.CLASSES:
            erros.append(f"associação com classe inexistente: {a} - {b}")

    for ciclo in C.CICLOS:
        horas = sum(int(re.search(r"\((\d+)h\)", x).group(1))
                    for x in ciclo[1] + ciclo[2] + ciclo[3] if "(" in x)
        horas += sum(int(h) for h in re.findall(r"\((\d+)h\)", ciclo[4]))
        if horas != ciclo[5]:
            erros.append(f"ciclo {ciclo[0]}: soma {horas}h difere do total {ciclo[5]}h")

    if erros:
        print("ERROS DE VALIDAÇÃO:")
        for e in erros:
            print("  -", e)
        sys.exit(1)
    print(f"Validação ok: {len(fs)} RF, {len(nfs)} NF, {len(ss)} S, "
          f"{len(C.CASOS_DE_USO)} casos de uso, {len(conceitos)} conceitos, "
          f"{len(C.CONSULTAS)} consultas.")


def rastreabilidade():
    """Retorna {F: {coluna: bool}} para a matriz de rastreabilidade."""
    cols = list(uc_ids()) + ["Conceitos", "Consultas"]
    m = {f["cod"]: dict.fromkeys(cols, False) for f in C.RF}
    for i, uc in enumerate(C.CASOS_DE_USO):
        for r in uc["refs"]:
            if r in m:
                m[r][f"UC{i + 1}"] = True
    for c in C.CONCEITOS:
        for r in c[6]:
            if r in m:
                m[r]["Conceitos"] = True
    for q in C.CONSULTAS:
        for r in q[1]:
            if r in m:
                m[r]["Consultas"] = True
    return cols, m


# ---------------------------------------------------------------------------
# Markdown (arquivos de revisão)
# ---------------------------------------------------------------------------

NOTA_F9 = """> **Nota de revisão — exemplo numérico da pontuação (F9)**
> Busca com raio R = 10 km; média geral da plataforma M = 4,2; C = 5; Pd = Pn = 0,5.
>
> | Prestador | Distância | Avaliações | Nota ajustada N | Pontuação |
> |---|---|---|---|---|
> | A | 1 km | 2 (5 e 5) | (5×4,2 + 10)/7 = 4,43 | 0,5×0,9 + 0,5×0,886 = **0,89** |
> | C (novo) | 2 km | nenhuma | 4,2 | 0,5×0,8 + 0,5×0,84 = **0,82** |
> | B | 6 km | 40 (média 4,8) | (21 + 192)/45 = 4,73 | 0,5×0,4 + 0,5×0,947 = **0,67** |
>
> Ordem: A, C, B. Sem a média bayesiana, A teria nota 5,0 com apenas duas avaliações e C (sem
> avaliações) ficaria em último, justamente o problema do "prestador novo" descrito no tema.
> Com pesos 0,5/0,5, a distância pesa bastante (B é o melhor avaliado, mas está a 6 km).
> Os pesos são configuráveis (NF9.3) e devem ser calibrados nos testes de aceitação."""


def md_visao():
    L = [f"# 1. Visão Geral do Sistema", "",
         f"**Sistema:** {C.SISTEMA} — {C.SUBTITULO}  ",
         f"**Disciplina:** {C.DISCIPLINA} ({C.PROFESSOR})  ",
         "**Equipe:** " + "; ".join(f"{n} ({m})" for n, m in C.EQUIPE), "",
         "## 1.1. Problema", ""]
    for p in C.VISAO_PROBLEMA:
        L += [p, ""]
    L += ["## 1.2. Proposta", "", C.VISAO_PROPOSTA, "", "Principais funcionalidades:", ""]
    L += [f"- {x}" for x in C.VISAO_FUNCIONALIDADES] + [""]
    L += ["## 1.3. Atores", "", "| Ator | Descrição |", "|---|---|"]
    L += [f"| **{a}** | {d} |" for a, d in C.ATORES] + [""]
    L += ["## 1.4. Escopo", "", "**Contemplado nesta versão:**", ""]
    L += [f"- {x}" for x in C.ESCOPO_DENTRO] + ["", "**Fora do escopo desta versão:**", ""]
    L += [f"- {x}" for x in C.ESCOPO_FORA] + [""]
    return "\n".join(L)


def md_rf():
    n_nf = sum(len(f["nfs"]) for f in C.RF)
    n_des = sum(nf[3] for f in C.RF for nf in f["nfs"])
    n_trans = sum(not nf[4] for f in C.RF for nf in f["nfs"])
    L = ["# 2.1. Requisitos funcionais", "",
         "> **Legenda.** *Oculto (X)*: função executada pelo sistema sem o conhecimento explícito "
         "do usuário. *Desejável (X)*: pode ser atendido se houver tempo e recursos; `( )` = "
         "obrigatório. *Permanente (X)*: poucas chances de mudar; `( )` = transitório.", "",
         f"**Resumo:** {len(C.RF)} requisitos funcionais "
         f"({sum(f['oculto'] for f in C.RF)} ocultos), {n_nf} requisitos não-funcionais "
         f"({n_des} desejáveis, {n_trans} transitórios).", "",
         "## Índice", "", "| Código | Requisito funcional | Oculto | Nº de NFs |",
         "|---|---|:---:|:---:|"]
    L += [f"| {f['cod']} | {f['nome']} | {mark(f['oculto'])} | {len(f['nfs'])} |" for f in C.RF]
    L += [""]
    for f in C.RF:
        L += ["---", "", f"### {f['cod']} {f['nome']} — Oculto {mark(f['oculto'])}", "",
              f"**Descrição:** {f['desc']}", "",
              "| Nome | Restrição | Categoria | Desejável | Permanente |",
              "|---|---|---|:---:|:---:|"]
        for i, (nome, rest, cat, des, perm) in enumerate(f["nfs"]):
            L.append(f"| **{nf_code(f, i)}** {nome} | {rest} | {cat} | {mark(des)} | "
                     f"{mark(perm)} |")
        L.append("")
        if f["cod"] == "F9":
            L += [NOTA_F9, ""]
    return "\n".join(L)


def md_sup():
    L = ["# 2.2. Requisitos suplementares", "",
         "Restrições que se aplicam ao sistema como um todo, e não a uma função específica.", "",
         "| Nome | Restrição | Categoria | Desejável | Permanente |", "|---|---|---|:---:|:---:|"]
    for i, (nome, paras, cat, des, perm) in enumerate(C.SUPLEMENTARES):
        L.append(f"| **S{i + 1}** {nome} | {'<br>'.join(paras)} | {cat} | {mark(des)} | "
                 f"{mark(perm)} |")
    return "\n".join(L) + "\n"


def md_org():
    L = ["# 3. Organização dos requisitos", "", "## 3.1. Casos de Uso", "",
         "| Nome | Atores | Descrição | Referências cruzadas |", "|---|---|---|---|"]
    for uc in C.CASOS_DE_USO:
        L.append(f"| {uc['nome']} | {', '.join(uc['atores'])} | {uc['desc']} | "
                 f"{', '.join(uc['refs'])} |")
    L += ["", "## 3.2. Diagrama de Casos de Uso", "",
          "![Diagrama de casos de uso](diagramas/diagrama_casos_de_uso.png)", "",
          "*Prestador é uma especialização de Cliente (um prestador também pode contratar "
          "serviços).*", "",
          "## 3.3. Modelo Conceitual Preliminar", "",
          "![Modelo conceitual preliminar](diagramas/modelo_conceitual.png)", "",
          "*Sem métodos, sem multiplicidades e sem direção nas associações, como pede o modelo "
          "preliminar da Concepção.*", "",
          "## 3.4. Conceitos", "",
          "| Conceito | C | R | U | D | Observações | Referências cruzadas |",
          "|---|:-:|:-:|:-:|:-:|---|---|"]
    for nome, c, r, u, d, obs, refs in C.CONCEITOS:
        x = lambda v: "X" if v else ""
        L.append(f"| {nome} | {x(c)} | {x(r)} | {x(u)} | {x(d)} | {obs} | {', '.join(refs)} |")
    L += ["", "## 3.5. Consultas", "", "| Nome | Referências cruzadas |", "|---|---|"]
    L += [f"| {n} | {', '.join(r)} |" for n, r in C.CONSULTAS]

    cols, m = rastreabilidade()
    ucs = uc_ids()
    L += ["", "---", "", "## Apoio à revisão — matriz de rastreabilidade", "",
          "Verificação do alerta da aula: todo requisito funcional precisa estar em pelo menos um "
          "caso de uso, conceito (CRUD) ou consulta. *(Esta matriz não faz parte do formato do "
          "exemplo; é só para conferência.)*", "",
          "Casos de uso: " + "; ".join(f"**{k}** = {v}" for k, v in ucs.items()), "",
          "| RF | " + " | ".join(cols) + " |", "|---|" + ":-:|" * len(cols)]
    for f in C.RF:
        L.append(f"| {f['cod']} {f['nome']} | " +
                 " | ".join("X" if m[f['cod']][c] else "" for c in cols) + " |")
    return "\n".join(L) + "\n"


def md_plan():
    L = ["# 4. Planejamento Preliminar", "", "## 4.1. Planejamento de ciclos iterativos", "",
         "| Ciclo | Casos de uso | Manutenção de informações | Consultas | Observações | "
         "Esforço estimado |", "|:-:|---|---|---|---|:-:|"]
    for ciclo, ucs, crud, cons, obs, tot in C.CICLOS:
        L.append(f"| {ciclo} | {'<br>'.join(ucs)} | {'<br>'.join(crud)} | {'<br>'.join(cons)} "
                 f"| {obs} | {tot} h |")
    L += [f"| **Total** | | | | | **{sum(c[5] for c in C.CICLOS)} h** |", "",
          C.JUSTIFICATIVA_CICLOS, "", "## 4.2. Cronograma para o desenvolvimento", ""]
    blocos = [(i, i + 4) for i in range(1, C.DIAS_TOTAIS + 1, 5)]
    L.append("| Dias | " + " | ".join(f"{a}-{b}" for a, b in blocos) + " |")
    L.append("|---|" + ":-:|" * len(blocos))
    for linha, fases in C.CRONOGRAMA:
        cel = []
        for a, b in blocos:
            txt = ""
            for fase, ini, fim in fases:
                if ini <= a and b <= fim:
                    txt = fase if len(fase) <= 1 else "Impl."
            cel.append(txt)
        L.append(f"| {linha} | " + " | ".join(cel) + " |")
    L += ["", "**Legenda:** " + "; ".join(f"{n} ({s})" for s, n in C.LEGENDA_FASES) +
          "; Implantação (Impl.).", "", "| Fase | Responsável(is) | Cor |", "|---|---|---|"]
    L += [f"| {f} | {r} | {c} |" for f, r, c, _ in C.RESPONSAVEIS]
    L += [""] + [f"**Obs.:** {C.OBS_CRONOGRAMA[0]}", "", C.OBS_CRONOGRAMA[1], "",
                 "## 4.3. Prioridade para melhores práticas do RUP", ""]
    for i, (titulo, texto) in enumerate(C.RUP, 1):
        L += [f"**{i}. {titulo}**", "", texto, ""]
    return "\n".join(L)


def gerar_md():
    arquivos = {
        "1 - Visão Geral.md": md_visao(),
        "2.1 - Requisitos Funcionais.md": md_rf(),
        "2.2 - Requisitos Suplementares.md": md_sup(),
        "3 - Organização dos Requisitos.md": md_org(),
        "4 - Planejamento Preliminar.md": md_plan(),
    }
    for nome, txt in arquivos.items():
        (RAIZ / nome).write_text(txt, encoding="utf-8")
    print("Markdown:", ", ".join(arquivos))


# ---------------------------------------------------------------------------
# Diagramas (SVG -> PNG)
# ---------------------------------------------------------------------------

AZUL_FILL, AZUL_TRACO, TEXTO = "#BFE3F5", "#2F6A8F", "#1A1A1A"
FONTE = "Arial"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_texto(x, y, t, size=14, anchor="middle", weight="normal", fill=TEXTO):
    return (f'<text x="{x}" y="{y}" font-family="{FONTE}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{esc(t)}</text>')


def svg_ator(x, y, nome):
    s = AZUL_TRACO
    return "\n".join([
        f'<circle cx="{x}" cy="{y}" r="13" fill="#7FC4E8" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y + 13}" x2="{x}" y2="{y + 50}" stroke="{s}" stroke-width="1.6"/>',
        f'<line x1="{x - 20}" y1="{y + 26}" x2="{x + 20}" y2="{y + 26}" stroke="{s}" '
        f'stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y + 50}" x2="{x - 16}" y2="{y + 78}" stroke="{s}" '
        f'stroke-width="1.6"/>',
        f'<line x1="{x}" y1="{y + 50}" x2="{x + 16}" y2="{y + 78}" stroke="{s}" '
        f'stroke-width="1.6"/>',
        svg_texto(x, y + 98, nome, 14, weight="bold"),
    ])


def borda_elipse(cx, cy, rx, ry, px, py):
    dx, dy = px - cx, py - cy
    k = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return cx + dx * k, cy + dy * k


def diagrama_casos_de_uso():
    W, H = 980, 560
    rx, ry = 112, 30
    ucs = {
        "Contratar serviço": (420, 110), "Avaliar prestador": (420, 195),
        "Tornar-se prestador": (420, 280), "Responder solicitação": (420, 380),
        "Concluir serviço": (420, 465), "Moderar denúncia": (665, 280),
    }
    atores = {"Cliente": (140, 150), "Prestador": (140, 395), "Administrador": (905, 255)}
    assert set(ucs) == {u["nome"] for u in C.CASOS_DE_USO}

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<rect x="260" y="30" width="540" height="505" fill="none" stroke="#555" '
           f'stroke-width="1.4"/>', svg_texto(530, 54, C.SISTEMA, 16, weight="bold")]

    for uc in C.CASOS_DE_USO:
        cx, cy = ucs[uc["nome"]]
        for ator in uc["atores"]:
            ax, ay = atores[ator]
            px = ax + 22 if ax < cx else ax - 22
            py = ay + 32
            ex, ey = borda_elipse(cx, cy, rx, ry, px, py)
            out.append(f'<line x1="{px}" y1="{py}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#333" '
                       f'stroke-width="1.3"/>')

    # generalização Prestador -> Cliente (triângulo vazado no Cliente)
    cx_, top = atores["Cliente"][0], atores["Cliente"][1] + 106
    out.append(f'<line x1="{cx_}" y1="{top + 16}" x2="{cx_}" y2="{atores["Prestador"][1] - 15}" '
               f'stroke="#333" stroke-width="1.3"/>')
    out.append(f'<polygon points="{cx_},{top} {cx_ - 9},{top + 16} {cx_ + 9},{top + 16}" '
               f'fill="white" stroke="#333" stroke-width="1.3"/>')

    for nome, (cx, cy) in ucs.items():
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{AZUL_FILL}" '
                   f'stroke="{AZUL_TRACO}" stroke-width="1.6"/>')
        out.append(svg_texto(cx, cy + 5, nome, 14))
    for nome, (x, y) in atores.items():
        out.append(svg_ator(x, y, nome))
    out.append("</svg>")
    return "\n".join(out)


def diagrama_conceitual():
    W, H = 1000, 660
    BW, HEAD, LH, PAD = 240, 30, 19, 10
    pos = {
        "Denúncia": (30, 30), "Administrador": (380, 30), "Categoria": (730, 30),
        "Usuário": (30, 250), "Prestador": (380, 250), "Serviço": (730, 250),
        "Avaliação": (30, 480), "Solicitação": (380, 480),
    }
    assert set(pos) == set(C.CLASSES)
    # pontos de ligação desenhados à mão para evitar cruzamentos
    ligacoes = {
        ("Denúncia", "Administrador"): ((270, 65), (380, 65), (325, 57, "middle")),
        ("Administrador", "Categoria"): ((620, 65), (730, 65), (675, 57, "middle")),
        ("Usuário", "Denúncia"): ((150, 250), (150, 165), (158, 213, "start")),
        ("Serviço", "Categoria"): ((850, 250), (850, 127), (858, 194, "start")),
        ("Usuário", "Prestador"): ((270, 310), (380, 310), (325, 302, "middle")),
        ("Prestador", "Serviço"): ((620, 310), (730, 310), (675, 302, "middle")),
        ("Solicitação", "Avaliação"): ((380, 540), (270, 540), (325, 532, "middle")),
        ("Usuário", "Solicitação"): ((240, 423), (420, 480), (318, 438, "middle")),
        ("Solicitação", "Serviço"): ((580, 480), (760, 404), (690, 430, "middle")),
    }
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']
    for a, b, rotulo in C.ASSOCIACOES:
        (x1, y1), (x2, y2), (lx, ly, anc) = ligacoes[(a, b)]
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" '
                   f'stroke-width="1.3"/>')
        w = len(rotulo) * 6.6
        bx = lx - w / 2 if anc == "middle" else lx - 2
        out.append(f'<rect x="{bx:.0f}" y="{ly - 12}" width="{w + 4:.0f}" height="16" '
                   f'fill="white"/>')
        out.append(svg_texto(lx, ly, rotulo, 12, anchor=anc, fill="#333"))
    for nome, attrs in C.CLASSES.items():
        x, y = pos[nome]
        h = HEAD + LH * len(attrs) + PAD
        out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{h}" fill="white" '
                   f'stroke="{AZUL_TRACO}" stroke-width="1.6"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{HEAD}" fill="{AZUL_FILL}" '
                   f'stroke="{AZUL_TRACO}" stroke-width="1.6"/>')
        out.append(svg_texto(x + BW / 2, y + 20, nome, 14, weight="bold"))
        for i, a in enumerate(attrs):
            out.append(svg_texto(x + 10, y + HEAD + 16 + i * LH, "+ " + a, 12, anchor="start"))
    out.append("</svg>")
    return "\n".join(out)


def gerar_diagramas():
    DIAG.mkdir(exist_ok=True)
    pngs = {}
    for nome, svg in [("diagrama_casos_de_uso", diagrama_casos_de_uso()),
                      ("modelo_conceitual", diagrama_conceitual())]:
        (DIAG / f"{nome}.svg").write_text(svg, encoding="utf-8")
        pix = pymupdf.open(str(DIAG / f"{nome}.svg"))[0].get_pixmap(dpi=150)
        pix.save(str(DIAG / f"{nome}.png"))
        pngs[nome] = DIAG / f"{nome}.png"
    print("Diagramas:", ", ".join(p.name for p in pngs.values()))
    return pngs


# ---------------------------------------------------------------------------
# Documento Word
# ---------------------------------------------------------------------------

CINZA = "D9D9D9"
CORES_FASE = {"A": "E6A0A0", "P": "E6A0A0", "I": "FFE08A", "T": "A9C9D3", "C": "E4E4E4",
              "Implantação": "B7D7A8"}
FONTE_DOC = "Calibri"
TAM_TAB = 10


def fixar_fonte(style, nome=FONTE_DOC):
    style.font.name = nome
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(qn(a), None)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(a), nome)


def sombrear(cell, cor):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    # ordem do schema: ... tcBorders, shd, noWrap, tcMar, textDirection, tcFitText, vAlign
    depois = [tcpr.find(qn(f"w:{t}")) for t in ("noWrap", "tcMar", "textDirection",
                                                  "tcFitText", "vAlign", "hideMark")]
    depois = [e for e in depois if e is not None]
    if depois:
        depois[0].addprevious(shd)
    else:
        tcpr.append(shd)


def escrever(cell, partes, align=None, size=TAM_TAB, italic=False):
    """partes: str ou lista de (texto, negrito). Aceita lista de parágrafos via '\n\n'."""
    if isinstance(partes, str):
        partes = [(partes, False)]
    p = cell.paragraphs[0]
    p.text = ""
    for texto, negrito in partes:
        blocos = texto.split("\n\n")
        for j, bloco in enumerate(blocos):
            if j > 0:
                p = cell.add_paragraph()
            r = p.add_run(bloco)
            r.bold = negrito
            r.italic = italic
            r.font.size = Pt(size)
    for par in cell.paragraphs:
        par.paragraph_format.space_before = Pt(1)
        par.paragraph_format.space_after = Pt(1)
        par.paragraph_format.line_spacing = 1.0
        if align:
            par.alignment = align
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def nova_tabela(doc, larguras_cm):
    t = doc.add_table(rows=0, cols=len(larguras_cm))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblpr = t._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for lado, v in (("left", 85), ("right", 85)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    look = tblpr.find(qn("w:tblLook"))
    if look is not None:
        look.addprevious(mar)
    else:
        tblpr.append(mar)
    for i, w in enumerate(larguras_cm):
        t.columns[i].width = Cm(w)
    t._larguras = larguras_cm
    return t


def nova_linha(t, nao_quebrar=True):
    row = t.add_row()
    for i, c in enumerate(row.cells):
        c.width = Cm(t._larguras[i])
    if nao_quebrar:
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
    row._larguras = t._larguras
    return row


def mesclar(row, i, j):
    c = row.cells[i].merge(row.cells[j])
    c.width = Cm(sum(row._larguras[i:j + 1]))
    return c


def repetir_cabecalho(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def manter_junto(t, ate=None):
    rows = t.rows if ate is None else t.rows[:ate]
    ultimo = len(t.rows) - 1
    for k, row in enumerate(rows):
        if ate is None and k == ultimo:
            break
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True


def paragrafo(doc, texto, negrito_prefixo=None, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
              after=6, italic=False):
    p = doc.add_paragraph()
    if negrito_prefixo:
        r = p.add_run(negrito_prefixo)
        r.bold = True
        r.font.size = Pt(size)
    r = p.add_run(texto)
    r.font.size = Pt(size)
    r.italic = italic
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    return p


def espaco(doc, pts=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = Pt(pts)
    return p


def quebra_pagina(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def campo(paragraph, instr, placeholder=""):
    r = paragraph.add_run()
    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    r._r.append(b)
    r = paragraph.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r._r.append(it)
    r = paragraph.add_run()
    s = OxmlElement("w:fldChar")
    s.set(qn("w:fldCharType"), "separate")
    r._r.append(s)
    paragraph.add_run(placeholder)
    r = paragraph.add_run()
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    r._r.append(e)


def configurar_estilos(doc):
    fixar_fonte(doc.styles["Normal"])
    doc.styles["Normal"].font.size = Pt(11)
    for nome, tam, antes, depois in (("Heading 1", 20, 18, 10), ("Heading 2", 14, 14, 8)):
        st = doc.styles[nome]
        fixar_fonte(st)
        st.font.size = Pt(tam)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        cor = st.element.rPr.find(qn("w:color"))
        for a in ("w:themeColor", "w:themeShade", "w:themeTint"):
            cor.attrib.pop(qn(a), None)
        st.paragraph_format.space_before = Pt(antes)
        st.paragraph_format.space_after = Pt(depois)
        st.paragraph_format.keep_with_next = True
    fixar_fonte(doc.styles["List Bullet"])
    for nome in ("TOC 1", "TOC 2"):
        try:
            fixar_fonte(doc.styles[nome])
        except KeyError:
            pass


def margens(section, paisagem=False):
    if paisagem:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = Cm(29.7), Cm(21.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)


def capa(doc):
    def linha(texto, tam=12, neg=False, antes=0, depois=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(antes)
        p.paragraph_format.space_after = Pt(depois)
        r = p.add_run(texto)
        r.font.size, r.bold = Pt(tam), neg

    linha(C.INSTITUICAO, 14, True, antes=60)
    linha(C.DISCIPLINA)
    linha(C.PROFESSOR)
    linha(C.SISTEMA, 40, True, antes=150)
    linha(C.SUBTITULO, 14)
    linha("Fase 1 – Concepção", 13, True, antes=18, depois=0)
    linha("Análise e Especificação de Requisitos do Software", 13, True)
    linha("Equipe", 12, True, antes=130)
    for nome, mat in C.EQUIPE:
        linha(f"{nome} – {mat}", depois=0)
    linha(C.DATA, antes=90)
    quebra_pagina(doc)


def sumario(doc):
    p = doc.add_paragraph()
    r = p.add_run("Sumário")
    r.bold, r.font.size = True, Pt(20)
    p.paragraph_format.space_after = Pt(12)
    campo(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u',
          "Clique com o botão direito e escolha “Atualizar campo” para gerar o sumário.")
    quebra_pagina(doc)


def secao_visao(doc):
    doc.add_heading("1. Visão Geral do Sistema", level=1)
    for rot, txt in (("Sistema: ", f"{C.SISTEMA} – {C.SUBTITULO}."),
                     ("Equipe: ", "; ".join(f"{n} ({m})" for n, m in C.EQUIPE) + ".")):
        paragrafo(doc, txt, rot, after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_heading("1.1. Problema", level=2)
    for p in C.VISAO_PROBLEMA:
        paragrafo(doc, p)
    doc.add_heading("1.2. Proposta", level=2)
    paragrafo(doc, C.VISAO_PROPOSTA)
    paragrafo(doc, "Principais funcionalidades:", after=2)
    for x in C.VISAO_FUNCIONALIDADES:
        doc.add_paragraph(x, style="List Bullet").paragraph_format.space_after = Pt(1)
    doc.add_heading("1.3. Atores", level=2)
    t = nova_tabela(doc, [3.2, 13.8])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Ator", "Descrição")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    for a, d in C.ATORES:
        row = nova_linha(t)
        escrever(row.cells[0], [(a, True)])
        escrever(row.cells[1], d, WD_ALIGN_PARAGRAPH.JUSTIFY)
    doc.add_heading("1.4. Escopo", level=2)
    paragrafo(doc, "Contemplado nesta versão:", after=2).runs[0].bold = True
    for x in C.ESCOPO_DENTRO:
        doc.add_paragraph(x, style="List Bullet").paragraph_format.space_after = Pt(1)
    p = paragrafo(doc, "Fora do escopo desta versão:", after=2)
    p.runs[0].bold = True
    p.paragraph_format.space_before = Pt(6)
    for x in C.ESCOPO_FORA:
        doc.add_paragraph(x, style="List Bullet").paragraph_format.space_after = Pt(1)


LARG_NF = [3.1, 6.6, 3.2, 1.95, 2.15]


def cabecalho_nf(t):
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Nome", "Restrição", "Categoria", "Desejável", "Permanente")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    return row


def tabela_rf(doc, f):
    t = nova_tabela(doc, LARG_NF)
    row = nova_linha(t)
    esq, dir_ = mesclar(row, 0, 1), mesclar(row, 2, 4)
    escrever(esq, [(f["cod"], True), (" " + f["nome"], False)])
    escrever(dir_, f"Oculto {mark(f['oculto'])}")
    row = nova_linha(t)
    escrever(mesclar(row, 0, 4), [("Descrição: ", True), (f["desc"], False)],
             WD_ALIGN_PARAGRAPH.JUSTIFY)
    row = nova_linha(t)
    c = mesclar(row, 0, 4)
    escrever(c, [("Requisitos Não-Funcionais", True)])
    sombrear(c, CINZA)
    cabecalho_nf(t)
    for i, (nome, rest, cat, des, perm) in enumerate(f["nfs"]):
        row = nova_linha(t)
        escrever(row.cells[0], [(nf_code(f, i), True), (" " + nome, False)],
                 WD_ALIGN_PARAGRAPH.LEFT)
        escrever(row.cells[1], rest, WD_ALIGN_PARAGRAPH.LEFT)
        escrever(row.cells[2], cat)
        escrever(row.cells[3], mark(des), WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[4], mark(perm), WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t)
    espaco(doc, 14)


def secao_concepcao(doc):
    quebra_pagina(doc)
    doc.add_heading("2. Concepção", level=1)
    doc.add_heading("2.1. Requisitos funcionais", level=2)
    p = paragrafo(doc, "Oculto (X): função executada pelo sistema sem o conhecimento explícito "
                  "do usuário. Desejável (X): pode ser atendido se houver tempo e recursos; ( ) = "
                  "obrigatório. Permanente (X): poucas chances de mudar; ( ) = transitório.",
                  "Legenda: ", size=9, italic=True, after=10)
    for f in C.RF:
        tabela_rf(doc, f)

    quebra_pagina(doc)
    doc.add_heading("2.2. Requisitos suplementares", level=2)
    t = nova_tabela(doc, LARG_NF)
    repetir_cabecalho(cabecalho_nf(t))
    for i, (nome, paras, cat, des, perm) in enumerate(C.SUPLEMENTARES):
        row = nova_linha(t)
        escrever(row.cells[0], [(f"S{i + 1}", True), (" " + nome, False)])
        escrever(row.cells[1], "\n\n".join(paras), WD_ALIGN_PARAGRAPH.LEFT)
        escrever(row.cells[2], cat)
        escrever(row.cells[3], mark(des), WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[4], mark(perm), WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t, ate=1)


def figura(doc, png, legenda, largura=16.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(png), width=Cm(largura))
    paragrafo(doc, legenda, size=9, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)


def secao_organizacao(doc, pngs):
    quebra_pagina(doc)
    doc.add_heading("3. Organização dos requisitos", level=1)
    doc.add_heading("3.1. Casos de Uso", level=2)
    t = nova_tabela(doc, [3.2, 2.6, 8.4, 2.8])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Nome", "Atores", "Descrição", "Referências cruzadas")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    repetir_cabecalho(row)
    for uc in C.CASOS_DE_USO:
        row = nova_linha(t)
        escrever(row.cells[0], uc["nome"])
        escrever(row.cells[1], ", ".join(uc["atores"]))
        escrever(row.cells[2], uc["desc"], WD_ALIGN_PARAGRAPH.JUSTIFY)
        escrever(row.cells[3], ", ".join(uc["refs"]), WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t, ate=1)

    doc.add_heading("3.2. Diagrama de Casos de Uso", level=2)
    figura(doc, pngs["diagrama_casos_de_uso"],
           "Figura 1 – Diagrama de casos de uso do Bicus (versão da Concepção). Prestador é uma "
           "especialização de Cliente.")

    quebra_pagina(doc)
    doc.add_heading("3.3. Modelo Conceitual Preliminar", level=2)
    figura(doc, pngs["modelo_conceitual"],
           "Figura 2 – Modelo conceitual preliminar (sem métodos, multiplicidades ou direção nas "
           "associações).")

    doc.add_heading("3.4. Conceitos", level=2)
    t = nova_tabela(doc, [2.6, 0.75, 0.75, 0.75, 0.75, 8.6, 2.8])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Conceito", "C", "R", "U", "D", "Observações",
                                  "Referências cruzadas")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    repetir_cabecalho(row)
    for nome, c_, r_, u_, d_, obs, refs in C.CONCEITOS:
        row = nova_linha(t)
        escrever(row.cells[0], nome)
        for k, v in enumerate((c_, r_, u_, d_), 1):
            escrever(row.cells[k], "X" if v else "", WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[5], obs, WD_ALIGN_PARAGRAPH.JUSTIFY)
        escrever(row.cells[6], ", ".join(refs), WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t, ate=1)

    doc.add_heading("3.5. Consultas", level=2)
    t = nova_tabela(doc, [11.0, 6.0])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Nome", "Referências cruzadas")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    for nome, refs in C.CONSULTAS:
        row = nova_linha(t)
        escrever(row.cells[0], nome)
        escrever(row.cells[1], ", ".join(refs), WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t)


def secao_planejamento(doc):
    quebra_pagina(doc)
    doc.add_heading("4. Planejamento Preliminar", level=1)
    doc.add_heading("4.1. Planejamento de ciclos iterativos", level=2)
    t = nova_tabela(doc, [1.4, 3.6, 3.3, 2.1, 4.6, 2.0])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Ciclos", "Casos de uso", "Manutenção de informações",
                                  "Consultas", "Observações", "Esforço estimado")):
        escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER)
        sombrear(c, CINZA)
    for ciclo, ucs, crud, cons, obs, tot in C.CICLOS:
        row = nova_linha(t)
        escrever(row.cells[0], ciclo, WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[1], "\n\n".join(ucs), WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[2], "\n\n".join(crud), WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[3], "\n\n".join(cons), WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[4], obs, WD_ALIGN_PARAGRAPH.CENTER)
        escrever(row.cells[5], f"{tot} h", WD_ALIGN_PARAGRAPH.CENTER)
    row = nova_linha(t)
    escrever(mesclar(row, 0, 4), [("Total", True)], WD_ALIGN_PARAGRAPH.RIGHT)
    escrever(row.cells[5], [(f"{sum(c[5] for c in C.CICLOS)} h", True)],
             WD_ALIGN_PARAGRAPH.CENTER)
    manter_junto(t)
    espaco(doc, 8)
    paragrafo(doc, C.JUSTIFICATIVA_CICLOS)

    # 4.2 em página paisagem
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    margens(sec, paisagem=True)
    doc.add_heading("4.2. Cronograma para o desenvolvimento", level=2)
    blocos = [(i, i + 4) for i in range(1, C.DIAS_TOTAIS + 1, 5)]
    larg = [2.3] + [(25.7 - 2.3) / len(blocos)] * len(blocos)
    t = nova_tabela(doc, larg)
    mar = t._tbl.tblPr.find(qn("w:tblCellMar"))
    for e in mar:
        e.set(qn("w:w"), "30")
    row = nova_linha(t)
    escrever(row.cells[0], [("Dias:", True)], WD_ALIGN_PARAGRAPH.CENTER, size=8)
    sombrear(row.cells[0], CINZA)
    for k, (a, b) in enumerate(blocos, 1):
        escrever(row.cells[k], [(f"{a}-{b}", True)], WD_ALIGN_PARAGRAPH.CENTER, size=8)
        sombrear(row.cells[k], CINZA)
    for linha, fases in C.CRONOGRAMA:
        row = nova_linha(t)
        row.height = Cm(0.9)
        escrever(row.cells[0], linha, size=9)
        row.cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        k = 1
        while k <= len(blocos):
            a, b = blocos[k - 1]
            achou = None
            for fase, ini, fim in fases:
                if ini <= a and b <= fim:
                    achou = (fase, ini, fim)
            if achou and achou[0] == "Implantação":
                n = (achou[2] - achou[1] + 1) // 5
                cel = mesclar(row, k, k + n - 1) if n > 1 else row.cells[k]
                escrever(cel, [("Impl.", True)], WD_ALIGN_PARAGRAPH.CENTER, size=9)
                sombrear(cel, CORES_FASE["Implantação"])
                cel.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                k += n
                continue
            cel = row.cells[k]
            if achou:
                escrever(cel, [(achou[0], True)], WD_ALIGN_PARAGRAPH.CENTER, size=10)
                sombrear(cel, CORES_FASE[achou[0]])
                cel.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            k += 1
    manter_junto(t)
    espaco(doc, 8)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Legenda: ")
    r.bold = True
    for i, (sig, nome) in enumerate(C.LEGENDA_FASES):
        p.add_run(("; " if i else "") + f"{nome} (")
        p.add_run(sig).bold = True
        p.add_run(")")
    p.add_run("; Implantação (")
    p.add_run("Impl.").bold = True
    p.add_run(").")

    t = nova_tabela(doc, [5.2, 11.0, 3.0])
    row = nova_linha(t)
    for c, txt in zip(row.cells, ("Fase", "Responsável(is)", "Cor")):
        escrever(c, [(txt, True)])
        sombrear(c, "B7B7B7")
    for fase, resp, cor, chave in C.RESPONSAVEIS:
        row = nova_linha(t)
        escrever(row.cells[0], [(fase, True)])
        escrever(row.cells[1], resp)
        escrever(row.cells[2], cor)
        sombrear(row.cells[2], CORES_FASE[chave])
    manter_junto(t)
    espaco(doc, 8)
    paragrafo(doc, C.OBS_CRONOGRAMA[0], "Obs.: ", size=10)
    paragrafo(doc, C.OBS_CRONOGRAMA[1], size=10)

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    margens(sec)
    doc.add_heading("4.3. Prioridade para melhores práticas do RUP", level=2)
    for i, (titulo, texto) in enumerate(C.RUP, 1):
        p = paragrafo(doc, "", f"{i}. {titulo}", after=3)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(6)
        paragrafo(doc, texto, after=6).paragraph_format.first_line_indent = Cm(1.0)


def rodape(doc):
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    campo(p, "PAGE", "1")
    for r in p.runs:
        r.font.size = Pt(9)


def modo_atual(doc):
    """Evita o 'Modo de Compatibilidade' do modelo padrão do python-docx."""
    for cs in doc.settings.element.iter(qn("w:compatSetting")):
        if cs.get(qn("w:name")) == "compatibilityMode":
            cs.set(qn("w:val"), "15")


def gerar_docx(pngs):
    doc = Document()
    modo_atual(doc)
    configurar_estilos(doc)
    margens(doc.sections[0])
    rodape(doc)
    capa(doc)
    sumario(doc)
    secao_visao(doc)
    secao_concepcao(doc)
    secao_organizacao(doc, pngs)
    secao_planejamento(doc)
    doc.core_properties.title = f"{C.SISTEMA} – Concepção (F1)"
    doc.core_properties.author = ", ".join(n for n, _ in C.EQUIPE)
    doc.save(str(DOCX))
    print("Word:", DOCX.name)


if __name__ == "__main__":
    validar()
    gerar_md()
    pngs = gerar_diagramas()
    gerar_docx(pngs)
