# -*- coding: utf-8 -*-
"""
Protótipos (esboços) das telas do Bicus para a Análise de Pontos de Função.

Estilo inspirado nos protótipos do sistema de locadora da aula de APF: telas brancas com
borda preta, botões turquesa, grades vazias, combos com ▼, setas de navegação e alertas
arredondados. Cada tela tem um código (T01...T29) usado nas tabelas de contagem.

O renderizador de SVG usado (PyMuPDF) não suporta gradiente nem traço pontilhado, por isso
tudo é desenhado com cores sólidas.
"""

FONTE = "Arial"
COR_BTN, COR_BTN_BORDA, COR_BTN_TXT = "#5ab8c5", "#2f8794", "#0c2a30"
COR_ALERTA, COR_ALERTA_BORDA = "#f4f4f4", "#9a9a9a"
COR_CAB = "#dff1f4"
LARG, ALT = 1400, 900


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def larg_txt(s, size):
    w = 0.0
    for ch in s:
        if ch in "ilj.,;:!'|I":
            w += 0.24
        elif ch in "tfr()[] -/":
            w += 0.32
        elif ch in "mwMW":
            w += 0.84
        elif ch.isupper():
            w += 0.67
        elif ch.isdigit():
            w += 0.56
        else:
            w += 0.53
    return w * size


class Desenho:
    def __init__(self, w=LARG, h=ALT):
        self.w, self.h, self.p = w, h, []

    def add(self, s):
        self.p.append(s)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n<rect width="{self.w}" height="{self.h}" '
                f'fill="white"/>\n' + "\n".join(self.p) + "\n</svg>")


# ---------------------------------------------------------------------------
# Primitivas
# ---------------------------------------------------------------------------

def texto(d, x, y, s, size=14, anchor="start", bold=False, cor="#111", italic=False):
    d.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONTE}" font-size="{size}" '
          f'font-weight="{"bold" if bold else "normal"}" '
          f'font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}" '
          f'fill="{cor}">{esc(s)}</text>')


def ret(d, x, y, w, h, fill="white", stroke="#000", sw=1.2, rx=0, opacity=None):
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    st = f'stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else 'stroke="none"'
    d.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
          f'fill="{fill}"{op} {st}/>')


def linha(d, x1, y1, x2, y2, cor="#000", sw=1.0):
    d.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{cor}" '
          f'stroke-width="{sw}"/>')


def botao(d, x, y, s, size=13, w=None, h=26):
    w = w or larg_txt(s, size) + 22
    ret(d, x, y, w, h, fill=COR_BTN, stroke=COR_BTN_BORDA, rx=3)
    ret(d, x + 1.5, y + 1.5, w - 3, h / 2 - 1.5, fill="#ffffff", stroke="none", rx=2,
        opacity=0.28)
    texto(d, x + w / 2, y + h / 2 + size * 0.36, s, size, anchor="middle", cor=COR_BTN_TXT)
    return w


def caixa(d, x, y, w, h=24, valor=None, cinza=False):
    ret(d, x, y, w, h, fill="#ececec" if cinza else "white", stroke="#000", sw=1.1)
    if valor:
        texto(d, x + 6, y + h / 2 + 4.5, valor, 12, cor="#777", italic=True)


def combo(d, x, y, w, valor, h=24):
    caixa(d, x, y, w, h)
    texto(d, x + 6, y + h / 2 + 4.5, valor, 12, cor="#333")
    ret(d, x + w - h, y, h, h, fill="#9a9a9a", stroke="#000", sw=1.1)
    cx, cy = x + w - h / 2, y + h / 2
    d.add(f'<polygon points="{cx - 6:.1f},{cy - 3.5:.1f} {cx + 6:.1f},{cy - 3.5:.1f} '
          f'{cx:.1f},{cy + 5:.1f}" fill="#111"/>')


def checkbox(d, x, y, marcado=False, s=13):
    ret(d, x, y, s, s, fill="white", stroke="#000", sw=1.1)
    if marcado:
        d.add(f'<polyline points="{x + 2.5:.1f},{y + s / 2:.1f} {x + s / 2 - 1:.1f},'
              f'{y + s - 3:.1f} {x + s - 2:.1f},{y + 2.5:.1f}" fill="none" stroke="#111" '
              f'stroke-width="1.8"/>')


def grade(d, x, y, w, cab, n=3, h_lin=22, pesos=None):
    pesos = pesos or [1] * len(cab)
    tot = sum(pesos)
    xs = [x]
    for p in pesos:
        xs.append(xs[-1] + w * p / tot)
    h = h_lin * (n + 1)
    ret(d, x, y, w, h_lin, fill=COR_CAB, stroke="none")
    for i, c in enumerate(cab):
        cw = xs[i + 1] - xs[i]
        size = 11
        while larg_txt(c, size) > cw - 4 and size > 8:
            size -= 0.5
        texto(d, (xs[i] + xs[i + 1]) / 2, y + h_lin / 2 + 4, c, size, anchor="middle",
              bold=True, cor="#21414a")
    for k in range(1, n + 1):
        linha(d, x, y + k * h_lin, x + w, y + k * h_lin)
    for xx in xs[1:-1]:
        linha(d, xx, y, xx, y + h)
    ret(d, x, y, w, h, fill="none", stroke="#000", sw=1.2)
    return h


def foto(d, x, y, w, h):
    ret(d, x, y, w, h, fill="#eeeeee", stroke="#888", sw=1)
    linha(d, x, y, x + w, y + h, "#bbb")
    linha(d, x + w, y, x, y + h, "#bbb")


