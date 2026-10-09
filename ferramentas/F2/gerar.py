# -*- coding: utf-8 -*-
"""
Ferramentas da F2 (Análise de Pontos de Função) do Bicus — FORA do repositório.

O documento entregue (D:/UFV/Bicus/F2 - .../Bicus - F2 Análise de Pontos de Função.docx) é editado
à mão pelo grupo e é a versão oficial: este módulo NÃO gera mais o documento inteiro. Ele guarda:
  - os dados e o cálculo da contagem (conteudo_f2.py) e as funções que montam as tabelas;
  - o desenho dos protótipos (prototipos.py) e do modelo conceitual.
As alterações no .docx são aplicadas por scripts (ex.: aplicar_v3.py), que abrem o .docx do grupo,
trocam só os trechos necessários e salvam.

Uso direto:  python gerar.py   -> valida a contagem e desenha as figuras em saida/
"""
import importlib.util
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

AQUI = Path(__file__).resolve().parent              # .../Bicus/ferramentas/F2
FERRAMENTAS = AQUI.parent
RAIZ = FERRAMENTAS.parent / "F2 - Análise de Pontos de Função"
F1_GER = FERRAMENTAS / "F1"
F1_DIAG = F1_GER / "diagramas"
SAIDA = AQUI / "saida"
PROTO = SAIDA / "prototipos"
DIAG = SAIDA / "diagramas"
DOCX = RAIZ / "Bicus - F2 Análise de Pontos de Função.docx"

sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(F1_GER))
_spec = importlib.util.spec_from_file_location("gerar_f1", F1_GER / "gerar.py")
G1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G1)
import conteudo as C1          # noqa: E402  (conteúdo da F1)
import conteudo_f2 as C2       # noqa: E402
import prototipos as P         # noqa: E402

# ---------------------------------------------------------------------------
# Regras da aula de APF
# ---------------------------------------------------------------------------

_MATRIZ = [["Simples", "Simples", "Médio"],
           ["Simples", "Médio", "Complexo"],
           ["Médio", "Complexo", "Complexo"]]

PESOS = {
    "EE": {"Simples": 3, "Médio": 4, "Complexo": 6},
    "SE": {"Simples": 4, "Médio": 5, "Complexo": 7},
    "CE": {"Simples": 3, "Médio": 4, "Complexo": 6},
    "ALI": {"Simples": 7, "Médio": 10, "Complexo": 15},
    "AIE": {"Simples": 5, "Médio": 7, "Complexo": 10},
}
NOMES_TIPO = {"EE": "Entradas Externas", "SE": "Saídas Externas", "CE": "Consultas Externas",
              "ALI": "Arquivos Lógicos Internos", "AIE": "Arquivos de Interface Externa"}


def complexidade(tipo, ar_tr, td):
    """Tabelas de complexidade da aula (ALI/AIE por TR x TD; EE, CE e SE por AR x TD)."""
    if tipo in ("ALI", "AIE"):
        lin = 0 if ar_tr <= 1 else (1 if ar_tr <= 5 else 2)
        col = 0 if td <= 19 else (1 if td <= 50 else 2)
    elif tipo == "EE":
        lin = 0 if ar_tr <= 1 else (1 if ar_tr == 2 else 2)
        col = 0 if td <= 4 else (1 if td <= 15 else 2)
    else:
        lin = 0 if ar_tr <= 1 else (1 if ar_tr <= 3 else 2)
        col = 0 if td <= 5 else (1 if td <= 19 else 2)
    return _MATRIZ[lin][col]


def teto(x):
    return math.ceil(round(x, 6))


