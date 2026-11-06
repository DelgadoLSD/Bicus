# -*- coding: utf-8 -*-
"""Diagrama de atividades UML do processo customizado do Bicus (F3) e figura do quadro Kanban."""

FONTE = "Arial"
AZUL_FILL, AZUL_TRACO = "#E3F1FA", "#2F6A8F"
NOTA_FILL, NOTA_TRACO = "#FFF4C2", "#B59B2A"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.p = w, h, []

    def add(self, s):
        self.p.append(s)

    def texto(self, x, y, t, size=13, anchor="middle", bold=False, italic=False, cor="#1A1A1A"):
        self.add(f'<text x="{x}" y="{y}" font-family="{FONTE}" font-size="{size}" '
                 f'font-weight="{"bold" if bold else "normal"}" '
                 f'font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}" '
                 f'fill="{cor}">{esc(t)}</text>')

    def linhas(self, cx, cy, linhas, size=13, **kw):
        alt = size + 4
        y0 = cy - alt * (len(linhas) - 1) / 2 + size * 0.35
        for i, t in enumerate(linhas):
            self.texto(cx, y0 + i * alt, t, size, **kw)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n<defs>'
                '<marker id="seta" markerWidth="10" markerHeight="10" refX="9" refY="5" '
                'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker>'
                '</defs>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="white"/>\n'
                + "\n".join(self.p) + "\n</svg>")


# --- elementos UML -----------------------------------------------------------------------

def acao(d, x, y, w, h, linhas, size=13):
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{AZUL_FILL}" '
          f'stroke="{AZUL_TRACO}" stroke-width="1.6"/>')
    d.linhas(x + w / 2, y + h / 2, linhas, size)


def artefato(d, x, y, w, h, linhas, size=12):
    c = 12
    d.add(f'<path d="M{x},{y} L{x + w - c},{y} L{x + w},{y + c} L{x + w},{y + h} L{x},{y + h} Z" '
          f'fill="white" stroke="#444" stroke-width="1.3"/>')
    d.add(f'<path d="M{x + w - c},{y} L{x + w - c},{y + c} L{x + w},{y + c}" fill="none" '
          f'stroke="#444" stroke-width="1.1"/>')
    d.linhas(x + w / 2 - 4, y + h / 2, linhas, size, bold=True)


def nota(d, x, y, w, h, linhas, size=11.5, negrito=2):
    c = 12
    d.add(f'<path d="M{x},{y} L{x + w - c},{y} L{x + w},{y + c} L{x + w},{y + h} L{x},{y + h} Z" '
          f'fill="{NOTA_FILL}" stroke="{NOTA_TRACO}" stroke-width="1.3"/>')
    d.add(f'<path d="M{x + w - c},{y} L{x + w - c},{y + c} L{x + w},{y + c}" fill="none" '
          f'stroke="{NOTA_TRACO}" stroke-width="1.1"/>')
    alt = size + 4
    y0 = y + 8 + size
    for i, t in enumerate(linhas):
        d.texto(x + 8, y0 + i * alt, t, size, anchor="start", bold=(i < negrito))


def objeto(d, x, y, w, h, nome, sub=None):
    """Nó de objeto UML (retângulo simples)."""
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#444" '
          f'stroke-width="1.4"/>')
    if sub:
        d.texto(x + w / 2, y + h / 2 - 3, nome, 13, bold=True)
        d.texto(x + w / 2, y + h / 2 + 14, sub, 11.5, italic=True, cor="#444")
    else:
        d.texto(x + w / 2, y + h / 2 + 5, nome, 13, bold=True)


def inicio(d, x, y):
    d.add(f'<circle cx="{x}" cy="{y}" r="11" fill="#111"/>')


def fim(d, x, y):
    d.add(f'<circle cx="{x}" cy="{y}" r="13" fill="white" stroke="#111" stroke-width="2"/>')
    d.add(f'<circle cx="{x}" cy="{y}" r="8" fill="#111"/>')


