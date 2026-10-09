# -*- coding: utf-8 -*-
"""
Conteúdo da Fase 2 (Análise de Pontos de Função) do Bicus.

Fonte única dos dados da contagem. O gerar.py calcula a complexidade de cada função a partir
das quantidades de AR/TR e TD (tabelas da aula de APF), soma os pontos e produz o .docx
integrado à F1, os .md de revisão e as pranchas de protótipos.

Cada TD é listado pelo nome, para que a contagem possa ser conferida item a item contra os
protótipos (pasta prototipos/). Os códigos de tela (T01...T29) estão em prototipos.py.
"""

# ---------------------------------------------------------------------------
# Modelo conceitual revisado (base das funções de dados)
# ---------------------------------------------------------------------------
# Revisão do modelo preliminar da Concepção contra os RF/NF, os suplementares, a tabela de
# conceitos, as consultas e as telas. A seção da F1 continua com o modelo preliminar entregue.
# Atributos: "nome: Tipo [multiplicidade]"; "/" = atributo derivado (armazenado).

MODELO_CLASSES = {
    "Usuário": ["nome: String", "email: String", "senha: String", "cpf: String",
                "telefone: String", "dataNascimento: Data", "endereco: Endereço",
                "localizacao: Coordenada", "fotoPerfil: Imagem [0..1]",
                "dataAceiteTermos: Data", "situacao: Enumeração", "fimSuspensao: Data [0..1]"],
    "Prestador": ["apresentacao: String", "localBase: Endereço [0..1]",
                  "localizacaoBase: Coordenada", "raioDeslocamento: Real [0..1]",
                  "disponibilidade: GradeSemanal", "inicioIndisponibilidade: Data [0..1]",
                  "fimIndisponibilidade: Data [0..1]", "portfolio: Imagem [0..10]",
                  "ativo: Booleano", "dataCadastro: Data", "/notaMedia: Real",
                  "/totalAvaliacoes: Inteiro"],
    "Serviço": ["titulo: String", "descricao: String", "precoMinimo: Moeda",
                "precoMaximo: Moeda", "unidadeCobranca: Enumeração", "ativo: Booleano"],
    "Categoria": ["nome: String", "icone: Imagem [0..1]", "situacao: Enumeração"],
    "Solicitação": ["descricao: String", "dataDesejada: Data", "turno: Enumeração",
                    "endereco: Endereço", "estado: Enumeração", "dataCriacao: Data",
                    "observacao: String [0..1]", "motivoRecusa: Enumeração [0..1]",
                    "canceladaPor: Enumeração [0..1]", "motivoCancelamento: String [0..1]",
                    "dataRegistroConclusao: Data [0..1]", "dataConclusao: Data [0..1]",
                    "valorCobrado: Moeda [0..1]"],
    "Avaliação": ["nota: Inteiro", "comentario: String [0..1]", "anexos: Imagem [0..*]",
                  "data: Data", "resposta: String [0..1]", "removida: Booleano"],
    "Denúncia": ["motivo: Enumeração", "descricao: String [0..1]", "data: Data",
                 "situacao: Enumeração", "medida: Enumeração [0..1]",
                 "justificativa: String [0..1]", "dataDecisao: Data [0..1]"],
    "Administrador": ["nome: String", "email: String", "senha: String"],
}

# (subclasse, superclasse)
MODELO_HERANCA = [("Prestador", "Usuário")]

# Associações: a classe "de" guarda a chave estrangeira "fk" para a classe "para".
MODELO_ASSOCIACOES = [
    dict(de="Solicitação", m_de="0..*", para="Usuário", m_para="1", rotulo="solicita",
         fk="cliente"),
    dict(de="Solicitação", m_de="0..*", para="Serviço", m_para="1", rotulo="referente a",
         fk="servico"),
    dict(de="Serviço", m_de="0..*", para="Prestador", m_para="1", rotulo="oferece",
         fk="prestador"),
    dict(de="Serviço", m_de="0..*", para="Categoria", m_para="1", rotulo="classificado em",
         fk="categoria"),
    dict(de="Avaliação", m_de="0..1", para="Solicitação", m_para="1", rotulo="origina",
         fk="solicitacao"),
    dict(de="Denúncia", m_de="0..*", para="Usuário", m_para="1", rotulo="registra",
         fk="denunciante"),
    dict(de="Denúncia", m_de="0..*", para="Usuário", m_para="1", rotulo="denuncia",
         fk="denunciado"),
    dict(de="Denúncia", m_de="0..*", para="Avaliação", m_para="0..1", rotulo="denuncia",
         fk="avaliacaoDenunciada"),
    dict(de="Denúncia", m_de="0..*", para="Administrador", m_para="0..1",
         rotulo="analisada por", fk="administrador"),
]