def r2(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def fmt(x, casas=2):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def rs(x):
    return "R$ " + fmt(x, 2)


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------

def nome_atributo(a):
    return a.split(":")[0].strip()


def tipo_atributo(a):
    return a.split(":")[1].split("[")[0].strip()


def td_classe(nome):
    """TD de um ALI: atributos próprios da classe + FKs das associações que ela guarda."""
    return ([nome_atributo(a) for a in C2.MODELO_CLASSES[nome]] +
            [f"{a['fk']} (FK)" for a in C2.MODELO_ASSOCIACOES if a["de"] == nome])


def tr_classe(nome):
    """TR de um ALI: 1 + subclasses (superclasse) + superclasse (subclasse)."""
    return (1 + sum(1 for _, sup in C2.MODELO_HERANCA if sup == nome)
            + sum(1 for sub, _ in C2.MODELO_HERANCA if sub == nome))


def funcoes():
    """Lista única de funções com tipo, contagens, complexidade e PF."""
    out = []
    for f in C2.ALI:
        td, tr = td_classe(f["nome"]), tr_classe(f["nome"])
        c = complexidade("ALI", tr, len(td))
        out.append(dict(f, tipo="ALI", tr=tr, td=td, n_ar=tr, n_td=len(td), compl=c,
                        pf=PESOS["ALI"][c]))
    for f in C2.AIE:
        c = complexidade("AIE", f["tr"], len(f["td"]))
        out.append(dict(f, tipo="AIE", n_ar=f["tr"], n_td=len(f["td"]), compl=c,
                        pf=PESOS["AIE"][c]))
    for tipo, lista in (("EE", C2.EE), ("CE", C2.CE), ("SE", C2.SE)):
        for f in lista:
            c = complexidade(tipo, len(f["ar"]), len(f["td"]))
            out.append(dict(f, tipo=tipo, n_ar=len(f["ar"]), n_td=len(f["td"]), compl=c,
                            pf=PESOS[tipo][c]))
    return out


def medicao():
    fs = funcoes()
    por_tipo = {t: [f for f in fs if f["tipo"] == t] for t in PESOS}
    resumo = {t: {c: sum(1 for f in por_tipo[t] if f["compl"] == c)
                  for c in ("Simples", "Médio", "Complexo")} for t in PESOS}
    subtotal = {t: sum(f["pf"] for f in por_tipo[t]) for t in PESOS}
    pfb = sum(subtotal.values())
    pfb_m = teto(pfb * (1 + C2.MARGEM))
    ni = sum(c[1] for c in C2.CGS)
    fa = round(0.65 + 0.01 * ni, 2)
    pfa = teto(pfb_m * fa)
    return dict(fs=fs, por_tipo=por_tipo, resumo=resumo, subtotal=subtotal, pfb=pfb,
                pfb_m=pfb_m, ni=ni, fa=fa, pfa=pfa)


def extras(prazo):
    fixos = sum(v for _, v in C2.EXTRAS_FIXOS)
    mensais = sum(v for _, v in C2.EXTRAS_MENSAIS)
    return fixos, mensais, r2(fixos + mensais * prazo)


def estimativa(pfa, hpf, equipe=C2.EQUIPE):
    esforco = teto(pfa * hpf)
    hm = r2(esforco / C2.HORAS_MES)
    prazo = r2(hm / equipe)
    custo_equipe = r2(equipe * C2.HORAS_MES * C2.VALOR_HORA * prazo)
    _, _, ext = extras(prazo)
    preco = r2((custo_equipe + ext) * (1 + C2.LUCRO))
    return dict(hpf=hpf, esforco=esforco, hm=hm, prazo=prazo, custo_equipe=custo_equipe,
                extras=ext, preco=preco, exato=pfa * hpf)


def adotado(m):
    return estimativa(m["pfa"], next(c["hpf"] for c in C2.CENARIOS if c["adotado"]))


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

def validar(m):
    erros = []
    arquivos = {f["nome"] for f in C2.ALI} | {f["nome"] for f in C2.AIE}
    erros += validar_modelo()
    cods = [f["cod"] for f in m["fs"]]
    if len(cods) != len(set(cods)):
        erros.append("códigos de função repetidos")
    usadas = set()
    for f in m["fs"]:
        if len(set(f["td"])) != len(f["td"]):
            erros.append(f"{f['cod']}: TD repetido")
        if f["tipo"] in ("EE", "CE", "SE"):
            for a in f["ar"]:
                if a not in arquivos:
                    erros.append(f"{f['cod']}: AR inexistente '{a}'")
            for t in f["telas"]:
                if t not in P.TELAS:
                    erros.append(f"{f['cod']}: tela inexistente {t}")
                usadas.add(t)
    nao_usadas = sorted(set(P.TELAS) - usadas)
    if nao_usadas:
        erros.append("telas sem nenhuma função: " + ", ".join(nao_usadas))
    nas_pranchas = [t for _, _, ts, _ in P.PRANCHAS for t in ts]
    if sorted(nas_pranchas) != sorted(P.TELAS):
        erros.append("as pranchas não cobrem exatamente as telas declaradas")
    rfs = {r for f in m["fs"] if f["tipo"] in ("EE", "CE", "SE") for r in f["rf"]}
    faltam = [f["cod"] for f in C1.RF if f["cod"] not in rfs]
    if faltam:
        erros.append("requisitos funcionais sem função APF: " + ", ".join(faltam))
    if len(C2.CGS) != 14 or any(not 0 <= c[1] <= 5 for c in C2.CGS):
        erros.append("as 14 características gerais devem ter NI entre 0 e 5")
    if sum(1 for c in C2.CENARIOS if c["adotado"]) != 1:
        erros.append("deve haver exatamente um cenário adotado")
    if erros:
        print("ERROS DE VALIDAÇÃO:")
        for e in erros:
            print("  -", e)
        sys.exit(1)
    n = {t: len(m["por_tipo"][t]) for t in PESOS}
    print(f"Validação ok: {n['ALI']} ALI, {n['AIE']} AIE, {n['EE']} EE, {n['CE']} CE, "
          f"{n['SE']} SE; {len(P.TELAS)} telas; todos os RF da F1 rastreados.")


TIPOS_SIMPLES = {"String", "Data", "Real", "Inteiro", "Moeda", "Imagem", "Booleano"}


def validar_modelo():
    """Coerência do modelo revisado consigo mesmo, com a F1 e com o desenho."""
    erros = []
    classes = set(C2.MODELO_CLASSES)
    if {f["nome"] for f in C2.ALI} != classes:
        erros.append(f"ALIs diferentes das classes do modelo: "
                     f"{({f['nome'] for f in C2.ALI}) ^ classes}")
    sem_classe = {c[0] for c in C1.CONCEITOS} - classes
    if sem_classe:
        erros.append(f"conceitos da F1 sem classe no modelo revisado: {sem_classe}")
    for a in C2.MODELO_ASSOCIACOES:
        if a["de"] not in classes or a["para"] not in classes:
            erros.append(f"associação com classe inexistente: {a}")
        if (a["de"], a["para"], a["rotulo"]) not in MODELO_LIGACOES:
            erros.append(f"associação sem traçado no desenho: {a['de']}–{a['para']}")
    for sub, sup in C2.MODELO_HERANCA:
        if sub not in classes or sup not in classes or (sub, sup) not in MODELO_HERANCA_PTS:
            erros.append(f"herança inválida ou sem traçado: {sub} → {sup}")
    if set(MODELO_POS) != classes:
        erros.append("classes sem posição no desenho do modelo")
    dominios = {t for t, _, _ in C2.MODELO_TIPOS}
    for classe, attrs in C2.MODELO_CLASSES.items():
        nomes = [nome_atributo(a) for a in attrs]
        if len(set(nomes)) != len(nomes):
            erros.append(f"{classe}: atributo repetido")
        for a in attrs:
            tipo = tipo_atributo(a)
            if tipo == "Enumeração" and f"{classe}.{nome_atributo(a)}" not in dominios:
                erros.append(f"{classe}.{nome_atributo(a)}: enumeração sem domínio")
            elif tipo not in TIPOS_SIMPLES | {"Enumeração"} and tipo not in dominios:
                erros.append(f"{classe}.{nome_atributo(a)}: tipo {tipo} sem definição")
    for t in dominios:
        if "." in t:
            classe, atr = t.split(".")
            if atr not in [nome_atributo(a) for a in C2.MODELO_CLASSES.get(classe, [])]:
                erros.append(f"domínio de atributo inexistente: {t}")
    if set(MODELO_POS) == classes:
        erros += validar_desenho()
    return erros


def rastreabilidade(m):
    """{RF: [códigos de função]} na ordem dos RF da F1."""
    return {rf["cod"]: [f["cod"] for f in m["fs"]
                        if f["tipo"] in ("EE", "CE", "SE") and rf["cod"] in f["rf"]]
            for rf in C1.RF}


def origem(f):
    telas = ", ".join(f["telas"]) if f["telas"] else "sem tela"
    rf = ", ".join("navegação" if r == "nav" else r for r in f["rf"])
    return f"{telas} · {rf}"


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def svg_para_png(svg, destino, margem=24):
    """Desenha o SVG em PNG (150 dpi) e recorta a margem branca em volta do conteúdo."""
    destino.with_suffix(".svg").write_text(svg, encoding="utf-8")
    png = destino.with_suffix(".png")
    pymupdf.open(str(destino.with_suffix(".svg")))[0].get_pixmap(dpi=150).save(str(png))
    img = Image.open(png).convert("RGB")
    x0, y0, x1, y1 = ImageChops.difference(img, Image.new("RGB", img.size, "white")).getbbox()
    img = img.crop((max(0, x0 - margem), max(0, y0 - margem),
                    min(img.width, x1 + margem), min(img.height, y1 + margem)))
    img.save(png)
    return png, img.width, img.height


def gerar_prototipos():
    PROTO.mkdir(parents=True, exist_ok=True)
    pngs = {nome: svg_para_png(fn(), PROTO / nome) for nome, _, _, fn in P.PRANCHAS}
    print(f"Protótipos: {len(pngs)} pranchas em {PROTO.name}/")
    return pngs


CINZA_TRACO = "#7A7A7A"

# Desenho do modelo revisado em grade 3 x 3. Linha 1: Administrador, Denúncia, Avaliação;
# linha 2: Usuário, Solicitação e a AIE; linha 3: Prestador (abaixo da superclasse), Serviço,
# Categoria.
MODELO_TAM = (1130, 970)
MODELO_CAIXA = dict(BW=270, HEAD=30, LH=19, PAD=10)
MODELO_POS = {
    "Administrador": (30, 30), "Denúncia": (430, 30), "Avaliação": (830, 30),
    "Usuário": (30, 300), "Solicitação": (430, 300),
    "Prestador": (30, 680), "Serviço": (430, 680), "Categoria": (830, 680),
}
MODELO_AIE_POS = (830, 430)
# Traçado de cada associação, do lado "de" ao lado "para": pontos, rótulo e multiplicidades,
# cada um como (x, y, alinhamento). Chave = (de, para, rótulo): há duas associações
# Denúncia–Usuário.
MODELO_LIGACOES = {
    ("Denúncia", "Administrador", "analisada por"): dict(
        pts=[(430, 88), (300, 88)], rot=(365, 80, "middle"),
        m_de=(424, 104, "end"), m_para=(306, 104, "start")),
    ("Denúncia", "Avaliação", "denuncia"): dict(
        pts=[(700, 88), (830, 88)], rot=(765, 80, "middle"),
        m_de=(706, 104, "start"), m_para=(824, 104, "end")),
    ("Denúncia", "Usuário", "registra"): dict(
        pts=[(470, 203), (470, 230), (200, 230), (200, 300)], rot=(335, 224, "middle"),
        m_de=(476, 221, "start"), m_para=(206, 294, "start")),
    ("Denúncia", "Usuário", "denuncia"): dict(
        pts=[(520, 203), (520, 262), (270, 262), (270, 300)], rot=(395, 256, "middle"),
        m_de=(526, 221, "start"), m_para=(276, 294, "start")),
    ("Solicitação", "Usuário", "solicita"): dict(
        pts=[(430, 360), (300, 360)], rot=(365, 352, "middle"),
        m_de=(424, 376, "end"), m_para=(306, 376, "start")),
    ("Avaliação", "Solicitação", "origina"): dict(
        pts=[(900, 184), (900, 350), (700, 350)], rot=(800, 342, "middle"),
        m_de=(906, 202, "start"), m_para=(706, 366, "start")),
    ("Solicitação", "Serviço", "referente a"): dict(
        pts=[(565, 587), (565, 680)], rot=(573, 638, "start"),
        m_de=(573, 604, "start"), m_para=(573, 672, "start")),
    ("Serviço", "Prestador", "oferece"): dict(
        pts=[(430, 740), (300, 740)], rot=(365, 732, "middle"),
        m_de=(424, 756, "end"), m_para=(306, 756, "start")),
    ("Serviço", "Categoria", "classificado em"): dict(
        pts=[(700, 740), (830, 740)], rot=(765, 732, "middle"),
        m_de=(706, 756, "start"), m_para=(824, 756, "end")),
}
# Herança: (subclasse, superclasse) -> (ponto na borda da subclasse, ponta do triângulo na
# borda da superclasse)
MODELO_HERANCA_PTS = {("Prestador", "Usuário"): ((165, 680), (165, 568))}


def caixa_classe(nome):
    """(x, y, largura, altura) da caixa de uma classe no desenho do modelo."""
    x, y = MODELO_POS[nome]
    c = MODELO_CAIXA
    return x, y, c["BW"], c["HEAD"] + c["LH"] * len(C2.MODELO_CLASSES[nome]) + c["PAD"]


def na_borda(ponto, nome):
    px, py = ponto
    x, y, w, h = caixa_classe(nome)
    dentro = x <= px <= x + w and y <= py <= y + h
    return dentro and (px in (x, x + w) or py in (y, y + h))


def validar_desenho():
    """Pontas das linhas sobre as bordas das caixas certas (o desenho acompanha o modelo)."""
    erros = []
    for (de, para, rot), lig in MODELO_LIGACOES.items():
        if not (na_borda(lig["pts"][0], de) and na_borda(lig["pts"][-1], para)):
            erros.append(f"linha {de}–{para} ({rot}) não termina nas bordas das caixas")
    for (sub, sup), (p1, p2) in MODELO_HERANCA_PTS.items():
        if not (na_borda(p1, sub) and na_borda(p2, sup)):
            erros.append(f"herança {sub} → {sup} não termina nas bordas das caixas")
    return erros


def diagrama_modelo():
    W, H = MODELO_TAM
    BW, HEAD, LH, PAD = (MODELO_CAIXA[k] for k in ("BW", "HEAD", "LH", "PAD"))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']

    def rotulo(x, y, t, anchor, size=12):
        w = len(t) * size * 0.55
        bx = {"middle": x - w / 2 - 2, "start": x - 2, "end": x - w - 2}[anchor]
        out.append(f'<rect x="{bx:.0f}" y="{y - size}" width="{w + 4:.0f}" '
                   f'height="{size + 4}" fill="white"/>')
        out.append(G1.svg_texto(x, y, t, size, anchor=anchor, fill="#333"))

    for a in C2.MODELO_ASSOCIACOES:
        lig = MODELO_LIGACOES[(a["de"], a["para"], a["rotulo"])]
        pts = " ".join(f"{x},{y}" for x, y in lig["pts"])
        out.append(f'<polyline points="{pts}" fill="none" stroke="#333" stroke-width="1.3"/>')
        for chave, texto, tam in (("rot", a["rotulo"], 12), ("m_de", a["m_de"], 11),
                                  ("m_para", a["m_para"], 11)):
            x, y, anc = lig[chave]
            rotulo(x, y, texto, anc, tam)
    for (x1, y1), (x2, y2) in MODELO_HERANCA_PTS.values():
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2 + 16}" stroke="#333" '
                   f'stroke-width="1.3"/>')
        out.append(f'<polygon points="{x2},{y2} {x2 - 10},{y2 + 16} {x2 + 10},{y2 + 16}" '
                   f'fill="white" stroke="#333" stroke-width="1.3"/>')

    def caixa(x, y, titulo, linhas, codigo, traco, fundo):
        h = HEAD + LH * len(linhas) + PAD
        out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{h}" fill="white" '
                   f'stroke="{traco}" stroke-width="1.6"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{HEAD}" fill="{fundo}" '
                   f'stroke="{traco}" stroke-width="1.6"/>')
        out.append(G1.svg_texto(x + BW / 2, y + 20, titulo, 14, weight="bold"))
        for i, linha in enumerate(linhas):
            out.append(G1.svg_texto(x + 10, y + HEAD + 16 + i * LH, "+ " + linha, 12,
                                    anchor="start"))
        return h

    for nome, attrs in C2.MODELO_CLASSES.items():
        caixa(*MODELO_POS[nome], nome, attrs, None, G1.AZUL_TRACO, G1.AZUL_FILL)
    aie = C2.AIE[0]
    x, y = MODELO_AIE_POS
    h = caixa(x, y, aie["nome"], aie["td"], None, CINZA_TRACO, "#E4E4E4")
    for i, t in enumerate(("API externa, fora da fronteira do sistema;",
                           "localização de Usuário e Prestador (F7).")):
        out.append(f'<text x="{x}" y="{y + h + 20 + i * 16}" font-family="{G1.FONTE}" '
                   f'font-size="12" font-style="italic" fill="#555">{G1.esc(t)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def gerar_modelo():
    DIAG.mkdir(parents=True, exist_ok=True)
    for antigo in DIAG.glob("modelo_conceitual_apf.*"):
        antigo.unlink()
    png, _, _ = svg_para_png(diagrama_modelo(), DIAG / "modelo_conceitual_revisado")
    print(f"Diagrama: {DIAG.name}/{png.name}")
    return png


# ---------------------------------------------------------------------------
# Textos e linhas de tabela usados no Word e no Markdown
# ---------------------------------------------------------------------------

TXT_PROTO = ("Telas identificadas por código (T01 a T29), usado na coluna Origem das tabelas de "
             "contagem. Setas: navegação; caixas cinza: telas de outra prancha; caixas "
             "arredondadas: mensagens e diálogos do sistema.")
TXT_DADOS = ("Modelo conceitual revisado a partir do modelo preliminar da Concepção (alterações "
             "e tipos nas tabelas após a figura). Cada classe é um ALI; a API de geocodificação "
             "é a AIE.")


def origem_dados(f):
    if f["tipo"] == "AIE":
        return f["origem"]
    txt = f["origem"]
    subs = [sub for sub, sup in C2.MODELO_HERANCA if sup == f["nome"]]
    sups = [sup for sub, sup in C2.MODELO_HERANCA if sub == f["nome"]]
    if subs:
        txt += "; superclasse de " + ", ".join(subs)
    if sups:
        txt += "; subclasse de " + ", ".join(sups)
    return txt


def calc_pfa(m):
    """(etapa, fórmula, cálculo, destaque) do PFA."""
    k = fmt(1 + C2.MARGEM)
    return [
        ("PFB", "soma dos PF das funções", str(m["pfb"]), False),
        (f"PFB com margem de {int(C2.MARGEM * 100)}%", f"PFB × {k}",
         f"{m['pfb']} × {k} = {fmt(m['pfb'] * (1 + C2.MARGEM), 1)} → {m['pfb_m']}", False),
        ("FA", "0,65 + 0,01 × NI", f"0,65 + 0,01 × {m['ni']} = {fmt(m['fa'])}", False),
        ("PFA", "PFB com margem × FA", f"{m['pfb_m']} × {fmt(m['fa'])} = {m['pfa']} PF", True),
    ]


def parametros(m):
    """(parâmetro, valor, critério) da estimativa."""
    a = adotado(m)
    fixos, mensais, _ = extras(a["prazo"])
    def lista(itens):
        return "; ".join(f"{d[0].lower()}{d[1:]}, {rs(v)}" for d, v in itens)

    criterio_extras = f"Fixos: {lista(C2.EXTRAS_FIXOS)}. Mensais: {lista(C2.EXTRAS_MENSAIS)}."
    return [
        ("Tamanho", f"{m['pfa']} PF", "PFA medido na seção anterior."),
        ("Produtividade", f"{fmt(a['hpf'])} h/PF", C2.CRITERIO_PRODUTIVIDADE),
        ("Horas por pessoa/mês", f"{C2.HORAS_MES} h", "Referência da aula: 6,5 h/dia × 20 dias "
                                                      "úteis."),
        ("Equipe", f"{C2.EQUIPE} pessoas", "Integrantes do grupo."),
        ("Valor da hora", rs(C2.VALOR_HORA), "Referência da aula."),
        ("Gastos extras", f"{rs(fixos)} + {rs(mensais)}/mês", criterio_extras),
        ("Lucro", f"{int(C2.LUCRO * 100)}%", "Percentual dos exemplos da aula."),
    ]


def calc_projecao(m):
    """(etapa, fórmula, cálculo, destaque) da projeção adotada."""
    a = adotado(m)
    fixos, mensais, ext = extras(a["prazo"])
    luc = fmt(1 + C2.LUCRO)
    return [
        ("Esforço", "PFA × produtividade",
         f"{m['pfa']} × {fmt(a['hpf'])} = {fmt(a['exato'])} → {fmt(a['esforco'], 0)} h", False),
        ("H/M", f"esforço ÷ {C2.HORAS_MES}",
         f"{fmt(a['esforco'], 0)} ÷ {C2.HORAS_MES} = {fmt(a['hm'])}", False),
        ("Prazo", "H/M ÷ equipe", f"{fmt(a['hm'])} ÷ {C2.EQUIPE} = {fmt(a['prazo'])} meses",
         False),
        ("Custo da equipe", f"equipe × {C2.HORAS_MES} × valor da hora × prazo",
         f"{C2.EQUIPE} × {C2.HORAS_MES} × {rs(C2.VALOR_HORA)} × {fmt(a['prazo'])} = "
         f"{rs(a['custo_equipe'])}", False),
        ("Gastos extras", "fixos + mensais × prazo",
         f"{rs(fixos)} + {rs(mensais)} × {fmt(a['prazo'])} = {rs(ext)}", False),
        ("Preço", f"(custo + extras) × {luc}",
         f"({rs(a['custo_equipe'])} + {rs(ext)}) × {luc} = {rs(a['preco'])}", True),
    ]


def txt_comparacao(m):
    a = adotado(m)
    return (f"Planejamento preliminar (Concepção): {fmt(C2.PLANEJAMENTO_F1_HORAS, 0)} h. "
            f"Estimativa por APF (cenário realista): {fmt(a['esforco'], 0)} h, cerca de "
            f"{fmt(a['esforco'] / C2.PLANEJAMENTO_F1_HORAS, 1)} vezes o planejado.")


# ---------------------------------------------------------------------------
# Markdown (revisão)
# ---------------------------------------------------------------------------

def _md_calculo(linhas):
    L = ["| Etapa | Fórmula | Cálculo |", "|---|---|---|"]
    for etapa, formula, calc, destaque in linhas:
        L.append(f"| {etapa} | {formula} | {'**' + calc + '**' if destaque else calc} |")
    return L


def md_prototipos():
    L = ["# Protótipos das telas", "", TXT_PROTO, ""]
    for i, (nome, titulo, telas, _) in enumerate(P.PRANCHAS, 1):
        L += [f"## Prancha {i} — {titulo}", "", f"![{titulo}](prototipos/{nome}.png)", "",
              "Telas: " + "; ".join(f"**{t}** {P.TELAS[t]}" for t in telas), ""]
    return "\n".join(L)


def _md_tabela_transacoes(m, tipo):
    L = ["| Função | Origem (tela · RF) | AR | TD | Complexidade | PF |",
         "|---|---|---|---|:-:|:-:|"]
    for f in m["por_tipo"][tipo]:
        nome = f["nome"] + (" *(oculta)*" if f.get("oculta") else "")
        ar = f"{f['n_ar']}" + (f": {', '.join(f['ar'])}" if f["ar"] else "")
        L.append(f"| **{f['cod']}** {nome} | {origem(f)} | {ar} | {f['n_td']}: "
                 f"{'; '.join(f['td'])} | {f['compl']} | {f['pf']} |")
    L.append(f"| **Total {tipo}** ({len(m['por_tipo'][tipo])} funções) | | | | | "
             f"**{m['subtotal'][tipo]}** |")
    return L


def md_contagem(m):
    L = ["# Análise de Pontos de Função — contagem", "",
         f"**Resultado:** PFB = {m['pfb']}; com margem de 30% = {m['pfb_m']}; NI = {m['ni']}; "
         f"FA = {fmt(m['fa'])}; **PFA = {m['pfa']} pontos de função**.", "",
         "## Critérios de contagem", ""]
    L += [f"{i}. {c}" for i, c in enumerate(C2.CRITERIOS, 1)]
    L += ["", "## Funções de dados (ALI e AIE)", "", TXT_DADOS, "",
          "![Modelo conceitual revisado](diagramas/modelo_conceitual_revisado.png)", "",
          "| Alteração em relação ao modelo preliminar | Requisitos |", "|---|---|"]
    L += [f"| {alt} | {req} |" for alt, req in C2.MODELO_ALTERACOES]
    L += ["", "| Tipo composto ou enumeração | Valores | Requisitos |", "|---|---|---|"]
    L += [f"| {t} | {v} | {req} |" for t, v, req in C2.MODELO_TIPOS]
    L += ["", "| Função | Tipo | Origem | TR | TD | Complexidade | PF |",
          "|---|:-:|---|:-:|---|:-:|:-:|"]
    for f in m["por_tipo"]["ALI"] + m["por_tipo"]["AIE"]:
        L.append(f"| **{f['cod']}** {f['nome']} | {f['tipo']} | {origem_dados(f)} | {f['tr']} | "
                 f"{f['n_td']}: {', '.join(f['td'])} | {f['compl']} | {f['pf']} |")
    L.append(f"| **Total** | | | | | | **{m['subtotal']['ALI'] + m['subtotal']['AIE']}** |")
    for tipo in ("EE", "CE", "SE"):
        L += ["", f"## {NOMES_TIPO[tipo]} ({tipo})", ""] + _md_tabela_transacoes(m, tipo)
    L += ["", "## Pontos de função brutos", "",
          "| Função | Ocorrências | Complexidade | Peso | Resultado |", "|---|:-:|---|:-:|:-:|"]
    for tipo in ("EE", "SE", "ALI", "AIE", "CE"):
        for c in ("Simples", "Médio", "Complexo"):
            n = m["resumo"][tipo][c]
            L.append(f"| {NOMES_TIPO[tipo]} | {n} | {c} | × {PESOS[tipo][c]} | "
                     f"{n * PESOS[tipo][c]} |")
        L.append(f"| **Total {tipo}** | | | | **{m['subtotal'][tipo]}** |")
    L += [f"| **PFB** | | | | **{m['pfb']}** |", "",
          "## Fator de ajuste", "",
          "| Nº | Característica | NI | Justificativa |", "|:-:|---|:-:|---|"]
    for i, (nome, ni, just) in enumerate(C2.CGS, 1):
        L.append(f"| {i} | {nome} | {ni} | {just} |")
    L += [f"| | **NI total** | **{m['ni']}** | FA = 0,65 + 0,01 × {m['ni']} = {fmt(m['fa'])} |",
          "", "## Pontos de função ajustados", ""]
    L += _md_calculo(calc_pfa(m))
    L += ["", "---", "", "## Apoio à revisão — rastreabilidade RF → funções", "",
          "*(Não está no documento; serve só para conferência do grupo.)*", "",
          "| RF | Funções APF |", "|---|---|"]
    rast = rastreabilidade(m)
    for rf in C1.RF:
        L.append(f"| {rf['cod']} {rf['nome']} | {', '.join(rast[rf['cod']])} |")
    return "\n".join(L) + "\n"


def md_estimativas(m):
    a = adotado(m)
    L = ["# Estimativas de esforço, prazo e custo", "",
         f"**Projeção adotada (cenário realista):** {fmt(a['esforco'], 0)} h, "
         f"{fmt(a['prazo'])} meses com {C2.EQUIPE} pessoas, {rs(a['preco'])}.", "",
         "## Parâmetros", "", "| Parâmetro | Valor | Critério |", "|---|---|---|"]
    L += [f"| {p} | {v} | {c} |" for p, v, c in parametros(m)]
    L += ["", "## Cenários", "",
          "| Cenário | h/PF | Esforço (h) | H/M | Prazo (meses) | Preço |",
          "|---|:-:|:-:|:-:|:-:|:-:|"]
    for c in C2.CENARIOS:
        e = estimativa(m["pfa"], c["hpf"])
        nome = f"**{c['nome']} (adotado)**" if c["adotado"] else c["nome"]
        L.append(f"| {nome} | {fmt(c['hpf'])} | {fmt(e['esforco'], 0)} | {fmt(e['hm'])} | "
                 f"{fmt(e['prazo'])} | {rs(e['preco'])} |")
    L += ["", "## Projeção adotada (cenário realista)", ""] + _md_calculo(calc_projecao(m))
    L += ["", "Prazo por tamanho de equipe:", "", "| Equipe | Prazo (meses) |", "|:-:|:-:|"]
    L += [f"| {n} pessoas | {fmt(r2(a['hm'] / n))} |" for n in C2.EQUIPES_ALTERNATIVAS]
    L += ["", "## Comparação com o planejamento preliminar", "", txt_comparacao(m)]
    return "\n".join(L) + "\n"


def gerar_md(m):
    arquivos = {
        "1 - Protótipos.md": md_prototipos(),
        "2 - Contagem de Pontos de Função.md": md_contagem(m),
        "3 - Estimativas.md": md_estimativas(m),
    }
    for nome, txt in arquivos.items():
        (RAIZ / nome).write_text(txt, encoding="utf-8")
    print("Markdown:", ", ".join(arquivos))


# ---------------------------------------------------------------------------
# Documento Word (F1 + F2)
# ---------------------------------------------------------------------------

TAM = 8.5   # fonte das tabelas de contagem


def cabecalho(t, nomes, tamanho=9):
    row = G1.nova_linha(t)
    for c, txt in zip(row.cells, nomes):
        G1.escrever(c, [(txt, True)], WD_ALIGN_PARAGRAPH.CENTER, size=tamanho)
        G1.sombrear(c, G1.CINZA)
    G1.repetir_cabecalho(row)
    return row


def sombrear_linha(row, cor):
    """Sombreia cada célula física uma vez (células mescladas se repetem em row.cells)."""
    vistos = []
    for c in row.cells:
        if any(e is c._tc for e in vistos):
            continue
        vistos.append(c._tc)
        G1.sombrear(c, cor)


def linha_total(t, rotulo, valor, ncols):
    row = G1.nova_linha(t)
    G1.escrever(G1.mesclar(row, 0, ncols - 2), [(rotulo, True)], WD_ALIGN_PARAGRAPH.RIGHT,
                size=9)
    G1.escrever(row.cells[ncols - 1], [(str(valor), True)], WD_ALIGN_PARAGRAPH.CENTER, size=9)


def tabela_calculo(doc, linhas):
    t = G1.nova_tabela(doc, [3.2, 5.0, 8.8])
    cabecalho(t, ["Etapa", "Fórmula", "Cálculo"])
    for etapa, formula, calc, destaque in linhas:
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], [(etapa, True)], size=9)
        G1.escrever(row.cells[1], formula, size=9)
        G1.escrever(row.cells[2], [(calc, destaque)], size=9)
        if destaque:
            sombrear_linha(row, "E8F4F6")
    G1.manter_junto(t)