def decisao(d, x, y, rot=None, r=18):
    d.add(f'<polygon points="{x},{y - r} {x + r},{y} {x},{y + r} {x - r},{y}" fill="white" '
          f'stroke="#222" stroke-width="1.4"/>')
    if rot:
        d.texto(x + r + 6, y - r + 2, rot, 12, anchor="start", italic=True, cor="#333")


def barra(d, x1, x2, y):
    d.add(f'<rect x="{x1}" y="{y - 4}" width="{x2 - x1}" height="8" fill="#111"/>')


def ponta(d, p1, p2, cheia=True, cor="#222"):
    """Ponta de seta em p2 (o renderizador não suporta marker do SVG)."""
    import math
    (x1, y1), (x2, y2) = p1, p2
    a = math.atan2(y2 - y1, x2 - x1)
    t = 10
    q1 = (x2 - t * math.cos(a - 0.4), y2 - t * math.sin(a - 0.4))
    q2 = (x2 - t * math.cos(a + 0.4), y2 - t * math.sin(a + 0.4))
    if cheia:
        d.add(f'<polygon points="{x2},{y2} {q1[0]:.1f},{q1[1]:.1f} {q2[0]:.1f},{q2[1]:.1f}" '
              f'fill="{cor}"/>')
    else:
        d.add(f'<polyline points="{q1[0]:.1f},{q1[1]:.1f} {x2},{y2} {q2[0]:.1f},{q2[1]:.1f}" '
              f'fill="none" stroke="{cor}" stroke-width="1.3"/>')


def fluxo(d, pts, rot=None, rot_pos=None, anchor="start"):
    s = " ".join(f"{x},{y}" for x, y in pts)
    d.add(f'<polyline points="{s}" fill="none" stroke="#222" stroke-width="1.4"/>')
    ponta(d, pts[-2], pts[-1])
    if rot:
        x, y = rot_pos
        d.texto(x, y, rot, 12, anchor=anchor, italic=True, cor="#333")


def dependencia(d, pts):
    s = " ".join(f"{x},{y}" for x, y in pts)
    d.add(f'<polyline points="{s}" fill="none" stroke="#555" stroke-width="1.2" '
          f'stroke-dasharray="5,4"/>')
    ponta(d, pts[-2], pts[-1], cheia=False, cor="#555")


def ligacao_nota(d, pts):
    s = " ".join(f"{x},{y}" for x, y in pts)
    d.add(f'<polyline points="{s}" fill="none" stroke="{NOTA_TRACO}" stroke-width="1.2" '
          f'stroke-dasharray="3,3"/>')


def moldura(d, x, y, w, h, rotulo):
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#666" '
          f'stroke-width="1.5" stroke-dasharray="8,5"/>')
    tw = len(rotulo) * 7.6 + 20
    d.add(f'<path d="M{x},{y + 26} L{x},{y + 10} Q{x},{y} {x + 10},{y} L{x + tw},{y} '
          f'L{x + tw},{y + 16} L{x + tw - 10},{y + 26} Z" fill="#F2F2F2" stroke="#666" '
          f'stroke-width="1.2"/>')
    d.texto(x + 10, y + 18, rotulo, 13.5, anchor="start", bold=True, cor="#333")


# --- diagrama do processo ----------------------------------------------------------------

