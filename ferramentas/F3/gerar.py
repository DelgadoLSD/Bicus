# -*- coding: utf-8 -*-
"""
Gera o documento da F3 (processo de desenvolvimento customizado) do Bicus.

Uso:  python gerar.py   -> desenha as figuras em saida/ e cria o .docx em
      D:/UFV/Bicus/F3 - Processo de Desenvolvimento/ (só se ainda não existir: depois que o grupo
      editar o documento, alterações são aplicadas sobre o arquivo deles, sem regerar).
"""
import importlib.util
import sys
from pathlib import Path

import pymupdf
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

AQUI = Path(__file__).resolve().parent
F1_GER = AQUI.parent / "F1"
SAIDA = AQUI / "saida"
PASTA = AQUI.parent.parent / "F3 - Processo de Desenvolvimento"
DOCX = PASTA / "Bicus - F3 Processo de Desenvolvimento.docx"

sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(F1_GER))
_spec = importlib.util.spec_from_file_location("gerar_f1", F1_GER / "gerar.py")
G1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G1)
import diagrama as D  # noqa: E402

# ---------------------------------------------------------------------------------------
# Conteúdo (texto simples, sem tabelas nem imagens: pedido do grupo em 06/11/2026)
# ---------------------------------------------------------------------------------------

# Tempos verbais: passado para o que já foi feito (F1 e F2), futuro para o que ainda será feito.
INTRO = (
    "Para a construção do Bicus, definimos um processo próprio que combina elementos de "
    "diferentes métodos: as fases iniciais do RUP; o quadro e o fluxo contínuo do Kanban; a "
    "programação em par, os testes automatizados e a integração contínua do XP; e as histórias "
    "de usuário e o acompanhamento diário inspirados no Scrum. Como o Bicus é uma proposta do "
    "nosso próprio grupo e não há um cliente externo, nós três atuaremos juntos como Product "
    "Owner (PO) e como desenvolvedores, sem outros papéis formais.")

SECOES = [
    ("Concepção e Elaboração", [
        "Nosso processo começou pelas fases de Concepção e Elaboração do RUP, que correspondem às "
        "entregas F1 e F2. Na Concepção, levantamos os requisitos funcionais e não funcionais, "
        "especificamos os casos de uso e elaboramos o modelo conceitual preliminar. Na "
        "Elaboração, fizemos os protótipos das telas principais, que serviram de base para a "
        "análise de pontos de função, com a qual medimos o tamanho do sistema e estimamos o "
        "esforço, o prazo e o custo do projeto.",
        "Para concluir a Elaboração, usaremos um elemento do Kanban: transformaremos os "
        "requisitos funcionais em histórias de usuário, cada uma com critérios de aceitação e com "
        "a indicação do requisito que a originou, e as organizaremos no backlog do quadro Kanban.",
    ]),
    ("Construção", [
        "Não dividiremos a construção em sprints. O trabalho seguirá um fluxo contínuo, "
        "organizado em um quadro Kanban, no GitHub Projects ou no Trello, com as colunas "
        "Backlog, Fazendo, Testes e Pronto. Sempre que um de nós ficar livre, puxará a próxima "
        "história do backlog. Para evitar sobrecarga, cada um terá no máximo uma tarefa em "
        "andamento.",
        "Desenvolveremos as histórias mais complexas em par, de modo que a revisão do código "
        "aconteça durante a própria implementação. As mais simples serão feitas individualmente "
        "e revisadas por outro integrante. Junto com o código, escreveremos testes automatizados, "
        "executados a cada envio ao repositório por meio de integração contínua.",
        "Se algum de nós travar por um impedimento durante o trabalho em uma história, "
        "registraremos um cartão de impedimento no quadro, trataremos o problema registrando a "
        "resolução no mesmo cartão e, depois de resolvido, retomaremos a implementação.",
        "Na coluna Testes, verificaremos a história pelos testes e pelos seus critérios de "
        "aceitação; se algo não estiver de acordo, ela voltará para Fazendo. A história só irá "
        "para Pronto quando os critérios tiverem sido conferidos, os testes passarem e o código "
        "estiver integrado à versão principal do projeto.",
        "Acompanharemos o andamento por um check-in diário por mensagem, em que cada um de nós "
        "informará o que fez, o que vai fazer e se está travado. Em seguida, conferiremos o "
        "quadro, incluindo os impedimentos em aberto, e ajustaremos a ordem do backlog quando "
        "necessário.",
    ]),
    ("Entrega", [
        "Quando todas as histórias estiverem prontas, faremos os testes finais do sistema "
        "completo e o publicaremos, em uma única entrega ao fim do projeto.",
    ]),
]