def secao_prototipos(doc, pngs):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    G1.margens(sec, paisagem=True)
    G1.h1(doc, "Protótipos das telas")
    G1.paragrafo(doc, TXT_PROTO, size=10)
    t = G1.nova_tabela(doc, [3.0, 7.2, 15.5])
    cabecalho(t, ["Prancha", "Assunto", "Telas"])
    for i, (nome, titulo, telas, _) in enumerate(P.PRANCHAS, 1):
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], f"Prancha {i}", WD_ALIGN_PARAGRAPH.CENTER, size=9)
        G1.escrever(row.cells[1], titulo, size=9)
        G1.escrever(row.cells[2], "; ".join(f"{c} {P.TELAS[c]}" for c in telas), size=9)
    for i, (nome, titulo, telas, _) in enumerate(P.PRANCHAS, 1):
        G1.quebra_pagina(doc)
        faixa = telas[0] if len(telas) == 1 else f"{telas[0]} a {telas[-1]}"
        G1.h2(doc, f"Prancha {i} — {titulo} ({faixa})")
        png, w, h = pngs[nome]
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(png), width=Cm(min(25.5, 14.6 * w / h)))


def tabela_lista(doc, larguras, nomes, linhas):
    t = G1.nova_tabela(doc, larguras)
    cabecalho(t, nomes)
    for linha in linhas:
        row = G1.nova_linha(t)
        for c, v in zip(row.cells, linha):
            G1.escrever(c, v, size=9)
    G1.manter_junto(t, ate=1)


