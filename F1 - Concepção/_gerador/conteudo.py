# -*- coding: utf-8 -*-
"""
Conteúdo do documento de Concepção (F1) do Bicus.

Este arquivo é a ÚNICA fonte do conteúdo. O script gerar.py lê estes dados e produz:
  - o documento Word (.docx) no formato do Exemplo_Concepção;
  - os arquivos .md de revisão (um por seção);
  - os diagramas (casos de uso e modelo conceitual).

SINCRONIZADO em 08/10/2026 com o `Bicus - F1 Concepção.docx` editado à mão pelo
Luis Felipe (commit 920619c, 02/10/2026). A partir de agora o fluxo de trabalho é:
Claude gera com `gerar.py` -> o grupo revisa e ajusta à mão no Word se precisar.

Convenções dos requisitos não-funcionais (NF) e suplementares (S):
  (nome, restrição, categoria, desejável, permanente)
  desejável  = True  -> "(X)" na coluna Desejável  (False = obrigatório)
  permanente = True  -> "(X)" na coluna Permanente (False = transitório)
Os códigos NFx.y e Sx são numerados automaticamente pela ordem das listas.
"""

SISTEMA = "Bicus"
SUBTITULO = "Marketplace online de bicos e pequenos serviços locais"
EQUIPE = [
    ("Hugo Costa Araújo", "112684"),
    ("Lucas Silva Delgado", "112685"),
    ("Luis Felipe Martins Pereira", "112710"),
]

# Metadados usados só nas propriedades do arquivo (autor/título), não aparecem mais na capa
# (a capa foi simplificada em 02/10/2026 - ver ARQUIVADO no fim do arquivo).
DISCIPLINA = "INF323 – Engenharia de Software II"
PROFESSOR = "Prof. Lucas Francisco da Matta Vegi"
INSTITUICAO = "Universidade Federal de Viçosa"
DATA = "Setembro de 2026"

# ---------------------------------------------------------------------------
# REQUISITOS FUNCIONAIS
# ---------------------------------------------------------------------------
# Cada item: cod, nome, oculto, desc, nfs=[(nome, restrição, categoria, desejável, permanente)]