def diagrama_processo():
    d = Svg(1800, 1715)

    # Linha 1: Concepção e Elaboração (RUP)
    moldura(d, 20, 30, 810, 260, "Concepção (RUP)")
    moldura(d, 850, 30, 920, 260, "Elaboração (RUP + Kanban)")
    inicio(d, 52, 203)
    fluxo(d, [(63, 203), (88, 203)])
    acoes1 = [
        (90, ["Levantar requisitos", "funcionais e", "não funcionais"], ["Documento de", "Requisitos"]),
        (340, ["Especificar casos", "de uso"], ["Casos de Uso"]),
        (590, ["Elaborar modelo", "conceitual", "preliminar"], ["Modelo Conceitual", "Preliminar"]),
        (920, ["Prototipar telas"], ["Protótipos de Tela"]),
        (1230, ["Escrever histórias de", "usuário a partir dos RF", "e ordenar o backlog"],
         ["Backlog de Histórias", "(quadro Kanban)"]),
    ]
    for i, (x, lin, art) in enumerate(acoes1):
        acao(d, x, 165, 210, 76, lin)
        artefato(d, x + 15, 68, 180, 54, art)
        dependencia(d, [(x + 105, 165), (x + 105, 124)])
        if i + 1 < len(acoes1):
            fluxo(d, [(x + 210, 203), (acoes1[i + 1][0] - 2, 203)])
    nota(d, 1452, 150, 160, 112, ["Nessa ação, a", "GRE3 é atendida:", "cada história", "registra o RF de", "origem (F1 a F20)."])
    ligacao_nota(d, [(1452, 203), (1440, 203)])

    # Construção (Kanban + XP)
    moldura(d, 20, 320, 1750, 1190, "Construção (Kanban + XP)")
    fluxo(d, [(1335, 241), (1335, 346)])
    barra(d, 680, 1620, 350)

    # Faixas do quadro Kanban
    faixas = [("Backlog", 380, 500), ("Fazendo", 500, 1050), ("Testes", 1050, 1220),
              ("Pronto", 1220, 1460)]
    d.add('<rect x="40" y="380" width="1165" height="1080" fill="none" stroke="#999" '
          'stroke-width="1"/>')
    d.add('<rect x="40" y="380" width="44" height="1080" fill="#F4F4F4" stroke="#999" '
          'stroke-width="1"/>')
    for nome, y1, y2 in faixas:
        if y1 > 380:
            d.add(f'<line x1="40" y1="{y1}" x2="1205" y2="{y1}" stroke="#999" '
                  f'stroke-width="1" stroke-dasharray="6,4"/>')
        cy = (y1 + y2) / 2
        d.add(f'<text x="67" y="{cy}" font-family="{FONTE}" font-size="14" font-weight="bold" '
              f'text-anchor="middle" fill="#2F6A8F" transform="rotate(-90 67 {cy})">'
              f'{esc(nome)}</text>')
    d.texto(90, 372, "Colunas do quadro Kanban (limite: 1 cartão por pessoa em Fazendo e Testes)",
            12, anchor="start", italic=True, cor="#555")

    fluxo(d, [(700, 354), (700, 408)])
    acao(d, 550, 410, 300, 60, ["Puxar a próxima história", "do backlog"])
    fluxo(d, [(700, 470), (700, 505)])
    decisao(d, 700, 525)                  # junção: retrabalho e retomada após impedimento
    fluxo(d, [(700, 543), (700, 570)])
    decisao(d, 700, 590, "história complexa?")
    fluxo(d, [(682, 590), (430, 590), (430, 638)], "[não]", (560, 582), "middle")
    fluxo(d, [(718, 590), (960, 590), (960, 638)], "[sim]", (850, 582), "middle")
    acao(d, 290, 640, 280, 76, ["Implementar individualmente", "e pedir revisão a outro", "integrante"])
    acao(d, 840, 640, 240, 64, ["Implementar em par", "(revisão contínua)"])
    nota(d, 590, 640, 230, 82, ["Nessa ação, a GRE4 é", "atendida:", "o código é revisado em",
                                "relação aos critérios da história."], 11)
    ligacao_nota(d, [(590, 680), (570, 680)])
    ligacao_nota(d, [(820, 672), (840, 672)])
    fluxo(d, [(430, 716), (430, 820), (682, 820)])
    fluxo(d, [(1080, 672), (1120, 672), (1120, 820), (718, 820)])
    decisao(d, 700, 820)                                   # junção
    fluxo(d, [(700, 838), (700, 852)])
    decisao(d, 700, 870, "travou por impedimento?")
    # impedimento encontrado durante o trabalho na história
    fluxo(d, [(718, 870), (1000, 870), (1000, 898)], "[sim]", (850, 892), "middle")
    acao(d, 890, 900, 220, 56, ["Registrar cartão de", "Impedimento no quadro"])
    fluxo(d, [(1000, 956), (1000, 968)])
    acao(d, 890, 970, 220, 70, ["Tratar o impedimento e", "registrar a resolução", "no cartão"])
    fluxo(d, [(1110, 1005), (1160, 1005), (1160, 525), (718, 525)], "resolvido", (1113, 1022))
    nota(d, 896, 1060, 256, 110, ["Nessas ações, a GPR16 é", "atendida:", "o impedimento fica registrado",
                                  "no quadro, com análise e", "resolução, e é acompanhado",
                                  "por todos no check-in."], 11)
    ligacao_nota(d, [(1000, 1060), (1000, 1040)])
    # sem impedimento: segue para os testes
    fluxo(d, [(700, 888), (700, 928)], "[não]", (708, 914))
    acao(d, 520, 930, 340, 70, ["Escrever testes automatizados e enviar", "o código (a integração contínua",
                                "roda os testes)"])
    artefato(d, 290, 937, 200, 56, ["Código-fonte e", "Testes Automatizados"])
    dependencia(d, [(520, 965), (492, 965)])
    fluxo(d, [(700, 1000), (700, 1068)])
    acao(d, 530, 1070, 340, 62, ["Executar os testes e conferir os", "critérios de aceitação"])
    nota(d, 270, 1063, 230, 76, ["Nessa ação, a GRE4 é", "atendida:", "produto conferido com",
                                 "os requisitos (RF/NF)."], 11)
    ligacao_nota(d, [(500, 1101), (530, 1101)])
    fluxo(d, [(700, 1132), (700, 1155)])
    decisao(d, 700, 1175, "aprovada?")
    fluxo(d, [(682, 1175), (240, 1175), (240, 525), (682, 525)], "[não] volta para Fazendo",
          (250, 1167))
    fluxo(d, [(700, 1193), (700, 1238)], "[sim]", (708, 1208))
    acao(d, 530, 1240, 340, 62, ["Integrar na branch principal e", "mover o cartão para Pronto"])
    nota(d, 890, 1232, 280, 82, ["Nessa ação, a GRE3 é atendida:", "commits e testes citam o cartão;",
                                 "o cartão cita o RF (requisito ↔", "código nos dois sentidos)."], 11, 1)
    ligacao_nota(d, [(870, 1270), (890, 1270)])
    fluxo(d, [(700, 1302), (700, 1342)])
    decisao(d, 700, 1360, "backlog vazio?")
    fluxo(d, [(718, 1360), (1185, 1360), (1185, 440), (852, 440)], "[não]", (1100, 1352))
    fluxo(d, [(700, 1378), (700, 1486)], "[sim]", (708, 1420))

    # Acompanhamento diário (fluxo paralelo): andamento do trabalho, conferido no quadro
    d.add('<rect x="1225" y="380" width="530" height="400" rx="8" fill="#FAFAFA" stroke="#999" '
          'stroke-width="1"/>')
    d.texto(1490, 372, "Acompanhamento diário", 12.5, bold=True, cor="#2F6A8F")
    fluxo(d, [(1580, 354), (1580, 408)])
    acao(d, 1440, 410, 280, 70, ["Check-in diário por mensagem:", "o que cada um fez, o que vai",
                                 "fazer e se está travado"], 12)
    fluxo(d, [(1580, 480), (1580, 508)])
    acao(d, 1440, 510, 280, 70, ["Conferir o quadro (cartões e", "impedimentos em aberto) e",
                                 "ajustar o backlog, se preciso"], 12)
    fluxo(d, [(1580, 580), (1580, 622)])
    decisao(d, 1580, 640, "construção encerrada?")
    fluxo(d, [(1562, 640), (1234, 640), (1234, 445), (1438, 445)],
          "[não] dia seguinte", (1244, 632))
    fluxo(d, [(1580, 658), (1580, 1486)], "[sim]", (1588, 690))
    # o quadro liga os dois fluxos: o impedimento registrado no trabalho é visto no check-in
    objeto(d, 1250, 700, 190, 56, "Quadro Kanban", "(cartões e impedimentos)")
    dependencia(d, [(1110, 914), (1214, 914), (1214, 728), (1248, 728)])
    dependencia(d, [(1420, 700), (1420, 560), (1438, 560)])
    barra(d, 680, 1620, 1490)

    # Entrega final
    moldura(d, 640, 1530, 1130, 160, "Entrega final")
    fluxo(d, [(1150, 1494), (1150, 1588)])
    acao(d, 1000, 1590, 300, 64, ["Executar testes finais do", "sistema completo"])
    fluxo(d, [(1300, 1622), (1348, 1622)])
    acao(d, 1350, 1590, 280, 64, ["Publicar o sistema"])
    fluxo(d, [(1630, 1622), (1690, 1622)])
    fim(d, 1704, 1622)
    return d.svg()