def tabela_dados(doc, m):
    t = G1.nova_tabela(doc, [2.8, 2.9, 0.8, 7.7, 1.7, 1.1])
    cabecalho(t, ["Função", "Origem", "TR", "TD (quantidade: lista)", "Complex.", "PF"])
    for f in m["por_tipo"]["ALI"] + m["por_tipo"]["AIE"]:
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], [(f["cod"], True), (" " + f["nome"], False)], size=TAM)
        G1.escrever(row.cells[1], origem_dados(f), size=TAM)
        G1.escrever(row.cells[2], str(f["tr"]), WD_ALIGN_PARAGRAPH.CENTER, size=TAM)
        G1.escrever(row.cells[3], [(f"{f['n_td']}: ", True), (", ".join(f["td"]), False)],
                    size=TAM)
        G1.escrever(row.cells[4], f["compl"], WD_ALIGN_PARAGRAPH.CENTER, size=TAM)
        G1.escrever(row.cells[5], str(f["pf"]), WD_ALIGN_PARAGRAPH.CENTER, size=TAM)
    linha_total(t, f"Total das funções de dados ({len(C2.ALI)} ALI + {len(C2.AIE)} AIE)",
                m["subtotal"]["ALI"] + m["subtotal"]["AIE"], 6)
    G1.manter_junto(t, ate=1)