RF = [
    dict(cod='F1', nome='Cadastrar usuário', oculto=False,
         desc='O sistema deverá conter uma tela de cadastro onde solicitará os dados do usuário, tais como: nome completo, e-mail, senha, CPF, telefone, data de nascimento, endereço e foto de perfil. Todo usuário cadastrado pode contratar serviços como cliente e, posteriormente, ativar um perfil de prestador (F4).',
         nfs=[
             ('Validação do CPF', 'O sistema deve validar os dígitos verificadores do CPF. Caso não seja válido, o sistema deverá avisar o usuário e interromper o cadastro.',
              'Segurança', False, True),
             ('Dados obrigatórios', 'O sistema deve associar obrigatoriamente à conta: nome completo, e-mail, senha, CPF, telefone, data de nascimento e endereço.',
              'Segurança', False, True),
             ('Dados opcionais', 'O sistema deve associar opcionalmente à conta: foto de perfil e complemento do endereço.',
              'Interface', False, True),
             ('Unicidade da conta', 'Não poderá existir mais de uma conta com o mesmo CPF ou com o mesmo e-mail.',
              'Segurança', False, True),
             ('Idade mínima', 'A data de nascimento deve indicar idade igual ou superior a 18 anos; caso contrário, o sistema deverá avisar o usuário e interromper o cadastro.',
              'Legal', False, True),
             ('Política de senha', 'A senha deve ter no mínimo 8 caracteres, com ao menos uma letra e um número.',
              'Segurança', False, False),
             ('Termos de uso e privacidade', 'O cadastro só será concluído após o aceite dos Termos de Uso e da Política de Privacidade.',
              'Legal', False, True),
             ('Confirmação de e-mail', 'O sistema enviará um link de confirmação para o e-mail informado. A conta só é ativada após a confirmação.',
              'Segurança', True, True),
         ]),

    dict(cod='F2', nome='Login', oculto=False,
         desc='O sistema irá conter uma tela de login que solicitará o e-mail e a senha do usuário.',
         nfs=[
             ('Permissão de acesso', 'O usuário só terá acesso ao sistema caso esteja cadastrado, com conta ativa e a senha digitada corresponda à senha cadastrada.',
              'Segurança', False, True),
             ('Recuperação de senha', 'O usuário poderá redefinir a senha por meio de um link enviado ao e-mail cadastrado.',
              'Usabilidade', False, True),
         ]),

    dict(cod='F3', nome='Editar dados da conta de usuário', oculto=False,
         desc='Os usuários poderão alterar alguns dados da conta, como nome, telefone, endereço, foto de perfil, e-mail e senha, e também solicitar a exclusão da conta.',
         nfs=[
             ('Dados não alteráveis', 'As informações de CPF e data de nascimento não poderão ser alteradas.',
              'Segurança', False, True),
             ('Alteração de e-mail', 'A alteração do e-mail exige nova confirmação pelo novo endereço.',
              'Segurança', True, True),
             ('Alteração de senha', 'Para alterar a senha, o usuário deve informar a senha atual.',
              'Segurança', False, True),
             ('Atualização da localização', 'Ao alterar o endereço, o sistema deve recalcular as coordenadas geográficas do usuário.',
              'Usabilidade', False, True),
             ('Exclusão da conta', 'O usuário pode solicitar a exclusão da conta. As avaliações já feitas permanecerão, sem identificação do autor. Não é possível excluir a conta com solicitações em andamento.',
              'Legal', False, True),
         ]),

    dict(cod='F4', nome='Cadastrar perfil de prestador', oculto=False,
         desc='O sistema deverá permitir que um usuário cadastrado ative um perfil de prestador, informando uma apresentação profissional, o local base de atendimento (caso exista) e, opcionalmente, fotos de trabalhos já realizados.',
         nfs=[
             ('Conta única', 'O perfil de prestador fica vinculado à conta do usuário, que continua podendo contratar serviços como cliente.',
              'Segurança', False, True),
             ('Privacidade do endereço', 'O endereço completo do prestador nunca é exibido publicamente. Apenas bairro, cidade e distância aproximada.',
              'Segurança', False, True),
             ('Raio de deslocamento', 'O prestador pode definir a distância máxima (em km) que aceita se deslocar. Clientes fora desse raio não o encontrarão nas buscas.',
              'Configurabilidade', True, False),
             ('Portfólio', 'O prestador pode adicionar até 10 fotos de trabalhos realizados.',
              'Implementação', True, False),
             ('Desativação do perfil', 'O prestador pode desativar o perfil e deixar de aparecer nas buscas. Não é possível desativá-lo com solicitações em andamento.',
              'Usabilidade', False, True),
         ]),

    dict(cod='F5', nome='Gerenciar serviços oferecidos', oculto=False,
         desc='O prestador poderá cadastrar, editar e remover os serviços que oferece, informando para cada um: categoria, título, descrição, faixa de preço (valor mínimo e máximo) e unidade de cobrança.',
         nfs=[
             ('Seleção de categoria', 'A categoria deve ser escolhida em uma lista pré-definida e não digitada livremente.',
              'Interface', False, True),
             ('Faixa de preço', 'Os valores devem ser informados em reais com valor mínimo menor ou igual ao valor máximo.',
              'Interface', False, True),
             ('Unidade de cobrança', 'A unidade de cobrança será escolhida entre: por hora, por diária ou por serviço.',
              'Configurabilidade', False, False),
             ('Um serviço por categoria', 'O prestador pode ter no máximo um serviço em cada categoria, evitando que apareça repetido nos resultados de uma busca.',
              'Configurabilidade', False, False),
             ('Remoção de serviço', 'Um serviço com solicitações em andamento não pode ser removido.',
              'Configurabilidade', False, True),
         ]),

    dict(cod='F6', nome='Definir disponibilidade', oculto=False,
         desc='O prestador poderá informar os dias da semana e turnos em que costuma atender, bem como marcar períodos de indisponibilidade temporária (ex.: férias).',
         nfs=[
             ('Grade semanal', 'A disponibilidade é informada marcando os dias da semana e os turnos (manhã, tarde e noite) de atendimento.',
              'Interface', True, True),
             ('Indisponibilidade temporária', 'Durante um período marcado como indisponível, o prestador não aparece nas buscas.',
              'Usabilidade', True, True),
             ('Exibição no perfil', 'A grade de disponibilidade é exibida no perfil do prestador.',
              'Interface', True, True),
         ]),

    dict(cod='F7', nome='Obter localização geográfica', oculto=True,
         desc='O sistema obtém as coordenadas geográficas dos usuários: para prestadores, a partir do endereço base de atendimento. Para clientes, a partir do endereço cadastrado.',
         nfs=[
             ('Obtenção de coordenadas', 'A conversão de endereço em coordenadas será feita por uma API externa de geocodificação.',
              'Implementação', False, False),
             ('Armazenamento das coordenadas', 'As coordenadas dos prestadores são calculadas uma única vez, no cadastro ou na alteração do endereço, e armazenadas, evitando geocodificar a cada busca.',
              'Desempenho', False, True),
             ('Endereço não localizado', 'Caso o endereço não seja localizado pela API, o sistema deve avisar o usuário e permitir ajustar a posição em um mapa.',
              'Usabilidade', True, False),
             ('Outro ponto de partida', 'O cliente pode buscar a partir de outro endereço ou CEP sem alterar o seu cadastro.',
              'Usabilidade', True, True),
         ]),

    dict(cod='F8', nome='Buscar prestadores por categoria', oculto=False,
         desc='O cliente seleciona uma categoria de serviço e o sistema identifica todos os prestadores com serviço ativo nessa categoria dentro de um raio de distância configurável a partir da localização do cliente, exibindo uma lista ordenada pela combinação de proximidade geográfica e nota média das avaliações (F9).',
         nfs=[
             ('Raio configurável', 'O cliente define o raio de busca.',
              'Configurabilidade', False, False),
             ('Cálculo da distância', 'A distância é calculada em linha reta entre as coordenadas do cliente e do prestador.',
              'Implementação', False, False),
             ('Prestadores exibidos', 'Não são exibidos na lista: o próprio usuário, prestadores com perfil excluído ou prestadores em período de indisponibilidade e prestadores cujo raio de deslocamento não alcança o cliente.',
              'Usabilidade', False, True),
             ('Informações da lista', 'Cada item exibe: nome e foto do prestador, título do serviço, faixa de preço, nota média (estrelas), quantidade de avaliações e distância aproximada.',
              'Interface', False, True),
             ('Nenhum resultado', 'Caso nenhum prestador seja encontrado no raio, o sistema informa o cliente e sugere ampliar o raio de busca.',
              'Usabilidade', True, True),
             ('Filtros adicionais', 'A lista pode ser filtrada por faixa de preço, nota mínima e disponibilidade (dia e turno).',
              'Configurabilidade', True, True),
             ('Visualização em mapa', 'O cliente pode alternar entre a lista e um mapa com a posição aproximada dos prestadores encontrados.',
              'Interface', True, False),
         ]),

    dict(cod='F9', nome='Calcular pontuação de recomendação', oculto=True,
         desc='Para cada prestador encontrado na busca, o sistema calcula uma pontuação que combina a proximidade geográfica e a nota do prestador. Essa pontuação define a ordem da lista de resultados.',
         nfs=[
             ('Fórmula de pontuação', 'Fórmula a definir. Mas atribuirá um peso maior para a pontuação em relação à proximidade geográfica.',
              'Especificação', False, False),
             ('Critério de desempate', 'Em caso de empate, aparece primeiro o prestador com mais serviços concluídos e, depois, o mais próximo.',
              'Especificação', True, False),
         ]),

    dict(cod='F10', nome='Visualizar perfil do prestador', oculto=False,
         desc='O cliente poderá acessar o perfil de um prestador, que exibe: nome, foto, apresentação, serviços oferecidos (categoria, descrição, faixa de preço e unidade de cobrança), disponibilidade, bairro e cidade, distância aproximada, nota média, quantidade de avaliações, quantidade de serviços concluídos, avaliações recebidas e portfólio.',
         nfs=[
             ('Privacidade do contato', 'O telefone do prestador só é exibido ao cliente depois que o prestador aceitar uma solicitação dele.',
              'Segurança', False, False),
             ('Lista de avaliações', 'As avaliações são exibidas das mais recentes para as mais antigas e podem ser filtradas por nota.',
              'Configurabilidade', True, True),
             ('Distribuição das notas', 'O perfil exibe a quantidade de avaliações recebidas em cada nota (1 a 5 estrelas).',
              'Interface', True, False),
         ]),

    dict(cod='F11', nome='Solicitar serviço', oculto=False,
         desc='O cliente poderá enviar uma solicitação de serviço a um prestador, escolhendo um dos serviços oferecidos e informando a descrição da necessidade, a data e o turno desejados e o endereço onde o serviço será realizado.',
         nfs=[
             ('Dados da solicitação', 'São obrigatórios: serviço escolhido, descrição da necessidade, data desejada e turno.',
              'Interface', False, True),
             ('Data válida', 'A data desejada deve ser igual ou posterior à data atual.',
              'Interface', False, True),
             ('Autossolicitação', 'O usuário não pode enviar solicitação ao seu próprio perfil de prestador.',
              'Segurança', False, True),
             ('Notificação ao prestador', 'Ao ser criada a solicitação, o prestador recebe uma notificação por e-mail.',
              'Interface', True, True),
             ('Limite de solicitações pendentes', 'Cada cliente pode ter no máximo 10 solicitações pendentes (sem resposta) ao mesmo tempo, evitando envios em massa.',
              'Desempenho', True, False),
             ('Cancelamento pelo cliente', 'O cliente pode cancelar a solicitação enquanto ela estiver pendente, sem necessidade de justificativa.',
              'Usabilidade', False, True),
             ('Expiração', 'Solicitações não respondidas em 72 horas expiram automaticamente.',
              'Usabilidade', True, False),
         ]),

    dict(cod='F12', nome='Responder solicitação', oculto=False,
         desc='O prestador poderá aceitar ou recusar as solicitações recebidas. Ao aceitar, pode fazer observações em relação ao serviço que será prestado.',
         nfs=[
             ('Motivo da recusa', 'Ao recusar, o prestador pode selecionar um motivo (ex.: sem disponibilidade, fora da área de atendimento, serviço não realizado).',
              'Usabilidade', True, True),
             ('Notificação ao cliente', 'O cliente é notificado da resposta do prestador.',
              'Interface', True, True),
             ('Liberação dos contatos', 'Após o aceite, cliente e prestador passam a visualizar o telefone um do outro para combinar os detalhes.',
              'Segurança', False, True),
             ('Atalho para WhatsApp', 'O sistema oferece um botão que abre a conversa no WhatsApp com o contato liberado.',
              'Interface', True, False),
         ]),

    dict(cod='F13', nome='Concluir serviço', oculto=False,
         desc='Após a realização do serviço, o prestador registra a conclusão da solicitação e o cliente confirma que o serviço foi realizado. A conclusão confirmada habilita a avaliação do prestador (F14). Antes da conclusão, a solicitação aceita pode ser cancelada por qualquer uma das partes.',
         nfs=[
             ('Estados da solicitação', 'Uma solicitação pode estar nos estados: Pendente, Aceita, Recusada, Expirada, Cancelada e Concluída.',
              'Implementação', False, False),
             ('Confirmação do cliente', 'O serviço só é considerado concluído após a confirmação do cliente.',
              'Usabilidade', False, False),
             ('Valor final', 'Ao registrar a conclusão, o cliente pode informar o valor efetivamente cobrado.',
              'Usabilidade', True, True),
             ('Cancelamento', 'Cliente ou prestador podem cancelar uma solicitação aceita, informando o motivo. O cancelamento fica registrado no histórico de ambos.',
              'Segurança', False, True),
             ('Pedido de avaliação', 'Ao ser confirmada a conclusão, o cliente recebe uma notificação convidando-o a avaliar o prestador.',
              'Interface', False, True),
         ]),

    dict(cod='F14', nome='Avaliar prestador', oculto=False,
         desc='Após a conclusão de um serviço, o cliente poderá avaliar o prestador atribuindo uma nota de 1 a 5 estrelas e, opcionalmente, um comentário.',
         nfs=[
             ('Direito de avaliar', 'Somente o cliente de uma solicitação concluída pode avaliá-la, e cada solicitação admite uma única avaliação.',
              'Segurança', False, True),
             ('Escala da nota', 'A nota é um número inteiro de 1 a 5, selecionado por estrelas.',
              'Interface', False, True),
             ('Comentário', 'O comentário é opcional, assim como anexos.',
              'Interface', False, True),
             ('Prazo para avaliar', 'A avaliação pode ser feita em até 7 dias após a conclusão do serviço.',
              'Usabilidade', True, False),
         ]),

    dict(cod='F15', nome='Atualizar reputação do prestador', oculto=True,
         desc='A cada avaliação registrada, editada ou removida, o sistema recalcula a reputação do prestador (nota média e quantidade de avaliações), que passa a ser utilizada no processo de recomendação (F9).',
         nfs=[
             ('Atualização imediata', 'A reputação deve ser recalculada no momento em que a avaliação é registrada, editada ou removida.',
              'Desempenho', False, True),
         ]),

    dict(cod='F16', nome='Responder avaliação', oculto=False,
         desc='O prestador poderá publicar uma resposta a uma avaliação recebida, exibida logo abaixo dela no seu perfil.',
         nfs=[
             ('Resposta única', 'Cada avaliação admite uma única resposta do prestador.',
              'Interface', True, True),
         ]),

    dict(cod='F17', nome='Consultar histórico de solicitações', oculto=False,
         desc='Clientes e prestadores poderão consultar o histórico das solicitações enviadas e recebidas, com o estado de cada uma e os dados do serviço.',
         nfs=[
             ('Permissão de acesso', 'Cada usuário só visualiza as solicitações em que é o cliente ou o prestador.',
              'Segurança', False, True),
             ('Separação por papel', 'Usuários que também são prestadores visualizam separadamente os serviços que contrataram e os serviços que prestaram.',
              'Interface', False, True),
             ('Filtro por estado', 'O histórico pode ser filtrado pelo estado da solicitação.',
              'Configurabilidade', True, True),
             ('Ordenação do histórico', 'O histórico pode ser ordenado por data.',
              'Configurabilidade', True, True),
         ]),

    dict(cod='F18', nome='Denunciar conteúdo', oculto=False,
         desc='Qualquer usuário poderá denunciar um perfil de outro ou uma avaliação que considere inadequado, informando o motivo.',
         nfs=[
             ('Motivo da denúncia', 'O motivo é escolhido de uma lista pré-definida com descrição opcional.',
              'Interface', False, False),
             ('Denúncia única', 'Um usuário só pode denunciar o mesmo item uma vez.',
              'Segurança', False, True),
             ('Sigilo do denunciante', 'A identidade do denunciante não é revelada ao usuário denunciado.',
              'Segurança', False, True),
             ('Aviso ao administrador', 'Cada nova denúncia gera um aviso no painel do administrador.',
              'Interface', True, True),
         ]),

    dict(cod='F19', nome='Moderar denúncias', oculto=False,
         desc='O administrador analisa as denúncias recebidas e decide entre arquivá-las ou aplicar uma medida: remover a avaliação denunciada ou advertir, suspender ou banir o usuário.',
         nfs=[
             ('Acesso restrito', 'Apenas usuários com perfil de administrador podem acessar a moderação.',
              'Segurança', False, True),
             ('Remoção de avaliação', 'A remoção de uma avaliação dispara o recálculo da reputação do prestador.',
              'Implementação', False, True),
             ('Suspensão de usuário', 'Um usuário suspenso não consegue fazer login durante a suspensão. Se for prestador, deixa de aparecer nas buscas e suas solicitações pendentes são canceladas.',
              'Segurança', False, True),
             ('Registro das decisões', 'Toda decisão de moderação é registrada com data, administrador responsável e justificativa.',
              'Segurança', False, True),
             ('Notificação do resultado', 'O denunciante e o usuário denunciado são notificados da decisão, sem que o denunciante seja identificado.',
              'Interface', True, True),
         ]),

    dict(cod='F20', nome='Gerenciar categorias de serviço', oculto=False,
         desc='O administrador poderá cadastrar, editar e desativar as categorias de serviço disponíveis na plataforma (ex.: jardinagem, aulas particulares, faxina, etc).',
         nfs=[
             ('Nome único', 'Não podem existir duas categorias com o mesmo nome.',
              'Segurança', False, True),
             ('Exclusão de categoria', 'Uma categoria com serviços associados não pode ser excluída, apenas desativada. Categorias desativadas não aparecem nas buscas nem no cadastro de novos serviços.',
              'Especificação', False, True),
             ('Ícone da categoria', 'Cada categoria possui um ícone, exibido na tela de busca.',
              'Interface', True, True),
             ('Carga inicial', 'O sistema será implantado com as categorias: Jardinagem, Aulas particulares, Pequenos reparos domésticos, Faxina, Pintura, Montagem de móveis e Cuidado de animais.',
              'Implementação', False, False),
             ('Sugestão de categoria', 'Prestadores podem sugerir uma nova categoria, que fica pendente até a aprovação do administrador.',
              'Usabilidade', True, False),
         ]),
]

