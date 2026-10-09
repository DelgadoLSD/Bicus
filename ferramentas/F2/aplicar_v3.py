# -*- coding: utf-8 -*-
"""
Aplica a rodada de 09/10/2026 sobre o .docx editado pelo grupo, sem regerar o documento.

Uso:  python aplicar_v3.py <docx do grupo> <docx de saída>

Troca só o que mudou: as figuras dos protótipos (e os títulos "Prancha" -> "Protótipo"), a
seção "Funções de dados" (modelo revisado, alterações, tipos e tabela de ALIs) e as tabelas
calculadas (EE, CE, SE, PFB, PFA e estimativas). O resto do documento fica como o grupo deixou
(capa, F1, critérios removidos, tabela de características sem justificativa etc.).
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar as G2  # noqa: E402

G1, C2, P = G2.G1, G2.C2, G2.P


def texto_de(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def corpo(doc):
    return list(doc.element.body.iterchildren())


def paragrafo_titulo(doc, texto, inicio=False):
    for p in doc.paragraphs:
        estilo = p.style.name if p.style is not None else ""
        t = p.text.strip()
        if ("Heading" in estilo or "Título" in estilo or "Ttulo" in p.style.style_id) and \
                (t.startswith(texto) if inicio else t == texto):
            return p
    raise LookupError(f"título não encontrado: {texto}")


def proximos(el, tag, n=1):
    """Os n próximos irmãos com a tag dada, parando no próximo título."""
    achados = []
    for irmao in el.itersiblings():
        if irmao.tag == qn("w:p") and irmao.find(qn("w:pPr")) is not None:
            st = irmao.find(qn("w:pPr")).find(qn("w:pStyle"))
            if st is not None and ("Heading" in st.get(qn("w:val")) or
                                   "tulo" in st.get(qn("w:val"))):
                break
        if irmao.tag == qn(tag):
            achados.append(irmao)
            if len(achados) == n:
                break
    if len(achados) < n:
        raise LookupError(f"{tag} não encontrado depois de '{texto_de(el)[:40]}'")
    return achados


def com_imagem(el):
    for irmao in el.itersiblings():
        if irmao.tag == qn("w:p") and list(irmao.iter(qn("w:drawing"))):
            return irmao
    raise LookupError("imagem não encontrada")


def trocar_texto(p, novo):
    runs = p.runs
    runs[0].text = novo
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def trocar_imagem(doc, p_el, png, largura_cm):
    from docx.text.paragraph import Paragraph
    p = Paragraph(p_el, doc._body)
    rids = [b.get(qn("r:embed")) for b in p_el.iter(qn("a:blip"))]
    for r in list(p_el.findall(qn("w:r"))):
        p_el.remove(r)
    p.add_run().add_picture(str(png), width=Cm(largura_cm))
    # python-docx reaproveita a mesma parte de imagem se o arquivo for idêntico: só remove a
    # relação antiga se nenhuma imagem do documento a usa mais
    em_uso = {b.get(qn("r:embed")) for b in doc.element.body.iter(qn("a:blip"))}
    for rid in set(rids) - em_uso:
        del doc.part.rels[rid]


def mover_para_antes(novos, ref):
    for el in novos:
        ref.addprevious(el)


def ultimo_do_corpo(doc):
    """Último elemento antes do sectPr (onde python-docx acrescenta tabelas e parágrafos)."""
    return corpo(doc)[-2]


def substituir_tabela(doc, antiga, construir):
    construir()
    nova = ultimo_do_corpo(doc)
    assert nova.tag == qn("w:tbl")
    antiga.addprevious(nova)
    antiga.getparent().remove(antiga)
    return nova


def novo_espaco(doc, pts=10):
    return G1.espaco(doc, pts)._p


def main(entrada, saida):
    doc = Document(entrada)
    m = G2.medicao()
    G2.validar(m)
    pngs = G2.gerar_prototipos()
    png_modelo = G2.gerar_modelo()

    # --- Protótipos: o título da seção ficou com uma quebra de página manual quando o índice das
    # pranchas foi apagado no Word; sem ela o título fica na mesma página do Protótipo 1 ---
    h1 = paragrafo_titulo(doc, "Protótipos das telas")
    for br in list(h1._p.iter(qn("w:br"))):
        if br.get(qn("w:type")) == "page":
            br.getparent().remove(br)

    # --- Protótipos: novas figuras e "Prancha" -> "Protótipo" ---
    for i, (nome, titulo, telas, _) in enumerate(P.PRANCHAS, 1):
        h = paragrafo_titulo(doc, f"Prancha {i} —", inicio=True)
        faixa = telas[0] if len(telas) == 1 else f"{telas[0]} a {telas[-1]}"
        trocar_texto(h, f"Protótipo {i} — {titulo} ({faixa})")
        png, w, hh = pngs[nome]
        # o protótipo 1 divide a página com o título da seção
        trocar_imagem(doc, com_imagem(h._p), png, min(23.5 if i == 1 else 25.5, 14.6 * w / hh))

    # --- Funções de dados: modelo revisado, alterações, tipos e ALIs ---
    h = paragrafo_titulo(doc, "Funções de dados (ALI e AIE)")
    from docx.text.paragraph import Paragraph
    fonte = Paragraph(proximos(h._p, "w:p")[0], doc._body)
    trocar_texto(fonte, G2.TXT_DADOS)
    trocar_imagem(doc, com_imagem(h._p), png_modelo, 16.5)
    tab_ali = proximos(h._p, "w:tbl")[0]
    G2.tabela_lista(doc, [12.0, 5.0], ["Alteração em relação ao modelo preliminar", "Requisitos"],
                    C2.MODELO_ALTERACOES)
    t_alt = ultimo_do_corpo(doc)
    e1 = novo_espaco(doc)
    G2.tabela_lista(doc, [4.2, 8.6, 4.2], ["Tipo composto ou enumeração", "Valores", "Requisitos"],
                    C2.MODELO_TIPOS)
    t_tipos = ultimo_do_corpo(doc)
    e2 = novo_espaco(doc)
    mover_para_antes([t_alt, e1, t_tipos, e2], tab_ali)
    substituir_tabela(doc, tab_ali, lambda: G2.tabela_dados(doc, m))

    # --- Transações, PFB e PFA ---
    for tipo, titulo in (("EE", "Entradas Externas (EE)"), ("CE", "Consultas Externas (CE)"),
                         ("SE", "Saídas Externas (SE)")):
        t = proximos(paragrafo_titulo(doc, titulo)._p, "w:tbl")[0]
        substituir_tabela(doc, t, lambda tipo=tipo: G2.tabela_transacoes(doc, m, tipo))
    t = proximos(paragrafo_titulo(doc, "Pontos de função brutos")._p, "w:tbl")[0]
    substituir_tabela(doc, t, lambda: G2.tabela_pfb(doc, m))
    t = proximos(paragrafo_titulo(doc, "Pontos de função ajustados")._p, "w:tbl")[0]
    substituir_tabela(doc, t, lambda: G2.tabela_calculo(doc, G2.calc_pfa(m)))

    # --- Estimativas ---
    a = G2.adotado(m)

    def parametros():
        t = G1.nova_tabela(doc, [3.4, 4.2, 9.4])
        G2.cabecalho(t, ["Parâmetro", "Valor", "Critério"])
        for par, val, crit in G2.parametros(m):
            row = G1.nova_linha(t)
            G1.escrever(row.cells[0], [(par, True)], size=9)
            G1.escrever(row.cells[1], val, size=9)
            G1.escrever(row.cells[2], crit, size=9)
        G1.manter_junto(t)

    def cenarios():
        t = G1.nova_tabela(doc, [4.4, 1.8, 2.3, 1.9, 2.4, 4.2])
        G2.cabecalho(t, ["Cenário", "h/PF", "Esforço (h)", "H/M", "Prazo (meses)", "Preço"])
        for c in C2.CENARIOS:
            e = G2.estimativa(m["pfa"], c["hpf"])
            row = G1.nova_linha(t)
            G1.escrever(row.cells[0], [(c["nome"] + (" (adotado)" if c["adotado"] else ""),
                                        c["adotado"])], size=9)
            for k, v in enumerate([G2.fmt(c["hpf"]), G2.fmt(e["esforco"], 0), G2.fmt(e["hm"]),
                                   G2.fmt(e["prazo"]), G2.rs(e["preco"])], 1):
                G1.escrever(row.cells[k], [(v, c["adotado"])], WD_ALIGN_PARAGRAPH.CENTER, size=9)
            if c["adotado"]:
                G2.sombrear_linha(row, "E8F4F6")
        G1.manter_junto(t)

    def equipes():
        t = G1.nova_tabela(doc, [4.0, 4.0])
        G2.cabecalho(t, ["Equipe", "Prazo (meses)"])
        for n in C2.EQUIPES_ALTERNATIVAS:
            row = G1.nova_linha(t)
            d = n == C2.EQUIPE
            G1.escrever(row.cells[0], [(f"{n} pessoas", d)], WD_ALIGN_PARAGRAPH.CENTER, size=9)
            G1.escrever(row.cells[1], [(G2.fmt(G2.r2(a["hm"] / n)), d)],
                        WD_ALIGN_PARAGRAPH.CENTER, size=9)
        G1.manter_junto(t)

    t = proximos(paragrafo_titulo(doc, "Parâmetros")._p, "w:tbl")[0]
    substituir_tabela(doc, t, parametros)
    t = proximos(paragrafo_titulo(doc, "Cenários")._p, "w:tbl")[0]
    substituir_tabela(doc, t, cenarios)
    calc, equipe = proximos(paragrafo_titulo(doc, "Projeção adotada (cenário realista)")._p,
                            "w:tbl", 2)
    substituir_tabela(doc, calc, lambda: G2.tabela_calculo(doc, G2.calc_projecao(m)))
    substituir_tabela(doc, equipe, equipes)
    comp = Paragraph(proximos(paragrafo_titulo(
        doc, "Comparação com o planejamento preliminar")._p, "w:p")[0], doc._body)
    trocar_texto(comp, G2.txt_comparacao(m))

    sobra = [p.text for p in doc.paragraphs if "prancha" in p.text.lower()]
    assert not sobra, sobra
    doc.save(saida)
    print("Salvo:", saida)
    print(f"PFB {m['pfb']} | PFA {m['pfa']} | realista {G2.fmt(a['esforco'], 0)} h, "
          f"{G2.fmt(a['prazo'])} meses, {G2.rs(a['preco'])}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