def alerta(d, x, y, w, linhas, botoes=(), campos=(), size=13, lw=None):
    """Caixa de alerta/diálogo. campos: [(rótulo, 'campo'|'combo'|'area', valor)]."""
    h = 12 + 19 * len(linhas)
    for c in campos:
        h += 58 if c[1] == "area" else 32
    if botoes:
        h += 36
    h += 6
    ret(d, x + 3, y + 3, w, h, fill="#000", stroke="none", rx=14, opacity=0.14)
    ret(d, x, y, w, h, fill=COR_ALERTA, stroke=COR_ALERTA_BORDA, rx=14, sw=1.2)
    cy = y + 12
    for t in linhas:
        texto(d, x + w / 2, cy + 13, t, size, anchor="middle")
        cy += 19
    lw = lw or (max(larg_txt(c[0], 13) for c in campos) + 12 if campos else 0)
    for rot, tipo, val in campos:
        cy += 6
        texto(d, x + 14, cy + 16, rot, 13)
        if tipo == "combo":
            combo(d, x + 14 + lw, cy, w - 28 - lw, val)
        elif tipo == "area":
            caixa(d, x + 14 + lw, cy, w - 28 - lw, 48, val)
            cy += 26
        else:
            caixa(d, x + 14 + lw, cy, w - 28 - lw, 24, val)
        cy += 26
    if botoes:
        cy += 6
        ws = [larg_txt(b, 13) + 22 for b in botoes]
        bx = x + (w - (sum(ws) + 12 * (len(ws) - 1))) / 2
        for b, bw in zip(botoes, ws):
            botao(d, bx, cy, b, w=bw)
            bx += bw + 12
    return h


def seta(d, x1, y1, x2, y2, dupla=True, rotulo=None, lado=1):
    import math
    linha(d, x1, y1, x2, y2, "#111", 1.3)
    ang = math.atan2(y2 - y1, x2 - x1)

    def cabeca(px, py, a):
        s = 9
        p1 = (px - s * math.cos(a - 0.42), py - s * math.sin(a - 0.42))
        p2 = (px - s * math.cos(a + 0.42), py - s * math.sin(a + 0.42))
        d.add(f'<polygon points="{px:.1f},{py:.1f} {p1[0]:.1f},{p1[1]:.1f} '
              f'{p2[0]:.1f},{p2[1]:.1f}" fill="#111"/>')
    cabeca(x2, y2, ang)
    if dupla:
        cabeca(x1, y1, ang + math.pi)
    if rotulo:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        w = larg_txt(rotulo, 12) + 8
        ox = 6 * lado if abs(x2 - x1) < abs(y2 - y1) else -w / 2
        oy = -6 if abs(x2 - x1) >= abs(y2 - y1) else 4
        ret(d, mx + ox - (0 if ox >= 0 else 0), my + oy - 12, w, 16, fill="white",
            stroke="none")
        texto(d, mx + ox + 4, my + oy, rotulo, 12, italic=True, cor="#444")


def etiqueta(d, titulo):
    ret(d, 20, 18, 196, 38, fill="#5e6b75", stroke="#3e4a52", rx=8)
    texto(d, 118, 43, "Protótipo para APF", 16, anchor="middle", cor="white")
    texto(d, LARG / 2 + 60, 44, titulo, 21, anchor="middle", bold=True, cor="#2b3a42")


def referencia(d, x, y, w, s, h=36):
    """Caixa cinza que representa uma tela desenhada em outra prancha."""
    ret(d, x, y, w, h, fill="#f1f1f1", stroke="#9a9a9a", rx=5)
    texto(d, x + w / 2, y + h / 2 + 5, s, 13, anchor="middle", italic=True, cor="#555")
    return {"top": (x + w / 2, y), "bottom": (x + w / 2, y + h), "left": (x, y + h / 2),
            "right": (x + w, y + h / 2)}


def nota(d, x, y, linhas_txt, size=12):
    for i, t in enumerate(linhas_txt):
        texto(d, x, y + i * (size + 5), t, size, italic=True, cor="#555")


# ---------------------------------------------------------------------------
# Tela com layout automático em linhas
# ---------------------------------------------------------------------------