# ---------------------------------------------------------------------------
# REQUISITOS SUPLEMENTARES
# ---------------------------------------------------------------------------
# (nome, restrição (lista de parágrafos), categoria, desejável, permanente)

SUPLEMENTARES = [
    ('Interface web', ['O sistema terá uma interface web responsiva, que se adapta a telas de computadores e smartphones e pode ser usada pelo navegador, sem necessidade de instalação.'],
     'Interface', False, True),
    ('Aplicativo mobile', ['O sistema terá também um aplicativo nativo para smartphones (Android e iOS), com as mesmas funcionalidades da versão web.'],
     'Interface', True, False),
    ('Idade mínima', ['O sistema deve ser usado somente por maiores de 18 anos.'],
     'Legal', False, True),
    ('Proteção de dados pessoais', ['O tratamento de dados pessoais deve seguir a Lei Geral de Proteção de Dados: coleta apenas dos dados necessários, finalidade informada, consentimento e direito de acesso, correção e exclusão.'],
     'Legal', False, True),
    ('Segurança das senhas', ['As senhas são armazenadas apenas na forma de hash, com algoritmo próprio para senhas.'],
     'Segurança', False, True),
    ('Intermediação do serviço', ['A plataforma apenas aproxima clientes e prestadores: não processa pagamentos nem se responsabiliza pela execução do serviço. Preço e forma de pagamento são combinados diretamente entre as partes, conforme os Termos de Uso.'],
     'Legal', False, False),
    ('Idioma e formatos', ['Interface em português do Brasil; valores em reais, datas no formato dd/mm/aaaa e distâncias em quilômetros.'],
     'Interface', False, True),
    ('Distribuição', ['A versão web será hospedada em um serviço de nuvem.'],
     'Empacotamento', True, False),
]