MPS_INTRO = "Nosso processo atenderá a três resultados esperados do nível G do MPS.BR."
MPS = [
    ("GRE3 – Rastreabilidade bidirecional entre requisitos e produtos de trabalho. ",
     "Cada história de usuário registrará o requisito funcional que a originou, e nossos commits "
     "e testes farão referência à história que implementam. Assim, conseguiremos partir de um "
     "requisito e chegar ao código e aos testes correspondentes, e também fazer o caminho "
     "inverso."),
    ("GRE4 – Revisões para identificar e corrigir inconsistências em relação aos requisitos. ",
     "Revisaremos todo o código, durante a programação em par ou com a ajuda de outro "
     "integrante, e na coluna Testes conferiremos a história com os seus critérios de aceitação, "
     "que derivam dos requisitos. Quando houver divergência, a história voltará para correção."),
    ("GPR16 – Registro e tratamento dos problemas identificados. ",
     "Quando algum de nós travar durante o trabalho em uma história, registraremos o impedimento "
     "em um cartão no quadro, com a descrição do problema e a história afetada, e anotaremos no "
     "mesmo cartão a análise e a resolução. Os impedimentos em aberto serão acompanhados por "
     "todos no check-in diário, quando conferirmos o quadro."),
]

# ---------------------------------------------------------------------------------------
# Figuras (ficam em saida/ e na pasta da F3, fora do documento) e documento
# ---------------------------------------------------------------------------------------


def gerar_figuras():
    SAIDA.mkdir(exist_ok=True)
    for nome, svg in (("processo", D.diagrama_processo()), ("quadro_kanban", D.quadro_kanban())):
        (SAIDA / f"{nome}.svg").write_text(svg, encoding="utf-8")
        pymupdf.open(str(SAIDA / f"{nome}.svg"))[0].get_pixmap(
            dpi=200 if nome == "processo" else 150).save(str(SAIDA / f"{nome}.png"))


def gerar_docx():
    doc = Document()
    G1.modo_atual(doc)
    for z in doc.settings.element.iter(G1.qn("w:zoom")):
        z.set(G1.qn("w:percent"), "100")
    G1.configurar_estilos(doc)
    G1.margens(doc.sections[0])
    G1.rodape(doc)
    G1.capa(doc, fases=("Fase 3 – Processo de Desenvolvimento Customizado",))

    G1.h1(doc, "Processo de desenvolvimento customizado")
    G1.paragrafo(doc, INTRO)
    for titulo, paragrafos in SECOES:
        G1.h2(doc, titulo)
        for texto in paragrafos:
            G1.paragrafo(doc, texto)
    G1.h2(doc, "Atendimento ao MPS.BR nível G")
    G1.paragrafo(doc, MPS_INTRO)
    for prefixo, texto in MPS:
        G1.paragrafo(doc, texto, prefixo)

    doc.core_properties.title = "Bicus – Processo de Desenvolvimento Customizado (F3)"
    doc.core_properties.author = ", ".join(n for n, _ in G1.C.EQUIPE)
    PASTA.mkdir(exist_ok=True)
    doc.save(str(DOCX))
    print("Word:", DOCX)


if __name__ == "__main__":
    gerar_figuras()
    if DOCX.exists() and "--sobrescrever" not in sys.argv:
        sys.exit(f"{DOCX.name} já existe (pode ter edições do grupo); use --sobrescrever.")
    gerar_docx()