def tabela_transacoes(doc, m, tipo):
    t = G1.nova_tabela(doc, [3.3, 2.2, 2.9, 5.7, 1.8, 1.1])
    cabecalho(t, ["Função", "Origem (tela · RF)", "AR", "TD (quantidade: lista)",
                  "Complex.", "PF"])
    for f in m["por_tipo"][tipo]:
        row = G1.nova_linha(t)
        partes = [(f["cod"], True), (" " + f["nome"], False)]
        if f.get("oculta"):
            partes.append((" (oculta)", False))
        G1.escrever(row.cells[0], partes, size=TAM)
        G1.escrever(row.cells[1], origem(f), size=TAM)
        ar = [(f"{f['n_ar']}", True)] + ([(": " + ", ".join(f["ar"]), False)] if f["ar"] else [])
        G1.escrever(row.cells[2], ar, size=TAM)
        G1.escrever(row.cells[3], [(f"{f['n_td']}: ", True), ("; ".join(f["td"]), False)],
                    size=TAM)
        G1.escrever(row.cells[4], f["compl"], WD_ALIGN_PARAGRAPH.CENTER, size=TAM)
        G1.escrever(row.cells[5], str(f["pf"]), WD_ALIGN_PARAGRAPH.CENTER, size=TAM)
    linha_total(t, f"Total {tipo} ({len(m['por_tipo'][tipo])} funções)", m["subtotal"][tipo], 6)
    G1.manter_junto(t, ate=1)