# ---------------------------------------------------------------------------
# ORGANIZAÇÃO DOS REQUISITOS
# ---------------------------------------------------------------------------

# Casos de uso (processos de negócio: monossessão, interativos, resultado consistente)
CASOS_DE_USO = [
    dict(nome="Contratar serviço", atores=["Cliente"],
         desc="O cliente escolhe uma categoria e o raio de busca. O sistema obtém a localização do "
              "cliente e exibe os prestadores próximos, ordenados por proximidade e nota. O cliente "
              "compara as opções, acessa o perfil de um prestador e envia a ele uma solicitação de "
              "serviço.",
         refs=["F7", "F8", "F9", "F10", "F11"]),
    dict(nome="Responder solicitação", atores=["Prestador"],
         desc="O prestador analisa uma solicitação recebida e a aceita ou a recusa, informando o "
              "motivo. Com o aceite, os contatos das duas partes são liberados.",
         refs=["F12", "F17"]),
    dict(nome="Concluir serviço", atores=["Prestador"],
         desc="Após realizar o serviço, o prestador localiza a solicitação no histórico e registra a "
              "conclusão ou registra o cancelamento, com o motivo. O cliente é notificado para "
              "confirmar.",
         refs=["F13", "F17"]),
    dict(nome="Avaliar prestador", atores=["Cliente"],
         desc="O cliente confirma a conclusão do serviço e avalia o prestador com nota e comentário. "
              "O sistema recalcula a reputação do prestador, que passa a influenciar a ordem das "
              "buscas.",
         refs=["F13", "F14", "F15"]),
    dict(nome="Tornar-se prestador", atores=["Cliente"],
         desc="O usuário ativa seu perfil de prestador: escreve a apresentação, confirma o local de "
              "atendimento, cadastra os serviços oferecidos e define a disponibilidade. Ao final, "
              "passa a aparecer nas buscas.",
         refs=["F4", "F5", "F6", "F7"]),
    dict(nome="Moderar denúncia", atores=["Administrador"],
         desc="O administrador analisa uma denúncia pendente, examina o conteúdo denunciado e decide "
              "arquivá-la ou aplicar uma medida. O sistema aplica os efeitos e notifica os "
              "envolvidos.",
         refs=["F18", "F19", "F15"]),
]