# Tipos compostos e domínios das enumerações: (tipo ou Classe.atributo, valores, requisitos)
MODELO_TIPOS = [
    ("Endereço", "logradouro, número, complemento, bairro, cidade, CEP",
     "NF1.3, NF4.2, F10, consulta 1"),
    ("Coordenada", "latitude, longitude", "F7"),
    ("GradeSemanal", "dias da semana × turnos (manhã, tarde, noite)", "F6 (NF6.1)"),
    ("Usuário.situacao", "aguardando confirmação, ativa, suspensa, banida, excluída",
     "NF1.8, NF2.1, NF3.5, F19"),
    ("Serviço.unidadeCobranca", "por hora, por diária, por serviço", "NF5.3"),
    ("Categoria.situacao", "pendente, ativa, desativada", "NF20.2, NF20.5"),
    ("Solicitação.turno", "manhã, tarde, noite", "F11, NF6.1"),
    ("Solicitação.estado", "pendente, aceita, recusada, expirada, cancelada, concluída",
     "NF13.1"),
    ("Solicitação.motivoRecusa",
     "sem disponibilidade, fora da área de atendimento, serviço não realizado", "NF12.1"),
    ("Solicitação.canceladaPor", "cliente, prestador, sistema", "NF11.6, NF13.4, NF19.3"),
    ("Denúncia.motivo", "lista pré-definida", "NF18.1"),
    ("Denúncia.situacao", "pendente, arquivada, procedente", "F19"),
    ("Denúncia.medida", "remover avaliação, advertir, suspender, banir", "F19"),
]

# Alterações em relação ao modelo preliminar da Concepção: (alteração, requisitos)
MODELO_ALTERACOES = [
    ("Prestador passa a ser subclasse de Usuário (herança), no lugar da associação "
     "\"atua como\".", "F1, F4 (NF4.1)"),
    ("Usuário: + senha.", "F1, F2, F3, S5"),
    ("Usuário: + dataAceiteTermos.", "NF1.7, S4"),
    ("Usuário: ativo (Booleano) → situacao (enumeração); + fimSuspensao.",
     "NF1.8, NF2.1, NF3.5, F19 (NF19.3)"),
    ("Prestador: raioAtendimento → raioDeslocamento; notaMedia e totalAvaliacoes marcados "
     "como derivados (/).", "NF4.3, F15"),
    ("Solicitação: + canceladaPor.", "NF11.6, NF13.4, NF19.3, consulta 4"),
    ("Solicitação: + dataRegistroConclusao (registro do prestador, antes da confirmação do "
     "cliente).", "F13 (NF13.2)"),
    ("Avaliação: + removida (a remoção por moderação mantém o registro ligado à denúncia).",
     "F19 (NF19.2, NF19.4)"),
    ("Denúncia: sempre ligada ao usuário denunciado (dono do perfil ou autor da avaliação); "
     "ligada à avaliação só quando ela é o item denunciado.", "F18, F19 (NF19.5)"),
    ("Administrador: + senha.", "F2"),
    ("Associação \"mantém\" (Administrador–Categoria) removida: a categoria não guarda quem "
     "a mantém.", "F20"),
    ("Multiplicidades e atributos opcionais ([0..1]) indicados; tipos compostos e "
     "enumerações detalhados.", "—"),
]

# ---------------------------------------------------------------------------
# Funções de dados
# ---------------------------------------------------------------------------
# ALI: um por classe do modelo revisado. TD e TR são calculados pelo gerar.py a partir do
# modelo (atributos próprios + FKs; herança soma TR), para a tabela não divergir do desenho.