def tabela_pfb(doc, m):
    t = G1.nova_tabela(doc, [4.6, 3.0, 3.0, 2.4, 4.0])
    cabecalho(t, ["Função", "Nº de ocorrências", "Complexidade", "Peso", "Resultado"])
    for tipo in ("EE", "SE", "ALI", "AIE", "CE"):
        linhas = []
        for c in ("Simples", "Médio", "Complexo"):
            n = m["resumo"][tipo][c]
            row = G1.nova_linha(t)
            linhas.append(row)
            G1.escrever(row.cells[1], str(n), WD_ALIGN_PARAGRAPH.CENTER, size=9)
            G1.escrever(row.cells[2], c, WD_ALIGN_PARAGRAPH.CENTER, size=9)
            G1.escrever(row.cells[3], f"× {PESOS[tipo][c]}", WD_ALIGN_PARAGRAPH.CENTER, size=9)
            G1.escrever(row.cells[4], str(n * PESOS[tipo][c]), WD_ALIGN_PARAGRAPH.CENTER,
                        size=9)
        cel = linhas[0].cells[0].merge(linhas[-1].cells[0])
        G1.escrever(cel, [(NOMES_TIPO[tipo], True), (f" ({tipo})", False)], size=9)
        row = G1.nova_linha(t)
        G1.escrever(G1.mesclar(row, 0, 3), [(f"Total {tipo}", True)], WD_ALIGN_PARAGRAPH.RIGHT,
                    size=9)
        G1.escrever(row.cells[4], [(str(m["subtotal"][tipo]), True)],
                    WD_ALIGN_PARAGRAPH.CENTER, size=9)
        sombrear_linha(row, "F2F2F2")
    row = G1.nova_linha(t)
    G1.escrever(G1.mesclar(row, 0, 3), [("Pontos de Função Brutos (PFB)", True)],
                WD_ALIGN_PARAGRAPH.RIGHT, size=10)
    G1.escrever(row.cells[4], [(str(m["pfb"]), True)], WD_ALIGN_PARAGRAPH.CENTER, size=10)
    sombrear_linha(row, G1.CINZA)
    G1.manter_junto(t)