# Modelo conceitual preliminar: (nome, [atributos])
CLASSES = {
    "Denúncia": ["motivo: Enumeração", "descricao: String", "data: Data", "situacao: Enumeração",
                 "medida: Enumeração", "justificativa: String", "dataDecisao: Data"],
    "Administrador": ["nome: String", "email: String"],
    "Categoria": ["nome: String", "icone: Imagem", "situacao: Enumeração"],
    "Usuário": ["nome: String", "email: String", "cpf: String", "telefone: String",
                "dataNascimento: Data", "endereco: Endereço", "localizacao: Coordenada",
                "fotoPerfil: Imagem", "ativo: Booleano"],
    "Prestador": ["apresentacao: String", "localBase: Endereço", "localizacaoBase: Coordenada",
                  "raioAtendimento: Real", "disponibilidade: GradeSemanal",
                  "inicioIndisponibilidade: Data", "fimIndisponibilidade: Data",
                  "portfolio: Imagem [0..10]", "ativo: Booleano", "dataCadastro: Data",
                  "notaMedia: Real", "totalAvaliacoes: Inteiro"],
    "Serviço": ["titulo: String", "descricao: String", "precoMinimo: Moeda", "precoMaximo: Moeda",
                "unidadeCobranca: Enumeração", "ativo: Booleano"],
    "Avaliação": ["nota: Inteiro", "comentario: String", "anexos: Imagem [*]", "data: Data",
                  "resposta: String"],
    "Solicitação": ["descricao: String", "dataDesejada: Data", "turno: Enumeração",
                     "endereco: Endereço", "estado: Enumeração", "dataCriacao: Data",
                     "observacao: String", "motivoRecusa: Enumeração", "motivoCancelamento: String",
                     "valorCobrado: Moeda", "dataConclusao: Data"],
}