ALI = [
    dict(cod="ALI01", nome="Usuário", origem="F1, F2, F3, F7, F19"),
    dict(cod="ALI02", nome="Prestador", origem="F4, F6, F7, F15"),
    dict(cod="ALI03", nome="Serviço", origem="F5"),
    dict(cod="ALI04", nome="Categoria", origem="F5, F20"),
    dict(cod="ALI05", nome="Solicitação", origem="F11, F12, F13, F17"),
    dict(cod="ALI06", nome="Avaliação", origem="F14, F15, F16, F19"),
    dict(cod="ALI07", nome="Denúncia", origem="F18, F19"),
    dict(cod="ALI08", nome="Administrador", origem="F2, F19, F20"),
]

AIE = [
    dict(cod="AIE01", nome="Geocodificação", tr=1,
         origem="F7 — base de endereços da API externa",
         td=["endereço", "latitude", "longitude"]),
]

# ---------------------------------------------------------------------------
# Funções de transação
# ---------------------------------------------------------------------------
# rf: requisitos de origem ("nav" = navegação; "Conceitos" = CRUD de Administrador da tabela
# de conceitos da F1, sem RF próprio; "Consulta n" = consultas da F1).

_VOLTAR = ["botão Voltar"]

EE = [
    dict(cod="EE01", nome="Entrar no sistema", telas=["T01"], rf=["F2"],
         ar=["Usuário", "Administrador"],
         td=["e-mail", "senha", "botão Entrar", "mensagem de erro"]),
    dict(cod="EE02", nome="Cadastrar usuário", telas=["T01", "T02"], rf=["F1", "F7"],
         ar=["Usuário", "Geocodificação"],
         td=["botão Criar conta", "nome completo", "e-mail", "senha", "CPF", "telefone",
             "data de nascimento", "endereço", "complemento", "foto de perfil",
             "aceite dos termos", "botão Cadastrar", "botão Voltar", "mensagem de sucesso",
             "mensagem de erro"]),
    dict(cod="EE03", nome="Confirmar e-mail", telas=["T03"], rf=["F1", "F3"],
         ar=["Usuário"],
         td=["mensagem de confirmação", "botão Ir para o login"]),
    dict(cod="EE04", nome="Solicitar recuperação de senha", telas=["T01", "T04"], rf=["F2"],
         ar=["Usuário"],
         td=["botão Esqueci minha senha", "e-mail", "botão Enviar link", "botão Voltar",
             "mensagem de envio"]),
    dict(cod="EE05", nome="Redefinir senha", telas=["T05"], rf=["F2"], ar=["Usuário"],
         td=["nova senha", "confirmação da senha", "botão Salvar senha",
             "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE06", nome="Menu principal", telas=["T06"], rf=["nav"], ar=[],
         td=["Buscar prestadores", "Minhas solicitações", "Minha conta", "Área do prestador",
             "Sair"]),
    dict(cod="EE07", nome="Fechar Buscar prestadores", telas=["T07"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE08", nome="Fechar Perfil do prestador", telas=["T08"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE09", nome="Solicitar serviço", telas=["T08", "T09"], rf=["F11"],
         ar=["Solicitação", "Serviço", "Usuário"],
         td=["botão Solicitar serviço", "serviço", "descrição da necessidade", "data desejada",
             "turno", "endereço do serviço", "botão Enviar solicitação", "botão Voltar",
             "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE10", nome="Denunciar conteúdo", telas=["T08", "T10", "T21"], rf=["F18"],
         ar=["Denúncia"],
         td=["botão Denunciar (perfil ou avaliação)", "motivo", "descrição",
             "botão Enviar denúncia", "botão Cancelar", "mensagem de sucesso",
             "mensagem de erro"]),
    dict(cod="EE11", nome="Editar dados da conta", telas=["T11"], rf=["F3", "F7"],
         ar=["Usuário", "Geocodificação"],
         td=["nome", "e-mail", "telefone", "endereço", "complemento", "foto de perfil",
             "botão Salvar alterações", "botão Voltar", "mensagem de sucesso",
             "mensagem de confirmação do novo e-mail"]),
    dict(cod="EE12", nome="Alterar senha", telas=["T11"], rf=["F3"], ar=["Usuário"],
         td=["botão Alterar senha", "senha atual", "nova senha", "botão Salvar",
             "botão Cancelar", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE13", nome="Excluir conta", telas=["T11"], rf=["F3"],
         ar=["Usuário", "Prestador", "Solicitação", "Serviço"],
         td=["botão Excluir conta", "mensagem de confirmação", "botão Sim", "botão Não",
             "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE14", nome="Cancelar solicitação", telas=["T12", "T20"], rf=["F11", "F13"],
         ar=["Solicitação"],
         td=["botão Cancelar", "solicitação selecionada", "motivo do cancelamento",
             "botão Confirmar", "botão Voltar", "mensagem de sucesso"]),
    dict(cod="EE15", nome="Confirmar conclusão do serviço", telas=["T12"], rf=["F13"],
         ar=["Solicitação", "Usuário"],
         td=["botão Confirmar conclusão", "solicitação selecionada", "mensagem de confirmação",
             "valor cobrado", "botão Sim", "botão Não", "mensagem de sucesso"]),
    dict(cod="EE16", nome="Fechar Minhas solicitações", telas=["T12"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE17", nome="Abrir conversa no WhatsApp", telas=["T13"], rf=["F12"], ar=[],
         td=["botão Abrir WhatsApp"]),
    dict(cod="EE18", nome="Fechar Detalhes da solicitação", telas=["T13"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE19", nome="Avaliar prestador", telas=["T12", "T14"], rf=["F14", "F15"],
         ar=["Avaliação", "Solicitação", "Serviço", "Prestador"],
         td=["botão Avaliar", "nota", "comentário", "anexos", "botão Enviar avaliação",
             "botão Voltar", "mensagem de sucesso"]),
    dict(cod="EE20", nome="Menu da área do prestador", telas=["T15"], rf=["nav"], ar=[],
         td=["Perfil de prestador", "Meus serviços", "Disponibilidade",
             "Solicitações recebidas", "Avaliações recebidas", "Voltar"]),
    dict(cod="EE21", nome="Cadastrar perfil de prestador", telas=["T16"], rf=["F4", "F7"],
         ar=["Prestador", "Usuário", "Geocodificação"],
         td=["apresentação", "local base", "usar o endereço da conta",
             "raio de deslocamento", "portfólio", "botão Salvar", "botão Voltar",
             "mensagem de sucesso"]),
    dict(cod="EE22", nome="Editar perfil de prestador", telas=["T16"], rf=["F4", "F7"],
         ar=["Prestador", "Usuário", "Geocodificação"],
         td=["apresentação", "local base", "usar o endereço da conta",
             "raio de deslocamento", "portfólio", "botão Salvar", "botão Voltar",
             "mensagem de sucesso"]),
    dict(cod="EE23", nome="Desativar perfil de prestador", telas=["T16"], rf=["F4"],
         ar=["Prestador", "Solicitação", "Serviço"],
         td=["botão Desativar perfil", "mensagem de confirmação", "botão Sim", "botão Não",
             "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE24", nome="Cadastrar serviço", telas=["T17", "T18"], rf=["F5"],
         ar=["Serviço"],
         td=["botão Novo", "categoria", "título", "descrição", "preço mínimo", "preço máximo",
             "unidade de cobrança", "botão Salvar", "botão Voltar", "mensagem de sucesso",
             "mensagem de erro"]),
    dict(cod="EE25", nome="Editar serviço", telas=["T17", "T18"], rf=["F5"], ar=["Serviço"],
         td=["botão Editar", "serviço selecionado", "categoria", "título", "descrição",
             "preço mínimo", "preço máximo", "unidade de cobrança", "botão Salvar",
             "botão Voltar", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE26", nome="Excluir serviço", telas=["T17"], rf=["F5"],
         ar=["Serviço", "Solicitação"],
         td=["botão Excluir", "serviço selecionado", "mensagem de confirmação", "botão Sim",
             "botão Não", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE27", nome="Fechar Meus serviços", telas=["T17"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE28", nome="Sugerir categoria", telas=["T18"], rf=["F20"], ar=["Categoria"],
         td=["botão Sugerir nova categoria", "nome da categoria", "botão Enviar",
             "botão Cancelar", "mensagem de sucesso"]),
    dict(cod="EE29", nome="Definir disponibilidade", telas=["T19"], rf=["F6"],
         ar=["Prestador"],
         td=["dias da semana", "turnos", "início da indisponibilidade",
             "fim da indisponibilidade", "botão Salvar", "botão Voltar",
             "mensagem de sucesso"]),
    dict(cod="EE30", nome="Aceitar solicitação", telas=["T20"], rf=["F12"],
         ar=["Solicitação", "Usuário"],
         td=["botão Aceitar", "solicitação selecionada", "observação", "botão Confirmar",
             "botão Voltar", "mensagem de sucesso"]),
    dict(cod="EE31", nome="Recusar solicitação", telas=["T20"], rf=["F12"],
         ar=["Solicitação", "Usuário"],
         td=["botão Recusar", "solicitação selecionada", "motivo da recusa", "botão Confirmar",
             "botão Voltar", "mensagem de sucesso"]),
    dict(cod="EE32", nome="Registrar conclusão do serviço", telas=["T20"], rf=["F13"],
         ar=["Solicitação", "Usuário"],
         td=["botão Registrar conclusão", "solicitação selecionada", "mensagem de confirmação",
             "botão Sim", "botão Não", "mensagem de sucesso"]),
    dict(cod="EE33", nome="Fechar Solicitações recebidas", telas=["T20"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE34", nome="Responder avaliação", telas=["T21"], rf=["F16"], ar=["Avaliação"],
         td=["botão Responder", "avaliação selecionada", "resposta", "botão Publicar",
             "botão Cancelar", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE35", nome="Fechar Avaliações recebidas", telas=["T21"], rf=["nav"], ar=[],
         td=_VOLTAR),
    dict(cod="EE36", nome="Menu do administrador", telas=["T22"], rf=["nav"], ar=[],
         td=["Denúncias", "Categorias", "Sair"]),
    dict(cod="EE37", nome="Registrar decisão de moderação", telas=["T23", "T24"],
         rf=["F19", "F15"],
         ar=["Denúncia", "Avaliação", "Usuário", "Prestador", "Solicitação", "Serviço"],
         td=["botão Analisar", "denúncia selecionada", "medida", "justificativa",
             "botão Registrar decisão", "botão Voltar", "mensagem de confirmação", "botão Sim",
             "botão Não", "mensagem de sucesso"]),
    dict(cod="EE38", nome="Fechar Denúncias", telas=["T23"], rf=["nav"], ar=[], td=_VOLTAR),
    dict(cod="EE39", nome="Cadastrar categoria", telas=["T25", "T26"], rf=["F20"],
         ar=["Categoria"],
         td=["botão Nova", "nome", "ícone", "situação", "botão Salvar", "botão Voltar",
             "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE40", nome="Editar categoria", telas=["T25", "T26"], rf=["F20"],
         ar=["Categoria"],
         td=["botão Editar", "categoria selecionada", "nome", "ícone", "situação",
             "botão Salvar", "botão Voltar", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE41", nome="Excluir categoria", telas=["T25"], rf=["F20"],
         ar=["Categoria", "Serviço"],
         td=["botão Excluir", "categoria selecionada", "mensagem de confirmação", "botão Sim",
             "botão Não", "mensagem de sucesso", "mensagem de erro"]),
    dict(cod="EE42", nome="Fechar Categorias", telas=["T25"], rf=["nav"], ar=[], td=_VOLTAR),
    dict(cod="EE43", nome="Expirar solicitações não respondidas (automático)", telas=[],
         rf=["F11"], ar=["Solicitação", "Usuário"],
         td=["data e hora da verificação", "estado da solicitação", "notificação ao cliente"]),
]

CE = [
    dict(cod="CE01", nome="Combo de categorias", oculta=True, telas=["T07", "T18"],
         rf=["F5", "F8"], ar=["Categoria"], td=["nome da categoria"]),
    dict(cod="CE02", nome="Combo de serviços do prestador", oculta=True, telas=["T09"],
         rf=["F11"], ar=["Serviço"], td=["título do serviço"]),
    dict(cod="CE03", nome="Carregar dados da conta", oculta=True, telas=["T11"], rf=["F3"],
         ar=["Usuário"],
         td=["nome", "e-mail", "telefone", "endereço", "complemento", "foto de perfil", "CPF",
             "data de nascimento"]),
    dict(cod="CE04", nome="Consultar minhas solicitações", oculta=False, telas=["T12"],
         rf=["F17"], ar=["Solicitação", "Serviço", "Usuário"],
         td=["filtro por estado", "ordenação", "data", "serviço", "prestador",
             "data desejada", "turno", "estado", "valor cobrado"]),
    dict(cod="CE05", nome="Consultar detalhes da solicitação", oculta=False,
         telas=["T12", "T13", "T20"], rf=["F17", "F12"],
         ar=["Solicitação", "Serviço", "Usuário"],
         td=["serviço", "prestador ou cliente", "telefone", "descrição", "data desejada",
             "turno", "endereço", "estado", "observação", "motivo de recusa ou cancelamento",
             "valor cobrado"]),
    dict(cod="CE06", nome="Carregar perfil de prestador", oculta=True, telas=["T16"],
         rf=["F4"], ar=["Prestador"],
         td=["apresentação", "local base", "raio de deslocamento", "portfólio"]),
    dict(cod="CE07", nome="Listar meus serviços", oculta=False, telas=["T17"], rf=["F5"],
         ar=["Serviço", "Categoria"],
         td=["categoria", "título", "preço mínimo", "preço máximo", "unidade de cobrança"]),
    dict(cod="CE08", nome="Carregar serviço para edição", oculta=True, telas=["T18"],
         rf=["F5"], ar=["Serviço", "Categoria"],
         td=["categoria", "título", "descrição", "preço mínimo", "preço máximo",
             "unidade de cobrança"]),
    dict(cod="CE09", nome="Carregar disponibilidade", oculta=True, telas=["T19"], rf=["F6"],
         ar=["Prestador"],
         td=["dias da semana", "turnos", "início da indisponibilidade",
             "fim da indisponibilidade"]),
    dict(cod="CE10", nome="Consultar solicitações recebidas", oculta=False, telas=["T20"],
         rf=["F17", "F12"], ar=["Solicitação", "Serviço", "Usuário"],
         td=["filtro por estado", "ordenação", "data", "cliente", "serviço", "data desejada",
             "turno", "endereço", "estado"]),
    dict(cod="CE11", nome="Consultar avaliações recebidas", oculta=False, telas=["T21"],
         rf=["F16"], ar=["Avaliação", "Solicitação", "Serviço", "Usuário"],
         td=["data", "cliente", "nota", "comentário", "anexos", "resposta"]),
    dict(cod="CE12", nome="Consultar denúncias", oculta=False, telas=["T23"], rf=["F19"],
         ar=["Denúncia", "Usuário"],
         td=["filtro por situação", "data", "tipo", "motivo", "denunciado", "situação"]),
    dict(cod="CE13", nome="Carregar denúncia para análise", oculta=True, telas=["T24"],
         rf=["F19"], ar=["Denúncia", "Usuário", "Avaliação", "Prestador"],
         td=["data", "motivo", "descrição", "denunciante", "denunciado",
             "conteúdo denunciado"]),
    dict(cod="CE14", nome="Listar categorias", oculta=False, telas=["T25"], rf=["F20"],
         ar=["Categoria"], td=["ícone", "nome", "situação"]),
    dict(cod="CE15", nome="Carregar categoria para edição", oculta=True, telas=["T26"],
         rf=["F20"], ar=["Categoria"], td=["nome", "ícone", "situação"]),
]

SE = [
    dict(cod="SE01", nome="Buscar prestadores por categoria", telas=["T07"],
         rf=["F8", "F9", "F7"],
         ar=["Serviço", "Prestador", "Usuário", "Categoria", "Geocodificação"],
         td=["categoria", "raio de busca", "endereço de partida", "preço máximo (filtro)",
             "nota mínima (filtro)", "dia (filtro)", "turno (filtro)", "foto", "prestador",
             "serviço", "preço mínimo", "preço máximo", "nota média", "nº de avaliações",
             "distância (derivado)", "mensagem de nenhum resultado"],
         derivados="distância calculada e ordenação pela pontuação de recomendação (F9)"),
    dict(cod="SE02", nome="Visualizar perfil do prestador", telas=["T08"], rf=["F10"],
         ar=["Prestador", "Usuário", "Serviço", "Categoria", "Avaliação", "Solicitação"],
         td=["foto", "nome", "bairro e cidade", "distância (derivado)", "nota média",
             "nº de avaliações", "serviços concluídos (derivado)", "apresentação",
             "distribuição das notas (derivado)", "categoria do serviço", "título do serviço",
             "descrição do serviço", "preço mínimo", "preço máximo", "unidade de cobrança",
             "dias e turnos disponíveis", "indisponível até", "portfólio", "filtro por nota",
             "data da avaliação", "nota da avaliação", "comentário", "anexos",
             "resposta do prestador"],
         derivados="distância, contagem de serviços concluídos e distribuição das notas"),
    dict(cod="SE03", nome="Relatório: prestadores mais bem avaliados por categoria e cidade",
         telas=[], rf=["Consulta 1"],
         ar=["Prestador", "Usuário", "Serviço", "Categoria"],
         td=["categoria (filtro)", "cidade (filtro)", "posição no ranking (derivado)",
             "prestador", "categoria", "cidade", "nota média", "nº de avaliações"],
         derivados="posição no ranking"),
    dict(cod="SE04", nome="Relatório: categorias mais solicitadas por período",
         telas=[], rf=["Consulta 2"], ar=["Solicitação", "Serviço", "Categoria"],
         td=["data inicial", "data final", "categoria", "quantidade de solicitações (derivado)",
             "percentual do total (derivado)"],
         derivados="contagem e percentual"),
    dict(cod="SE05", nome="Relatório: serviços concluídos por prestador por mês",
         telas=[], rf=["Consulta 3"],
         ar=["Solicitação", "Serviço", "Usuário", "Avaliação"],
         td=["data inicial", "data final", "prestador", "mês",
             "quantidade de serviços concluídos (derivado)", "nota média do mês (derivado)"],
         derivados="contagem e média por mês"),
    dict(cod="SE06", nome="Relatório: taxa de aceitação e de cancelamento por prestador",
         telas=[], rf=["Consulta 4"],
         ar=["Solicitação", "Serviço", "Usuário"],
         td=["data inicial", "data final", "prestador", "solicitações recebidas (derivado)",
             "aceitas (derivado)", "canceladas (derivado)", "taxa de aceitação (derivado)",
             "taxa de cancelamento (derivado)"],
         derivados="contagens e taxas percentuais"),
    dict(cod="SE07", nome="Relatório: novos prestadores por categoria e período",
         telas=[], rf=["Consulta 5"], ar=["Prestador", "Serviço", "Categoria"],
         td=["data inicial", "data final", "categoria (filtro)", "categoria",
             "quantidade de novos prestadores (derivado)"],
         derivados="contagem"),
    dict(cod="SE08", nome="Relatório: denúncias por motivo e situação no período",
         telas=[], rf=["Consulta 6"], ar=["Denúncia"],
         td=["data inicial", "data final", "motivo", "situação",
             "quantidade de denúncias (derivado)"],
         derivados="contagem"),
]

# ---------------------------------------------------------------------------
# Critérios de contagem adotados (lista curta de decisões; sem explicar o método)
# ---------------------------------------------------------------------------

CRITERIOS = [
    "Fronteira: interfaces web e mobile e servidor do Bicus. A API de geocodificação e o serviço "
    "de e-mail ficam fora da fronteira.",
    "ALI: um por classe do modelo conceitual revisado. TD = atributos próprios da classe + "
    "chaves estrangeiras das associações (FK); tipo composto (Endereço, Coordenada, "
    "GradeSemanal) conta 1 TD. TR = 1, exceto na herança: Usuário (com a subclasse) e "
    "Prestador (com a superclasse) têm TR = 2.",
    "AIE: base de endereços da API de geocodificação (F7).",
    "AR: ALIs e AIE gravados ou lidos pela função, inclusive leituras exigidas por requisitos "
    "(validações como NF3.5, NF4.5, NF5.5 e NF20.2; e-mail do destinatário de notificações; "
    "coordenadas da AIE). Atributo herdado é lido do ALI Usuário. Item escolhido em combo não "
    "conta AR na EE (o combo é CE oculta).",
    "EE: TD inclui o botão que abre o formulário, os botões do formulário, o item selecionado "
    "na grade e as mensagens com seus botões; mensagem de erro só quando exigida por um "
    "requisito.",
    "Menus e botões Voltar de telas de listagem: EE sem AR. Voltar de formulário: TD da EE do "
    "formulário.",
    "CE: TD inclui os filtros e a ordenação. Combos que carregam dados e formulários "
    "pré-preenchidos: CE oculta.",
    "SE: funções com dados derivados (marcados com \"derivado\" na lista de TD).",
    "Função acionada de mais de uma tela: contada uma vez.",
    "Requisitos ocultos F7, F9 e F15: contados dentro das funções que os disparam. Expiração "
    "automática de solicitações (NF11.7): EE sem tela.",
    "Requisitos desejáveis incluídos.",
]

# ---------------------------------------------------------------------------
# Características gerais do sistema (fator de ajuste): (nome, NI, justificativa curta)
# ---------------------------------------------------------------------------

CGS = [
    ("Comunicação de dados", 5,
     "On-line (web e app) com mais de um protocolo: HTTPS (servidor e API de geocodificação) e "
     "SMTP (e-mails, NF1.8 e NF11.4)."),
    ("Processamento distribuído", 4,
     "Cliente (navegador ou app) e servidor, com transferência on-line nas duas direções."),
    ("Performance", 1,
     "Requisitos de desempenho definidos (NF7.2, NF11.5, NF15.1), sem ação especial."),
    ("Configuração altamente utilizada", 1,
     "Hospedagem em nuvem (S8), restrições leves."),
    ("Volume de transações", 0,
     "Sem picos previstos nos requisitos."),
    ("Entrada de dados on-line", 5,
     "Todas as transações são on-line."),
    ("Eficiência do usuário final", 4,
     "Mais de cinco itens (menus, navegação, rolagem, mouse/toque, pop-ups, destaques visuais) e "
     "requisitos de usabilidade (NF7.4, NF8.5, NF12.4, NF20.5)."),
    ("Atualização on-line", 3,
     "Maioria dos ALIs atualizada on-line; sem requisito de backup."),
    ("Complexidade de processamento", 3,
     "Segurança (S4, S5, NF18.3, NF19.1), lógica extensa (estados da solicitação, moderação) e "
     "cálculo (distância e pontuação, F8 e F9)."),
    ("Reutilização", 1,
     "Reúso apenas dentro da aplicação (web e mobile)."),
    ("Facilidade de instalação", 1,
     "Procedimentos de implantação: carga de categorias (NF20.4) e primeiro administrador."),
    ("Facilidade de operação", 1,
     "Processo digital, sem papel; sem rotinas de salva e recuperação definidas."),
    ("Múltiplos locais", 3,
     "Navegadores em computador e smartphone (S1) e app Android/iOS (S2)."),
    ("Facilidade de mudanças", 3,
     "Relatórios com filtros (1 item); categorias mantidas on-line com efeito imediato (2 itens)."),
]

# ---------------------------------------------------------------------------
# Estimativas de esforço, prazo e custo
# ---------------------------------------------------------------------------

MARGEM = 0.30          # margem de segurança sobre o PFB (diretriz da aula)
HORAS_MES = 130        # horas por pessoa por mês (6,5 h/dia x 20 dias úteis)
EQUIPE = 3             # integrantes do grupo
VALOR_HORA = 45.00     # referência da aula
LUCRO = 0.20

EXTRAS_FIXOS = [
    ("Domínio (1 ano)", 40.00),
]
EXTRAS_MENSAIS = [
    ("Hospedagem em nuvem", 300.00),
    ("Internet e energia da equipe (3 × R$ 150,00)", 450.00),
]

CENARIOS = [
    dict(nome="Referência LABD2M", hpf=0.28, adotado=False),
    dict(nome="Otimista", hpf=6.5, adotado=False),
    dict(nome="Realista", hpf=9.25, adotado=True),
    dict(nome="Pessimista", hpf=12.0, adotado=False),
]

# Critério da produtividade (coluna "Critério" da tabela de parâmetros; os demais critérios são
# montados no gerador a partir dos valores acima)
CRITERIO_PRODUTIVIDADE = (
    "Ponto médio da faixa de 6,5 a 12 h/PF das linguagens orientadas a objeto (tabela da aula), "
    "considerando Python e JavaScript; a equipe não tem dados históricos.")

PLANEJAMENTO_F1_HORAS = 1600   # 4 ciclos de 400 h do planejamento preliminar da F1
EQUIPES_ALTERNATIVAS = [2, 3, 4, 5, 6]