def tabela_cgs(doc, m):
    t = G1.nova_tabela(doc, [0.9, 3.9, 1.0, 11.2])
    cabecalho(t, ["Nº", "Característica", "NI", "Justificativa"])
    for i, (nome, ni, just) in enumerate(C2.CGS, 1):
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], str(i), WD_ALIGN_PARAGRAPH.CENTER, size=9)
        G1.escrever(row.cells[1], nome, size=9)
        G1.escrever(row.cells[2], [(str(ni), True)], WD_ALIGN_PARAGRAPH.CENTER, size=9)
        G1.escrever(row.cells[3], just, size=9)
    row = G1.nova_linha(t)
    G1.escrever(G1.mesclar(row, 0, 1), [("Nível de influência total (NI)", True)],
                WD_ALIGN_PARAGRAPH.RIGHT, size=9)
    G1.escrever(row.cells[2], [(str(m["ni"]), True)], WD_ALIGN_PARAGRAPH.CENTER, size=9)
    G1.escrever(row.cells[3], f"FA = 0,65 + 0,01 × {m['ni']} = {fmt(m['fa'])}", size=9)
    sombrear_linha(row, "F2F2F2")
    G1.manter_junto(t, ate=1)


def secao_apf(doc, m, png_modelo):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    G1.margens(sec)
    G1.h1(doc, "Análise de Pontos de Função")
    G1.h2(doc, "Critérios de contagem")
    for i, c in enumerate(C2.CRITERIOS, 1):
        p = G1.paragrafo(doc, c, f"{i}.\t", size=10, after=3, align=WD_ALIGN_PARAGRAPH.LEFT)
        pf = p.paragraph_format
        pf.left_indent, pf.first_line_indent = Cm(0.7), Cm(-0.7)
        pf.tab_stops.add_tab_stop(Cm(0.7))

    G1.h2(doc, "Funções de dados (ALI e AIE)")
    p = G1.paragrafo(doc, TXT_DADOS, size=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(str(png_modelo), width=Cm(16.5))
    tabela_lista(doc, [12.0, 5.0], ["Alteração em relação ao modelo preliminar", "Requisitos"],
                 C2.MODELO_ALTERACOES)
    G1.espaco(doc, 10)
    tabela_lista(doc, [4.2, 8.6, 4.2], ["Tipo composto ou enumeração", "Valores", "Requisitos"],
                 C2.MODELO_TIPOS)
    G1.espaco(doc, 10)
    tabela_dados(doc, m)

    # quebra de página no próprio título: um parágrafo de quebra logo após uma tabela que termina
    # no pé da página deixaria uma página em branco
    for tipo in ("EE", "CE", "SE"):
        G1.h2(doc, f"{NOMES_TIPO[tipo]} ({tipo})").paragraph_format.page_break_before = True
        tabela_transacoes(doc, m, tipo)
    G1.h2(doc, "Pontos de função brutos").paragraph_format.page_break_before = True
    tabela_pfb(doc, m)
    G1.espaco(doc, 10)
    G1.h2(doc, "Fator de ajuste")
    tabela_cgs(doc, m)
    G1.espaco(doc, 10)
    G1.h2(doc, "Pontos de função ajustados")
    tabela_calculo(doc, calc_pfa(m))


def secao_estimativas(doc, m):
    a = adotado(m)
    G1.h1(doc, "Estimativas de esforço, prazo e custo").paragraph_format.page_break_before = True
    G1.h2(doc, "Parâmetros")
    t = G1.nova_tabela(doc, [3.4, 4.2, 9.4])
    cabecalho(t, ["Parâmetro", "Valor", "Critério"])
    for par, val, crit in parametros(m):
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], [(par, True)], size=9)
        G1.escrever(row.cells[1], val, size=9)
        G1.escrever(row.cells[2], crit, size=9)
    G1.manter_junto(t)
    G1.espaco(doc, 10)

    G1.h2(doc, "Cenários")
    t = G1.nova_tabela(doc, [4.4, 1.8, 2.3, 1.9, 2.4, 4.2])
    cabecalho(t, ["Cenário", "h/PF", "Esforço (h)", "H/M", "Prazo (meses)", "Preço"])
    for c in C2.CENARIOS:
        e = estimativa(m["pfa"], c["hpf"])
        row = G1.nova_linha(t)
        G1.escrever(row.cells[0], [(c["nome"] + (" (adotado)" if c["adotado"] else ""),
                                    c["adotado"])], size=9)
        for k, v in enumerate([fmt(c["hpf"]), fmt(e["esforco"], 0), fmt(e["hm"]),
                               fmt(e["prazo"]), rs(e["preco"])], 1):
            G1.escrever(row.cells[k], [(v, c["adotado"])], WD_ALIGN_PARAGRAPH.CENTER, size=9)
        if c["adotado"]:
            sombrear_linha(row, "E8F4F6")
    G1.manter_junto(t)
    G1.espaco(doc, 10)

    G1.h2(doc, "Projeção adotada (cenário realista)")
    tabela_calculo(doc, calc_projecao(m))
    G1.espaco(doc, 8)
    p = G1.paragrafo(doc, "Prazo por tamanho de equipe:", size=10, after=4,
                     align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    t = G1.nova_tabela(doc, [4.0, 4.0])
    cabecalho(t, ["Equipe", "Prazo (meses)"])
    for n in C2.EQUIPES_ALTERNATIVAS:
        row = G1.nova_linha(t)
        d = n == C2.EQUIPE
        G1.escrever(row.cells[0], [(f"{n} pessoas", d)], WD_ALIGN_PARAGRAPH.CENTER, size=9)
        G1.escrever(row.cells[1], [(fmt(r2(a["hm"] / n)), d)], WD_ALIGN_PARAGRAPH.CENTER,
                    size=9)
    G1.manter_junto(t)
    G1.espaco(doc, 10)

    G1.h2(doc, "Comparação com o planejamento preliminar")
    G1.paragrafo(doc, txt_comparacao(m), size=10, align=WD_ALIGN_PARAGRAPH.LEFT)


def gerar_docx(m, pngs, png_modelo):
    doc = Document()
    G1.modo_atual(doc)
    for z in doc.settings.element.iter(G1.qn("w:zoom")):
        z.set(G1.qn("w:percent"), "100")   # atributo obrigatório ausente no modelo padrão
    G1.configurar_estilos(doc)
    G1.margens(doc.sections[0])
    G1.rodape(doc)
    G1.capa(doc, fases=("Fase 1 – Concepção", "Fase 2 – Análise de Pontos de Função"))
    G1.secao_concepcao(doc)
    G1.secao_organizacao(doc, {"diagrama_casos_de_uso": F1_DIAG / "diagrama_casos_de_uso.png",
                               "modelo_conceitual": F1_DIAG / "modelo_conceitual.png"})
    G1.secao_planejamento(doc)
    secao_prototipos(doc, pngs)
    secao_apf(doc, m, png_modelo)
    secao_estimativas(doc, m)
    doc.core_properties.title = f"{C1.SISTEMA} – Análise de Pontos de Função (F2)"
    doc.core_properties.author = ", ".join(n for n, _ in C1.EQUIPE)
    doc.save(str(DOCX))
    print("Word:", DOCX.name)


if __name__ == "__main__":
    G1.validar()                     # a F1 continua consistente
    m = medicao()
    validar(m)
    gerar_prototipos()
    gerar_modelo()
    a = adotado(m)
    print(f"PFB = {m['pfb']} | com margem = {m['pfb_m']} | NI = {m['ni']} | FA = {fmt(m['fa'])} | "
          f"PFA = {m['pfa']}")
    print(f"Realista: {fmt(a['esforco'], 0)} h | H/M {fmt(a['hm'])} | "
          f"prazo {fmt(a['prazo'])} meses | preço {rs(a['preco'])}")