# (classeA, classeB, rótulo) — há duas associações "denuncia" (Denúncia->Usuário e Denúncia->Avaliação,
# pois F18 permite denunciar tanto um perfil quanto uma avaliação).
ASSOCIACOES = [
    ("Usuário", "Prestador", "atua como"),
    ("Usuário", "Solicitação", "solicita"),
    ("Usuário", "Denúncia", "registra"),
    ("Prestador", "Serviço", "oferece"),
    ("Categoria", "Serviço", "classificado em"),
    ("Serviço", "Solicitação", "referente a"),
    ("Avaliação", "Solicitação", "origina"),
    ("Denúncia", "Administrador", "analisada por"),
    ("Administrador", "Categoria", "mantém"),
    ("Denúncia", "Usuário", "denuncia"),
    ("Denúncia", "Avaliação", "denuncia"),
]

# Conceitos (CRUD): nome, C, R, U, D, observação, refs
CONCEITOS = [
    ('Usuário', True, True, True, True,
     'Qualquer pessoa maior de 18 anos pode se cadastrar. A exclusão anonimiza os dados pessoais e só é possível sem solicitações em andamento.',
     ['F1', 'F2', 'F3']),
    ('Prestador', False, True, True, True,
     'Como a criação do perfil de prestador é um processo iterativo, não trivial (apresentação, serviços e disponibilidade), está descrita no caso de uso “Tornar-se prestador”. A exclusão corresponde à desativação do perfil, só permitida sem solicitações em andamento.',
     ['F4', 'F6', 'F10']),
    ('Serviço', True, True, True, True,
     'Só é possível excluir um serviço sem solicitações em andamento.',
     ['F5']),
    ('Categoria', True, True, True, True,
     'Mantida apenas pelo administrador. Só é possível excluir uma categoria sem serviços associados; caso contrário, ela é desativada.',
     ['F5', 'F20']),
    ('Solicitação', False, True, True, False,
     'Criada apenas pelo caso de uso “Contratar serviço” e alterada (mudança de estado) pelos casos de uso “Responder solicitação”, “Concluir serviço” e “Avaliar prestador”, pelo cancelamento do cliente, pela expiração automática e pela suspensão do prestador. Não é excluída: cancelamentos permanecem no histórico.',
     ['F11', 'F12', 'F13', 'F17', 'F19']),
    ('Avaliação', False, True, True, True,
     'Criada apenas pelo caso de uso “Avaliar prestador”. Pode ser editada pelo cliente e receber resposta do prestador. É excluída somente por decisão de moderação.',
     ['F14', 'F15', 'F16', 'F19']),
    ('Denúncia', True, True, True, False,
     'Qualquer usuário pode registrar. A decisão é registrada no caso de uso “Moderar denúncia”. Não é excluída, para manter o registro das decisões.',
     ['F18', 'F19']),
    ('Administrador', True, True, True, True,
     'Contas de administrador são criadas apenas por outro administrador; não há cadastro público. O primeiro administrador é criado na implantação do sistema.',
     ['F19', 'F20']),
]

# Consultas (relatórios)
CONSULTAS = [
    ('Prestadores mais bem avaliados por categoria e cidade', ['F1', 'F5', 'F8', 'F14', 'F15']),
    ('Categorias mais solicitadas por período', ['F11', 'F20']),
    ('Serviços concluídos por prestador por mês (quantidade e nota média)', ['F13', 'F14', 'F17']),
    ('Taxa de aceitação e de cancelamento de solicitações por prestador', ['F11', 'F12', 'F13']),
    ('Novos prestadores cadastrados por categoria e período', ['F4', 'F5']),
    ('Denúncias por motivo e situação em um período', ['F18', 'F19']),
]

# ---------------------------------------------------------------------------
# PLANEJAMENTO PRELIMINAR
# ---------------------------------------------------------------------------

# Ciclos iterativos: (ciclo, casos de uso, manutenção (CRUD), consultas, observações, total)
CICLOS = [
    ("1", ["Contratar serviço (250h)"], ["Categoria (50h)"], ["-"],
     "Parte do mecanismo de persistência (banco de dados geoespacial) e integração com a API de "
     "geocodificação (100h). Clientes e prestadores de teste inseridos por stubs.", 400),
    ("2", ["Tornar-se prestador (160h)", "Responder solicitação (120h)"], ["Usuário (80h)"], ["-"],
     "Terminar de implementar o mecanismo de persistência (40h).", 400),
    ("3", ["Concluir serviço (100h)", "Avaliar prestador (160h)"],
     ["Serviço (70h)", "Prestador (70h)"], ["-"], "-", 400),
    ("4", ["Moderar denúncia (130h)"],
     ["Solicitação (30h)", "Avaliação (30h)", "Denúncia (30h)", "Administrador (30h)"],
     ["Todas (150h)"], "-", 400),
]