# --- quadro Kanban ilustrativo -----------------------------------------------------------

def quadro_kanban():
    d = Svg(1240, 380)
    cols = [("Backlog", ""), ("Fazendo", "limite: 1 por pessoa"), ("Testes", "limite: 1 por pessoa"),
            ("Pronto", "")]
    w = 295
    for i, (nome, lim) in enumerate(cols):
        x = 20 + i * (w + 10)
        d.add(f'<rect x="{x}" y="20" width="{w}" height="320" rx="8" fill="#F4F7F9" '
              f'stroke="#9AB" stroke-width="1.2"/>')
        d.add(f'<rect x="{x}" y="20" width="{w}" height="46" rx="8" fill="{AZUL_TRACO}"/>')
        d.texto(x + w / 2, 42, nome, 17, bold=True, cor="white")
        if lim:
            d.texto(x + w / 2, 59, lim, 11.5, italic=True, cor="#DDEEFF")

    def cartao(col, y, linhas, cor="#FFFFFF", borda="#7A93A8", etiqueta=None):
        x = 20 + col * (w + 10) + 14
        d.add(f'<rect x="{x}" y="{y}" width="{w - 28}" height="70" rx="6" fill="{cor}" '
              f'stroke="{borda}" stroke-width="1.2"/>')
        for k, t in enumerate(linhas):
            d.texto(x + 10, y + 22 + k * 18, t, 12.5, anchor="start", bold=(k == 0))
        if etiqueta:
            tw = len(etiqueta) * 7 + 12
            d.add(f'<rect x="{x + w - 28 - tw - 8}" y="{y + 8}" width="{tw}" height="18" rx="9" '
                  f'fill="{etiqueta[1] if isinstance(etiqueta, tuple) else "#2F6A8F"}"/>')

    def tag(col, y, txt, cor):
        x = 20 + col * (w + 10) + 14
        tw = len(txt) * 7 + 14
        d.add(f'<rect x="{x + w - 28 - tw - 8}" y="{y + 8}" width="{tw}" height="18" rx="9" '
              f'fill="{cor}"/>')
        d.texto(x + w - 28 - tw / 2 - 8, y + 21, txt, 11, bold=True, cor="white")

    cartao(0, 85, ["#31 · F18 Denunciar conteúdo", "Como usuário, quero denunciar", "um perfil ou avaliação…"])
    cartao(0, 170, ["#32 · F19 Moderar denúncias", "Como administrador, quero…"])
    cartao(0, 255, ["#33 · F20 Gerenciar categorias", "Como administrador, quero…"])
    cartao(1, 85, ["#24 · F8 Buscar prestadores", "Hugo e Lucas (em par)"])
    tag(1, 85, "complexa", "#C26A00")
    cartao(1, 170, ["#27 · F16 Responder avaliação", "Luis Felipe (individual + revisão)"])
    cartao(1, 255, ["Impedimento · #24", "API de geocodificação fora do", "ar; ver alternativa…"],
           cor="#FDECEC", borda="#C0392B")
    tag(1, 255, "impedimento", "#C0392B")
    cartao(2, 85, ["#22 · F7 Obter localização", "Critérios de aceitação: 3/4 ✓"])
    cartao(3, 85, ["#20 · F1 Cadastrar usuário", "Testes ✓ · integrado ✓"])
    cartao(3, 170, ["#21 · F2 Login", "Testes ✓ · integrado ✓"])
    d.texto(620, 366, "Exemplo ilustrativo de cartões: número da história · RF de origem · descrição",
            11.5, italic=True, cor="#555")
    return d.svg()