class Tela:
    PAD, GAP = 14, 10

    def __init__(self, cod, titulo, x, y, w, linhas, lw=110, titulo_dir=False):
        self.cod, self.titulo, self.x, self.y, self.w = cod, titulo, x, y, w
        self.linhas, self.lw, self.h = linhas, lw, 0
        self.titulo_dir = titulo_dir   # título alinhado à direita (setas chegando pela esquerda)
        self.marcas = {}   # posições nomeadas (ex.: botões) para ancorar setas e alertas

    # ---- linhas -----------------------------------------------------------
    def _campo(self, d, y, rot, valor=None, cinza=False):
        texto(d, self.x + self.PAD, y + 17, rot, 14)
        caixa(d, self.x + self.PAD + self.lw, y, self.w - 2 * self.PAD - self.lw, 24, valor,
              cinza)
        return 24

    def _combo(self, d, y, rot, valor):
        texto(d, self.x + self.PAD, y + 17, rot, 14)
        combo(d, self.x + self.PAD + self.lw, y, self.w - 2 * self.PAD - self.lw, valor)
        return 24

    def _arquivo(self, d, y, rot, btn):
        texto(d, self.x + self.PAD, y + 17, rot, 14)
        bw = larg_txt(btn, 13) + 22
        x0 = self.x + self.PAD + self.lw
        caixa(d, x0, y, self.w - 2 * self.PAD - self.lw - bw - 8, 24)
        botao(d, self.x + self.w - self.PAD - bw, y - 1, btn, w=bw)
        return 24

    def _area(self, d, y, rot, n=2, valor=None, cinza=False):
        texto(d, self.x + self.PAD, y + 14, rot, 14)
        h = 18 * n + 8
        caixa(d, self.x + self.PAD, y + 20, self.w - 2 * self.PAD, h, valor, cinza)
        return 20 + h

    def _par(self, d, y, itens):
        """itens: [(rótulo, tipo, largura_rótulo, largura_campo, valor)]"""
        x = self.x + self.PAD
        for rot, tipo, lw, cw, val in itens:
            texto(d, x, y + 17, rot, 14)
            x += lw
            if tipo == "combo":
                combo(d, x, y, cw, val or "")
            else:
                caixa(d, x, y, cw, 24, val)
            x += cw + 18
        return 24

    def _check(self, d, y, s, marcado=False):
        checkbox(d, self.x + self.PAD, y + 2, marcado)
        texto(d, self.x + self.PAD + 20, y + 13, s, 13)
        return 16

    def _botoes(self, d, y, nomes, alinh="direita", size=13):
        ws = [larg_txt(n, size) + 22 for n in nomes]
        total = sum(ws) + 10 * (len(ws) - 1)
        if alinh == "direita":
            x = self.x + self.w - self.PAD - total
        elif alinh == "centro":
            x = self.x + (self.w - total) / 2
        else:
            x = self.x + self.PAD
        for n, bw in zip(nomes, ws):
            botao(d, x, y, n, size, w=bw)
            self.marcas[n] = (x, y, bw, 26)
            x += bw + 10
        return 26

    def _menu(self, d, y, nomes):
        n = len(nomes)
        disp = self.w - 2 * self.PAD
        bw = (disp - 14 * (n - 1)) / n
        x = self.x + self.PAD
        for nome in nomes:
            partes = nome.split("\n")
            ret(d, x, y, bw, 50, fill=COR_BTN, stroke=COR_BTN_BORDA, rx=3)
            ret(d, x + 1.5, y + 1.5, bw - 3, 23.5, fill="#ffffff", stroke="none", rx=2,
                opacity=0.28)
            for i, p in enumerate(partes):
                yy = y + 30 + (i - (len(partes) - 1) / 2) * 17
                texto(d, x + bw / 2, yy, p, 15, anchor="middle", cor=COR_BTN_TXT)
            self.marcas[nome.replace("\n", " ")] = (x, y, bw, 50)
            x += bw + 14
        return 50

    def _grade(self, d, y, cab, n=3, pesos=None):
        return grade(d, self.x + self.PAD, y, self.w - 2 * self.PAD, cab, n, 22, pesos)

    def _texto(self, d, y, s, size=13, bold=False, italic=False, cor="#111", centro=False):
        if centro:
            texto(d, self.x + self.w / 2, y + size, s, size, anchor="middle", bold=bold,
                  italic=italic, cor=cor)
        else:
            texto(d, self.x + self.PAD, y + size, s, size, bold=bold, italic=italic, cor=cor)
        return size + 5

    def _secao(self, d, y, s):
        texto(d, self.x + self.PAD, y + 13, s, 13, bold=True, cor="#21414a")
        linha(d, self.x + self.PAD + larg_txt(s, 13) + 10, y + 9, self.x + self.w - self.PAD,
              y + 9, "#9bbcc2")
        return 16

    def _info(self, d, y, rot, valor=""):
        texto(d, self.x + self.PAD, y + 14, rot, 13, bold=True)
        texto(d, self.x + self.PAD + larg_txt(rot, 13) * 1.12 + 8, y + 14, valor, 13,
              cor="#555", italic=True)
        return 18

    def _estrelas(self, d, y, rot):
        texto(d, self.x + self.PAD, y + 19, rot, 14)
        texto(d, self.x + self.PAD + self.lw, y + 22, "☆ ☆ ☆ ☆ ☆", 24, cor="#c48a00")
        return 28

    def _fotos(self, d, y, rot, n=4, botao_txt=None):
        texto(d, self.x + self.PAD, y + 14, rot, 14)
        x = self.x + self.PAD + self.lw
        for _ in range(n):
            foto(d, x, y, 54, 42)
            x += 62
        if botao_txt:
            botao(d, x + 6, y + 8, botao_txt)
        return 42

    def _perfil(self, d, y):
        foto(d, self.x + self.PAD, y, 78, 78)
        x = self.x + self.PAD + 92
        texto(d, x, y + 18, "Nome do prestador", 16, bold=True)
        texto(d, x, y + 40, "Bairro – Cidade  ·  2,3 km de você", 13, cor="#444")
        texto(d, x, y + 62, "★ 4,7  (32 avaliações)  ·  41 serviços concluídos", 13,
              cor="#444")
        return 78

    def _dist_disp(self, d, y):
        x0 = self.x + self.PAD
        texto(d, x0, y + 13, "Distribuição das notas", 12, bold=True, cor="#21414a")
        for i, (n, frac) in enumerate(zip("54321", (0.8, 0.45, 0.15, 0.05, 0.03))):
            yy = y + 20 + i * 15
            texto(d, x0, yy + 10, f"{n} ★", 11, cor="#444")
            ret(d, x0 + 30, yy + 2, 150, 9, fill="white", stroke="#999", sw=0.8)
            ret(d, x0 + 30, yy + 2, 150 * frac, 9, fill="#bbbbbb", stroke="none")
        xd = self.x + self.w / 2 + 10
        texto(d, xd, y + 13, "Disponibilidade", 12, bold=True, cor="#21414a")
        dias = ["", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        cw = (self.x + self.w - self.PAD - xd) / 8
        for i, dd in enumerate(dias):
            texto(d, xd + i * cw + cw / 2, y + 30, dd, 10, anchor="middle", cor="#444")
        for j, t in enumerate(["M", "T", "N"]):
            texto(d, xd + cw / 2, y + 46 + j * 15, t, 10, anchor="middle", cor="#444")
            for i in range(1, 8):
                checkbox(d, xd + i * cw + cw / 2 - 5, y + 37 + j * 15, (i + j) % 3 != 0, 10)
        texto(d, xd, y + 96, "Indisponível até: —", 11, italic=True, cor="#555")
        return 98

    def _disp(self, d, y):
        dias = ["", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        x0 = self.x + self.PAD
        cw = (self.w - 2 * self.PAD) / 8
        for i, dd in enumerate(dias):
            texto(d, x0 + i * cw + cw / 2, y + 14, dd, 13, anchor="middle", bold=True,
                  cor="#21414a")
        for j, t in enumerate(["Manhã", "Tarde", "Noite"]):
            texto(d, x0 + 4, y + 40 + j * 24, t, 13)
            for i in range(1, 8):
                checkbox(d, x0 + i * cw + cw / 2 - 7, y + 28 + j * 24, (i + j) % 3 != 0, 14)
        return 100

    def _espaco(self, d, y, h):
        return h

    # ---- desenho ----------------------------------------------------------
    def desenhar(self, d):
        corpo = Desenho()
        y = self.y + self.PAD
        for item in self.linhas:
            tipo, args = item[0], item[1:]
            y += getattr(self, "_" + tipo)(corpo, y, *args) + self.GAP
        self.h = y - self.GAP + self.PAD - self.y
        if self.titulo_dir:
            texto(d, self.x + self.w, self.y - 9, f"{self.cod} · {self.titulo}", 15,
                  anchor="end", bold=True, cor="#1d2a31")
        else:
            texto(d, self.x, self.y - 9, f"{self.cod} · {self.titulo}", 15, bold=True,
                  cor="#1d2a31")
        ret(d, self.x, self.y, self.w, self.h, fill="white", stroke="#000", sw=1.6)
        d.p.extend(corpo.p)
        return self

    def a(self, lado, t=0.5):
        """Ponto na borda da tela para ancorar setas."""
        if lado == "top":
            return (self.x + self.w * t, self.y)
        if lado == "bottom":
            return (self.x + self.w * t, self.y + self.h)
        if lado == "left":
            return (self.x, self.y + self.h * t)
        return (self.x + self.w, self.y + self.h * t)

    def btn(self, nome, lado="bottom"):
        x, y, w, h = self.marcas[nome]
        return {"bottom": (x + w / 2, y + h), "top": (x + w / 2, y), "left": (x, y + h / 2),
                "right": (x + w, y + h / 2)}[lado]


# ---------------------------------------------------------------------------
# Pranchas
# ---------------------------------------------------------------------------
# Ordem de desenho em cada prancha: telas -> alertas/diálogos -> setas (as setas por último
# para que os rótulos não fiquem escondidos atrás de alertas).


def prancha1():
    d = Desenho(LARG, 840)
    t01 = Tela("T01", "Login", 40, 110, 360, [
        ("campo", "E-mail:"), ("campo", "Senha:"),
        ("botoes", ["Entrar"]),
        ("botoes", ["Criar conta", "Esqueci minha senha"], "centro"),
    ], lw=70).desenhar(d)
    t04 = Tela("T04", "Recuperar senha", 40, 370, 360, [
        ("texto", "Informe o e-mail cadastrado.", 13, False, True, "#444"),
        ("campo", "E-mail:"), ("botoes", ["Enviar link", "Voltar"]),
    ], lw=70).desenhar(d)
    t05 = Tela("T05", "Redefinir senha", 40, 640, 360, [
        ("campo", "Nova senha:"), ("campo", "Confirmar senha:"),
        ("botoes", ["Salvar senha"]),
    ], lw=130).desenhar(d)
    t02 = Tela("T02", "Cadastro de usuário", 500, 110, 450, [
        ("campo", "Nome completo:"), ("campo", "E-mail:"), ("campo", "Senha:"),
        ("campo", "CPF:", "000.000.000-00"), ("campo", "Telefone:"),
        ("campo", "Data de nascimento:", "dd/mm/aaaa"), ("campo", "Endereço:"),
        ("campo", "Complemento:", "(opcional)"),
        ("arquivo", "Foto de perfil:", "Escolher..."),
        ("check", "Li e aceito os Termos de Uso e a Política de Privacidade"),
        ("botoes", ["Cadastrar", "Voltar"]),
    ], lw=150).desenhar(d)
    t03 = Tela("T03", "Confirmação de e-mail", 1030, 110, 330, [
        ("texto", "E-mail confirmado!", 16, True, False, "#111", True),
        ("texto", "Sua conta está ativa.", 13, False, False, "#444", True),
        ("botoes", ["Ir para o login"], "centro"),
    ]).desenhar(d)

    alerta(d, 50, t01.y + t01.h + 20, 270, ["ALERTA: E-mail ou senha", "inválidos."])
    alerta(d, 50, t04.y + t04.h + 16, 290, ["ALERTA: Link de redefinição",
                                             "enviado para o seu e-mail."])
    alerta(d, 450, t05.y + 4, 360, ["ALERTA: Senha redefinida com sucesso!"])
    alerta(d, 450, t05.y + 66, 360, ["ALERTA: Senha fora da política",
                                      "ou confirmação diferente."])
    alerta(d, 990, 390, 370, ["ALERTA: Cadastro realizado! Confirme",
                              "seu e-mail pelo link enviado."])
    alerta(d, 990, 470, 370, ["ALERTA: Dados inválidos (CPF, idade",
                              "mínima ou conta já existente)."])

    p1, p2 = t01.a("right", 0.78), t02.a("left", 0.2)
    seta(d, *p1, *p2)
    texto(d, 407, (p1[1] + p2[1]) / 2 - 10, "Criar conta", 12, italic=True, cor="#444")
    seta(d, *t01.a("bottom", 0.9), *t04.a("top", 0.9), rotulo="Esqueci minha senha")
    seta(d, *t04.a("bottom", 0.9), *t05.a("top", 0.9), rotulo="link no e-mail")
    p1, p2 = t02.a("right", 0.08), t03.a("left", 0.4)
    seta(d, *p1, *p2)
    texto(d, 958, p1[1] - 12, "link no e-mail", 11, italic=True, cor="#444")
    return d.svg()


def prancha2():
    d = Desenho(LARG, 980)
    t06 = Tela("T06", "Menu principal", 300, 100, 800, [
        ("menu", ["Buscar\nprestadores", "Minhas\nsolicitações", "Minha\nconta",
                  "Área do\nprestador", "Sair"]),
    ]).desenhar(d)
    t07 = Tela("T07", "Buscar prestadores", 40, 270, 620, [
        ("combo", "Categoria:", "Categorias..."),
        ("campo", "Raio de busca (km):"),
        ("campo", "Endereço de partida:", "(opcional — padrão: endereço da conta)"),
        ("secao", "Filtros"),
        ("par", [("Preço máx. (R$):", "campo", 118, 110, None),
                 ("Nota mínima:", "combo", 96, 100, "Qualquer")]),
        ("par", [("Dia:", "combo", 40, 150, "Qualquer"),
                 ("Turno:", "combo", 52, 150, "Qualquer")]),
        ("botoes", ["Buscar"]),
        ("grade", ["Foto", "Prestador", "Serviço", "Preço (R$)", "Nota", "Aval.", "Dist."], 5,
         [0.7, 1.6, 1.6, 1.2, 0.7, 0.7, 0.8]),
        ("botoes", ["Ver perfil", "Voltar"]),
    ], lw=150).desenhar(d)
    t08 = Tela("T08", "Perfil do prestador", 720, 270, 640, [
        ("perfil",),
        ("area", "Apresentação:", 2, None, True),
        ("dist_disp",),
        ("secao", "Serviços oferecidos"),
        ("grade", ["Categoria", "Serviço", "Descrição", "Preço (R$)", "Unidade"], 2,
         [1.1, 1.2, 1.8, 1, 0.9]),
        ("fotos", "Portfólio:", 6),
        ("par", [("Avaliações — filtrar por nota:", "combo", 205, 130, "Todas")]),
        ("grade", ["Data", "Nota", "Comentário", "Anexos", "Resposta"], 2,
         [0.8, 0.6, 1.8, 0.8, 1.6]),
        ("botoes", ["Solicitar serviço", "Denunciar perfil", "Denunciar avaliação", "Voltar"]),
    ], lw=86).desenhar(d)
    alerta(d, 230, t07.y + t07.h - 165, 380, ["ALERTA: Nenhum prestador encontrado.",
                                               "Tente ampliar o raio de busca."])
    seta(d, *t06.btn("Buscar prestadores", "bottom"), *t07.a("top", 0.5),
         rotulo="Buscar prestadores")
    p1, p2 = t07.a("right", 0.62), t08.a("left", 0.5)
    seta(d, *p1, *p2)
    texto(d, 664, p1[1] - 10, "Ver perfil", 12, italic=True, cor="#444")
    return d.svg()


def prancha3():
    d = Desenho(LARG, 720)
    ref = referencia(d, 420, 95, 560, "T08 · Perfil do prestador (protótipo 2)")
    t09 = Tela("T09", "Solicitar serviço", 40, 220, 560, [
        ("combo", "Serviço:", "Serviços do prestador..."),
        ("area", "Descrição da necessidade:", 3),
        ("par", [("Data desejada:", "campo", 112, 140, "dd/mm/aaaa"),
                 ("Turno:", "combo", 52, 160, "Manhã")]),
        ("campo", "Endereço do serviço:"),
        ("botoes", ["Enviar solicitação", "Voltar"]),
    ], lw=150).desenhar(d)
    t10 = Tela("T10", "Denunciar conteúdo", 800, 220, 560, [
        ("texto", "Item denunciado: perfil do prestador ou avaliação", 13, False, True, "#444"),
        ("combo", "Motivo:", "Conteúdo ofensivo"),
        ("area", "Descrição (opcional):", 3),
        ("botoes", ["Enviar denúncia", "Cancelar"]),
    ], lw=80).desenhar(d)
    alerta(d, 120, t09.y + t09.h + 26, 420, ["ALERTA: Solicitação enviada!",
                                              "O prestador tem até 72 h para responder."])
    alerta(d, 120, t09.y + t09.h + 102, 420, ["ALERTA: Data inválida ou limite de",
                                               "10 solicitações pendentes atingido."])
    alerta(d, 880, t10.y + t10.h + 26, 400, ["ALERTA: Denúncia registrada. Obrigado!"])
    alerta(d, 880, t10.y + t10.h + 84, 400, ["ALERTA: Você já denunciou este item."])
    seta(d, 560, ref["bottom"][1], *t09.a("top", 0.7), rotulo="Solicitar serviço")
    seta(d, 840, ref["bottom"][1], *t10.a("top", 0.6), rotulo="Denunciar perfil / avaliação")
    return d.svg()


def prancha4():
    d = Desenho(LARG, 700)
    ref = referencia(d, 40, 95, 360, "T06 · Menu principal (protótipo 2)")
    t11 = Tela("T11", "Minha conta", 40, 220, 560, [
        ("campo", "Nome:"), ("campo", "E-mail:"), ("campo", "Telefone:"),
        ("campo", "Endereço:"), ("campo", "Complemento:"),
        ("arquivo", "Foto de perfil:", "Alterar foto..."),
        ("campo", "CPF:", "000.000.000-00  (não editável)", True),
        ("campo", "Data de nascimento:", "dd/mm/aaaa  (não editável)", True),
        ("botoes", ["Salvar alterações", "Voltar"]),
        ("botoes", ["Alterar senha", "Excluir conta"], "esquerda"),
    ], lw=150).desenhar(d)
    for y, rot in ((222, "Salvar alterações"), (342, "Alterar senha"), (512, "Excluir conta")):
        texto(d, 680, y, rot, 12, italic=True, cor="#444")
    alerta(d, 680, 230, 320, ["ALERTA: Dados atualizados!"])
    alerta(d, 1020, 230, 340, ["ALERTA: Confirme o novo e-mail", "pelo link enviado."])
    alerta(d, 680, 350, 380, [], botoes=["Salvar", "Cancelar"],
           campos=[("Senha atual:", "campo", None), ("Nova senha:", "campo", None)])
    alerta(d, 1080, 350, 280, ["ALERTA: Senha alterada!"])
    alerta(d, 1080, 410, 280, ["ALERTA: Senha atual", "incorreta."])
    alerta(d, 680, 520, 380, ["ALERTA: Confirma a exclusão", "da sua conta?"],
           botoes=["Sim", "Não"])
    alerta(d, 1080, 520, 280, ["ALERTA: Conta excluída."])
    alerta(d, 1080, 580, 280, ["ALERTA: Há solicitações", "em andamento."])
    seta(d, *ref["bottom"], *t11.a("top", 0.32), rotulo="Minha conta")
    xb = t11.x + t11.w
    ys = t11.marcas["Salvar alterações"][1] + 13
    ya = t11.marcas["Alterar senha"][1] + 9
    seta(d, xb, ys, 680, 250, dupla=False)
    seta(d, xb, ya, 680, 410, dupla=False)
    seta(d, xb, ya + 8, 680, 565, dupla=False)
    return d.svg()


def prancha5():
    d = Desenho(LARG, 890)
    ref = referencia(d, 300, 95, 360, "T06 · Menu principal (protótipo 2)")
    t12 = Tela("T12", "Minhas solicitações", 40, 220, 760, [
        ("par", [("Estado:", "combo", 60, 170, "Todos"),
                 ("Ordenar por:", "combo", 92, 190, "Mais recentes")]),
        ("grade", ["Data", "Serviço", "Prestador", "Data desejada", "Turno", "Estado",
                   "Valor (R$)"], 5, [0.9, 1.4, 1.4, 1.1, 0.8, 1, 0.9]),
        ("botoes", ["Ver detalhes", "Cancelar", "Confirmar conclusão", "Avaliar", "Voltar"]),
    ]).desenhar(d)
    t13 = Tela("T13", "Detalhes da solicitação", 880, 220, 480, [
        ("info", "Serviço:", "Faxina residencial"), ("info", "Prestador / Cliente:", "Nome"),
        ("info", "Telefone:", "(liberado após o aceite)"), ("info", "Descrição:", "..."),
        ("info", "Data desejada / Turno:", "dd/mm/aaaa · Manhã"),
        ("info", "Endereço:", "..."), ("info", "Estado:", "Aceita"),
        ("info", "Observação do prestador:", "..."),
        ("info", "Motivo (recusa/cancelamento):", "—"), ("info", "Valor cobrado:", "R$ —"),
        ("botoes", ["Abrir WhatsApp", "Voltar"]),
    ]).desenhar(d)
    t14 = Tela("T14", "Avaliar prestador", 880, 600, 480, [
        ("estrelas", "Nota:"), ("area", "Comentário (opcional):", 2),
        ("fotos", "Anexos:", 3, "Adicionar fotos"),
        ("botoes", ["Enviar avaliação", "Voltar"]),
    ], lw=86).desenhar(d)
    y0 = t12.y + t12.h + 30
    alerta(d, 40, y0, 320, [], botoes=["Confirmar", "Voltar"],
           campos=[("Motivo do cancelamento:", "campo", None)])
    alerta(d, 40, y0 + 100, 320, ["ALERTA: Solicitação cancelada."])
    alerta(d, 380, y0, 320, ["ALERTA: O serviço foi realizado?"], botoes=["Sim", "Não"],
           campos=[("Valor cobrado (R$):", "campo", None)])
    alerta(d, 380, y0 + 118, 320, ["ALERTA: Conclusão confirmada!", "Avalie o prestador."])
    alerta(d, 1060, t14.y + t14.h + 12, 300, ["ALERTA: Avaliação publicada!"])
    seta(d, *ref["bottom"], 480, t12.y, rotulo="Minhas solicitações")
    p1, p2 = t12.a("right", 0.2), t13.a("left", 0.25)
    seta(d, *p1, *p2)
    texto(d, 806, p1[1] - 10, "Ver detalhes", 12, italic=True, cor="#444")
    cb = t12.btn("Cancelar", "bottom")
    seta(d, cb[0], cb[1], 200, y0, dupla=False)
    cc = t12.btn("Confirmar conclusão", "bottom")
    seta(d, cc[0], cc[1], 540, y0, dupla=False)
    av = t12.btn("Avaliar", "bottom")
    seta(d, av[0], av[1], *t14.a("left", 0.35), rotulo="Avaliar")
    return d.svg()


def prancha6():
    d = Desenho(LARG, 1000)
    t15 = Tela("T15", "Área do prestador", 220, 100, 960, [
        ("menu", ["Perfil de\nprestador", "Meus\nserviços", "Disponibilidade",
                  "Solicitações\nrecebidas", "Avaliações\nrecebidas", "Voltar"]),
    ]).desenhar(d)
    t16 = Tela("T16", "Perfil de prestador (tornar-se prestador / editar)", 40, 280, 520, [
        ("area", "Apresentação profissional:", 3),
        ("campo", "Local base:"),
        ("check", "Usar o endereço da minha conta", True),
        ("campo", "Raio de deslocamento (km):"),
        ("fotos", "Portfólio:", 3, "Adicionar fotos"),
        ("botoes", ["Salvar", "Voltar"]),
        ("botoes", ["Desativar perfil"], "esquerda"),
    ], lw=190).desenhar(d)
    t17 = Tela("T17", "Meus serviços", 620, 280, 740, [
        ("grade", ["Categoria", "Serviço", "Preço mín. (R$)", "Preço máx. (R$)", "Unidade"], 4,
         [1.2, 1.6, 1, 1, 1]),
        ("botoes", ["Novo", "Editar", "Excluir", "Voltar"], "esquerda"),
    ]).desenhar(d)
    t18 = Tela("T18", "Serviço", 620, 540, 440, [
        ("combo", "Categoria:", "Categorias..."),
        ("botoes", ["Sugerir nova categoria"]),
        ("campo", "Título:"), ("area", "Descrição:", 2),
        ("par", [("Preço mín. (R$):", "campo", 118, 90, None),
                 ("máx.:", "campo", 40, 90, None)]),
        ("combo", "Unidade de cobrança:", "Por hora"),
        ("botoes", ["Salvar", "Voltar"]),
    ], lw=160, titulo_dir=True).desenhar(d)
    alerta(d, 40, t16.y + t16.h + 22, 520, ["ALERTA: Perfil salvo! Cadastre seus serviços",
                                             "para aparecer nas buscas."])
    alerta(d, 40, t16.y + t16.h + 92, 250, ["ALERTA: Deseja desativar", "seu perfil?"],
           botoes=["Sim", "Não"])
    alerta(d, 310, t16.y + t16.h + 92, 250, ["ALERTA: Perfil desativado."])
    alerta(d, 310, t16.y + t16.h + 142, 250, ["ALERTA: Há solicitações", "em andamento."])
    x = 1090
    alerta(d, x, 470, 270, ["ALERTA: Confirma", "exclusão?"], botoes=["Sim", "Não"])
    alerta(d, x, 574, 270, ["ALERTA: Serviço excluído."])
    alerta(d, x, 623, 270, ["ALERTA: Serviço com", "solicitações em andamento."])
    alerta(d, x, 691, 270, [], botoes=["Enviar", "Cancelar"],
           campos=[("Categoria:", "campo", None)])
    alerta(d, x, 789, 270, ["ALERTA: Sugestão enviada", "para aprovação."])
    alerta(d, x, 857, 270, ["ALERTA: Serviço salvo!"])
    alerta(d, x, 906, 270, ["ALERTA: Categoria repetida ou", "faixa de preço inválida."])
    seta(d, *t15.btn("Perfil de prestador", "bottom"), *t16.a("top", 0.85))
    seta(d, *t15.btn("Meus serviços", "bottom"), *t17.a("top", 0.35))
    nb, eb = t17.btn("Novo", "bottom"), t17.btn("Editar", "bottom")
    seta(d, nb[0], nb[1], nb[0], t18.y)
    seta(d, eb[0], eb[1], eb[0], t18.y, rotulo="Novo / Editar")
    ex = t17.btn("Excluir", "bottom")
    seta(d, ex[0], ex[1], x, 500, dupla=False)
    sg = t18.btn("Sugerir nova categoria", "right")
    seta(d, sg[0], sg[1], x, 720, dupla=False)
    return d.svg()


def prancha7():
    d = Desenho(LARG, 960)
    ref = referencia(d, 40, 95, 380, "T15 · Área do prestador (protótipo 6)")
    t19 = Tela("T19", "Disponibilidade", 40, 220, 470, [
        ("texto", "Marque os dias e turnos em que você atende:", 13, False, True, "#444"),
        ("disp",),
        ("secao", "Indisponibilidade temporária (ex.: férias)"),
        ("par", [("De:", "campo", 30, 140, "dd/mm/aaaa"), ("Até:", "campo", 38, 140,
                                                           "dd/mm/aaaa")]),
        ("botoes", ["Salvar", "Voltar"]),
    ]).desenhar(d)
    t20 = Tela("T20", "Solicitações recebidas", 570, 220, 790, [
        ("par", [("Estado:", "combo", 60, 170, "Pendentes"),
                 ("Ordenar por:", "combo", 92, 190, "Mais recentes")]),
        ("grade", ["Data", "Cliente", "Serviço", "Data desejada", "Turno", "Endereço",
                   "Estado"], 4, [0.9, 1.3, 1.3, 1.1, 0.8, 1.5, 0.9]),
        ("botoes", ["Ver detalhes", "Aceitar", "Recusar", "Registrar conclusão", "Cancelar",
                    "Voltar"]),
    ]).desenhar(d)
    t21 = Tela("T21", "Avaliações recebidas", 40, 600, 580, [
        ("grade", ["Data", "Cliente", "Nota", "Comentário", "Anexos", "Resposta"], 4,
         [0.8, 1.1, 0.6, 1.8, 0.8, 1.5]),
        ("botoes", ["Responder", "Denunciar", "Voltar"]),
    ]).desenhar(d)
    alerta(d, 60, t19.y + t19.h + 14, 280, ["ALERTA: Disponibilidade salva!"])
    y0 = t20.y + t20.h + 42
    alerta(d, 650, y0, 240, [], botoes=["Confirmar", "Voltar"],
           campos=[("Observação:", "campo", None)])
    alerta(d, 650, y0 + 98, 240, ["ALERTA: Solicitação aceita!", "Contatos liberados."])
    alerta(d, 900, y0, 225, [], botoes=["Confirmar", "Voltar"],
           campos=[("Motivo:", "combo", "Fora da área")])
    alerta(d, 900, y0 + 98, 225, ["ALERTA: Solicitação", "recusada."])
    alerta(d, 1135, y0, 225, ["ALERTA: Confirma que o", "serviço foi realizado?"],
           botoes=["Sim", "Não"])
    alerta(d, 1135, y0 + 104, 225, ["ALERTA: Conclusão", "registrada. Aguardando",
                                     "confirmação do cliente."])
    yr = t21.y + t21.h + 26
    alerta(d, 40, yr, 330, [], botoes=["Publicar", "Cancelar"],
           campos=[("Resposta:", "area", None)])
    alerta(d, 390, yr, 230, ["ALERTA: Resposta publicada!"])
    alerta(d, 390, yr + 50, 230, ["ALERTA: Esta avaliação", "já foi respondida."])
    seta(d, *ref["bottom"], *t19.a("top", 0.4), rotulo="Disponibilidade")
    seta(d, *ref["right"], *t20.a("top", 0.55), rotulo="Solicitações recebidas")
    ac, rc, rg = t20.btn("Aceitar"), t20.btn("Recusar"), t20.btn("Registrar conclusão")
    seta(d, ac[0], ac[1], 770, y0, dupla=False)
    seta(d, rc[0], rc[1], 1012, y0, dupla=False)
    seta(d, rg[0], rg[1], 1220, y0, dupla=False)
    rp = t21.btn("Responder", "bottom")
    seta(d, rp[0], rp[1], 200, yr, dupla=False)
    return d.svg()


def prancha8():
    d = Desenho(LARG, 980)
    t22 = Tela("T22", "Menu do administrador", 140, 100, 560, [
        ("menu", ["Denúncias", "Categorias", "Sair"]),
    ]).desenhar(d)
    t23 = Tela("T23", "Denúncias", 40, 270, 430, [
        ("combo", "Situação:", "Pendentes"),
        ("grade", ["Data", "Tipo", "Motivo", "Denunciado", "Situação"], 5,
         [0.9, 0.9, 1.1, 1.2, 1]),
        ("botoes", ["Analisar", "Voltar"]),
    ], lw=80).desenhar(d)
    t24 = Tela("T24", "Analisar denúncia", 40, 600, 430, [
        ("info", "Data:", "dd/mm/aaaa"), ("info", "Motivo:", "Conteúdo ofensivo"),
        ("info", "Descrição:", "..."), ("info", "Denunciante:", "Nome"),
        ("info", "Denunciado:", "Nome"),
        ("info", "Conteúdo denunciado:", "texto do perfil ou avaliação"),
        ("combo", "Medida:", "Arquivar"), ("area", "Justificativa:", 2),
        ("botoes", ["Registrar decisão", "Voltar"]),
    ], lw=80).desenhar(d)
    alerta(d, 540, 700, 320, ["ALERTA: Confirma a medida?"], botoes=["Sim", "Não"])
    alerta(d, 540, 800, 320, ["ALERTA: Decisão registrada.", "Envolvidos notificados."])
    seta(d, *t22.btn("Denúncias", "bottom"), *t23.a("top", 0.5), rotulo="Denúncias")
    seta(d, *t23.btn("Analisar", "bottom"), *t24.a("top", 0.7), rotulo="Analisar")
    yb = t24.marcas["Registrar decisão"][1] + 13
    seta(d, t24.x + t24.w, yb, 540, 735, dupla=False)
    return d.svg()


def prancha9():
    d = Desenho(LARG, 860)
    ref = referencia(d, 120, 90, 440, "T22 · Menu do administrador (protótipo 8)")
    t25 = Tela("T25", "Categorias", 40, 220, 600, [
        ("grade", ["Ícone", "Nome", "Situação"], 4, [0.6, 2, 1]),
        ("botoes", ["Nova", "Editar", "Excluir", "Voltar"], "esquerda"),
    ]).desenhar(d)
    t26 = Tela("T26", "Categoria", 40, 560, 400, [
        ("campo", "Nome:"), ("arquivo", "Ícone:", "Escolher..."),
        ("combo", "Situação:", "Ativa"),
        ("botoes", ["Salvar", "Voltar"]),
    ], lw=80, titulo_dir=True).desenhar(d)
    xa = 460
    alerta(d, xa, 420, 220, ["ALERTA: Confirma", "exclusão?"], botoes=["Sim", "Não"])
    alerta(d, xa, 524, 220, ["ALERTA: Categoria", "excluída."])
    alerta(d, xa, 592, 220, ["ALERTA: Categoria com", "serviços: desative-a", "em Editar."])
    alerta(d, xa, 679, 220, ["ALERTA: Categoria salva!"])
    alerta(d, xa, 728, 220, ["ALERTA: Já existe categoria", "com este nome."])
    seta(d, *ref["bottom"], *t25.a("top", 0.5), rotulo="Categorias")
    a, b = t25.btn("Nova", "bottom"), t25.btn("Editar", "bottom")
    seta(d, a[0], a[1], a[0], t26.y)
    seta(d, b[0], b[1], b[0], t26.y, rotulo="Nova / Editar")
    e = t25.btn("Excluir", "bottom")
    seta(d, e[0], e[1], xa + 30, 420, dupla=False)
    return d.svg()


PRANCHAS = [
    ("prancha1", "Acesso ao sistema", ["T01", "T02", "T03", "T04", "T05"], prancha1),
    ("prancha2", "Busca de prestadores", ["T06", "T07", "T08"], prancha2),
    ("prancha3", "Solicitar serviço e denunciar conteúdo", ["T09", "T10"], prancha3),
    ("prancha4", "Minha conta", ["T11"], prancha4),
    ("prancha5", "Acompanhamento das solicitações (cliente)", ["T12", "T13", "T14"], prancha5),
    ("prancha6", "Área do prestador: perfil e serviços", ["T15", "T16", "T17", "T18"], prancha6),
    ("prancha7", "Área do prestador: disponibilidade e atendimento", ["T19", "T20", "T21"],
     prancha7),
    ("prancha8", "Administração: moderação de denúncias", ["T22", "T23", "T24"], prancha8),
    ("prancha9", "Administração: categorias", ["T25", "T26"], prancha9),
]

TELAS = {
    "T01": "Login", "T02": "Cadastro de usuário", "T03": "Confirmação de e-mail",
    "T04": "Recuperar senha", "T05": "Redefinir senha", "T06": "Menu principal",
    "T07": "Buscar prestadores", "T08": "Perfil do prestador", "T09": "Solicitar serviço",
    "T10": "Denunciar conteúdo", "T11": "Minha conta", "T12": "Minhas solicitações",
    "T13": "Detalhes da solicitação", "T14": "Avaliar prestador", "T15": "Área do prestador",
    "T16": "Perfil de prestador", "T17": "Meus serviços", "T18": "Serviço",
    "T19": "Disponibilidade", "T20": "Solicitações recebidas", "T21": "Avaliações recebidas",
    "T22": "Menu do administrador", "T23": "Denúncias", "T24": "Analisar denúncia",
    "T25": "Categorias", "T26": "Categoria",
}