JUSTIFICATIVA_CICLOS = (
    "Os casos de uso foram priorizados por risco: primeiro os processos de negócio, depois a "
    "manutenção de informações (CRUD) e, por último, as consultas, que dependem de dados já "
    "estruturados. “Contratar serviço” vem no ciclo 1 por ser o núcleo do Bicus e o ponto "
    "de maior incerteza técnica (geolocalização, busca por raio e ranking). Nesse ciclo, clientes e "
    "prestadores ainda não podem se cadastrar pelo sistema (o cadastro de usuários entra no ciclo "
    "2), então dados de teste são inseridos por stubs."
)

# Cronograma: blocos de 5 dias; cada ciclo -> {fase: [(dia_inicio, dia_fim)]}
DIAS_TOTAIS = 100
CRONOGRAMA = [
    ("Ciclo 1", [("A", 1, 10), ("P", 11, 20), ("I", 21, 30), ("T", 31, 35), ("C", 36, 40)]),
    ("Ciclo 2", [("A", 21, 30), ("P", 31, 40), ("I", 41, 50), ("T", 51, 55), ("C", 56, 60)]),
    ("Ciclo 3", [("A", 41, 50), ("P", 51, 60), ("I", 61, 70), ("T", 71, 75), ("C", 76, 80)]),
    ("Ciclo 4", [("A", 61, 70), ("P", 71, 80), ("I", 81, 90), ("T", 91, 95)]),
    ("Implantação", [("Implantação", 96, 100)]),
]

LEGENDA_FASES = [
    ("A", "Análise"), ("P", "Projeto"), ("I", "Implementação"), ("T", "Testes"),
    ("C", "Correções / folga"),
]

RESPONSAVEIS = [
    ("Análise (A) e Projeto (P)", "Hugo Costa Araújo (analista-projetista)", "Vermelho", "A"),
    ("Implementação (I)", "Lucas Silva Delgado e Luis Felipe Martins Pereira "
     "(programadores-testadores)", "Amarelo", "I"),
    ("Testes (T)", "Lucas Silva Delgado e Luis Felipe Martins Pereira", "Azul", "T"),
    ("Correções / folga (C)", "Lucas Silva Delgado e Luis Felipe Martins Pereira", "Cinza", "C"),
    ("Implantação", "Toda a equipe", "Verde", "Implantação"),
]

OBS_CRONOGRAMA = [
    "A estimativa considera uma equipe de 3 integrantes trabalhando 8 horas por dia útil: 1 "
    "analista-projetista e 2 programadores-testadores. Cada ciclo soma 400 horas: Análise (10 "
    "dias × 1 pessoa × 8h = 80h) + Projeto (10 × 1 × 8h = 80h) + Implementação (10 × 2 × 8h = "
    "160h) + Testes (5 × 2 × 8h = 80h). Os 4 ciclos totalizam 1.600 horas em 100 dias úteis "
    "(cerca de 20 semanas). Cada ciclo dura 8 semanas (o ciclo 4, sem a etapa de correções, dura "
    "7). Os 5 dias de “Correções / folga” (C) não entram nas 400 horas de cada ciclo: "
    "funcionam como reserva.",
    "Os ciclos se sobrepõem: enquanto os programadores implementam e testam um ciclo, o "
    "analista-projetista já trabalha na análise e no projeto do ciclo seguinte. Os 5 dias de "
    "“Correções / folga” (C) acomodam correções de defeitos e mudanças de requisitos "
    "antes do início da implementação seguinte. Após concluir o projeto do ciclo 4, o "
    "analista-projetista prepara a implantação (manual do usuário e testes de aceitação).",
]

# ---------------------------------------------------------------------------
# ARQUIVADO — removido do documento oficial em 02/10/2026 (commit 920619c)
# ---------------------------------------------------------------------------
# Mantido aqui só para o grupo decidir depois se quer restaurar algo. gerar.py NÃO usa
# nada a partir daqui. Ver LEIA-ME.md e a conversa com o Claude de 08/10/2026 para o
# resumo do que foi removido e por quê.

# "1. Visão Geral do Sistema" (Problema, Proposta, Atores, Escopo) e a página de Sumário
# saíram do documento inteiras. Texto original preservado abaixo.

VISAO_PROBLEMA_ARQUIVADO = [
    "Quem presta pequenos serviços, como jardinagem, aulas particulares, pequenos reparos "
    "domésticos, faxina e reforço escolar, costuma divulgar seu trabalho de maneira informal: "
    "indicações boca a boca, grupos de WhatsApp e Facebook ou redes sociais pessoais. Para quem "
    "precisa contratar um serviço pontual, encontrar um prestador de confiança é um processo lento, "
    "baseado em recomendações de conhecidos ou em informações dispersas na internet. Também não é "
    "possível verificar rapidamente se o prestador está próximo, qual é o seu histórico de "
    "avaliações, sua disponibilidade e a qualidade dos serviços já realizados.",
    "Essa falta de organização prejudica os dois lados. Prestadores novos, sem uma rede de "
    "indicações estabelecida, têm dificuldade em conseguir os primeiros trabalhos, mesmo sendo "
    "qualificados. Clientes acabam recorrendo sempre ao mesmo prestador por falta de uma forma "
    "fácil de comparar alternativas.",
]

VISAO_PROPOSTA_ARQUIVADO = (
    "O Bicus é uma plataforma online (web e mobile) que aproxima clientes e prestadores de pequenos "
    "serviços locais. Prestadores se cadastram informando categoria de atuação, descrição do "
    "serviço, faixa de preço e localização. Ao buscar por uma categoria, o cliente recebe a lista "
    "de prestadores daquela categoria dentro de um raio de distância configurável a partir da sua "
    "localização, ordenada pela combinação de proximidade geográfica e nota média das avaliações "
    "anteriores. Após a conclusão de cada serviço, o cliente avalia o prestador, alimentando um "
    "histórico de reputação que passa a fazer parte do processo de recomendação."
)

VISAO_FUNCIONALIDADES_ARQUIVADO = [
    "Cadastro de usuários e ativação de perfil de prestador, com serviços, faixa de preço, "
    "localização e disponibilidade;",
    "Busca de prestadores por categoria dentro de um raio configurável, com ordenação por "
    "proximidade e reputação;",
    "Solicitação de serviço ao prestador, com aceite ou recusa e liberação do contato após o aceite;",
    "Registro de conclusão do serviço e avaliação do prestador pelo cliente (nota e comentário);",
    "Histórico de reputação usado na recomendação, incluindo tratamento justo para prestadores novos;",
    "Denúncia de conteúdo inadequado e moderação pelo administrador.",
]

ATORES_ARQUIVADO = [
    ("Cliente",
     "Qualquer pessoa cadastrada que busca e contrata serviços. Busca prestadores, envia "
     "solicitações, confirma a conclusão e avalia o prestador."),
    ("Prestador",
     "Cliente que ativou um perfil de prestador. Além de contratar serviços, cadastra os serviços "
     "que oferece, define sua disponibilidade, responde às solicitações e registra a conclusão dos "
     "serviços. Na UML, é uma especialização do ator Cliente."),
    ("Administrador",
     "Membro da equipe do Bicus. Mantém as categorias de serviço e modera as denúncias de "
     "conteúdo inadequado."),
]

ESCOPO_DENTRO_ARQUIVADO = [
    "Cadastro e autenticação de usuários; perfil de prestador, serviços oferecidos e disponibilidade;",
    "Busca geográfica por categoria e raio, com ranking por proximidade e nota;",
    "Ciclo da solicitação de serviço (envio, aceite/recusa, conclusão, cancelamento);",
    "Avaliação do prestador, reputação e resposta do prestador à avaliação;",
    "Denúncias, moderação e manutenção de categorias.",
]

ESCOPO_FORA_ARQUIVADO = [
    "Pagamento intermediado pela plataforma: preço e pagamento são combinados diretamente entre "
    "cliente e prestador;",
    "Chat interno: após o aceite, a conversa segue pelo telefone/WhatsApp liberado pelo sistema;",
    "Avaliação do cliente pelo prestador;",
    "Verificação de documentos ou antecedentes dos prestadores;",
    "Cálculo de rotas reais: a distância considerada é em linha reta.",
]

# "4.3. Prioridade para melhores práticas do RUP" — removida intencionalmente (confirmado
# pelo grupo em 08/10/2026). Texto original preservado abaixo.

RUP_ARQUIVADO = [
    ("Desenvolva software iterativamente",
     "O valor do Bicus depende de uma regra que só pode ser validada com uso real: a ordenação "
     "dos prestadores por proximidade e nota. Entregar o sistema em ciclos permite que, ao fim de "
     "cada ciclo, clientes e prestadores façam testes de aceitação, e que pesos, raios e prazos "
     "sejam ajustados antes que o restante do sistema dependa deles."),
    ("Gerencie requisitos",
     "O sistema atende a dois públicos com interesses diferentes (quem contrata e quem presta o "
     "serviço) e reúne muitas regras de negócio marcadas como transitórias, como prazos da "
     "solicitação, fórmula de pontuação e limites de busca. Manter os requisitos documentados e "
     "rastreados até os casos de uso permite avaliar o impacto de cada mudança."),
    ("Verifique continuamente a qualidade",
     "A proposta do Bicus é oferecer informações confiáveis. Um defeito que permita avaliar sem "
     "ter contratado o serviço, ou que distorça o ranking, compromete a confiança na plataforma. "
     "Por isso, as regras de avaliação, reputação e permissões devem ser testadas em todos os "
     "ciclos, e não apenas no final."),
    ("Controle as mudanças",
     "Vários requisitos foram marcados como transitórios (APIs externas, raio de busca, fórmula "
     "de pontuação e ausência de pagamento intermediado). Mudanças nesses pontos devem passar "
     "por um processo de solicitação que avalie viabilidade e impacto antes de serem "
     "incorporadas."),
    ("Use arquiteturas baseadas em componentes",
     "As interfaces web e mobile consomem a mesma API, e os serviços externos de geocodificação "
     "devem ficar isolados em componentes próprios, para que possam ser trocados sem afetar o "
     "restante do sistema."),
    ("Modele visualmente o software",
     "Os diagramas UML (casos de uso e modelo conceitual) mantêm a equipe alinhada sobre o "
     "domínio. Por ser uma equipe pequena, com comunicação direta, esta prática recebe a menor "
     "prioridade."),
]
