# Requisitos funcionais

> **Legenda.** *Oculto (X)*: função executada pelo sistema sem o conhecimento explícito do usuário. *Desejável (X)*: pode ser atendido se houver tempo e recursos; `( )` = obrigatório. *Permanente (X)*: poucas chances de mudar; `( )` = transitório.

**Resumo:** 20 requisitos funcionais (3 ocultos), 84 requisitos não-funcionais (30 desejáveis, 23 transitórios).

## Índice

| Código | Requisito funcional | Oculto | Nº de NFs |
|---|---|:---:|:---:|
| F1 | Cadastrar usuário | ( ) | 8 |
| F2 | Login | ( ) | 2 |
| F3 | Editar dados da conta de usuário | ( ) | 5 |
| F4 | Cadastrar perfil de prestador | ( ) | 5 |
| F5 | Gerenciar serviços oferecidos | ( ) | 5 |
| F6 | Definir disponibilidade | ( ) | 3 |
| F7 | Obter localização geográfica | (X) | 4 |
| F8 | Buscar prestadores por categoria | ( ) | 7 |
| F9 | Calcular pontuação de recomendação | (X) | 2 |
| F10 | Visualizar perfil do prestador | ( ) | 3 |
| F11 | Solicitar serviço | ( ) | 7 |
| F12 | Responder solicitação | ( ) | 4 |
| F13 | Concluir serviço | ( ) | 5 |
| F14 | Avaliar prestador | ( ) | 4 |
| F15 | Atualizar reputação do prestador | (X) | 1 |
| F16 | Responder avaliação | ( ) | 1 |
| F17 | Consultar histórico de solicitações | ( ) | 4 |
| F18 | Denunciar conteúdo | ( ) | 4 |
| F19 | Moderar denúncias | ( ) | 5 |
| F20 | Gerenciar categorias de serviço | ( ) | 5 |

---

### F1 Cadastrar usuário — Oculto ( )

**Descrição:** O sistema deverá conter uma tela de cadastro onde solicitará os dados do usuário, tais como: nome completo, e-mail, senha, CPF, telefone, data de nascimento, endereço e foto de perfil. Todo usuário cadastrado pode contratar serviços como cliente e, posteriormente, ativar um perfil de prestador (F4).

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF1.1** Validação do CPF | O sistema deve validar os dígitos verificadores do CPF. Caso não seja válido, o sistema deverá avisar o usuário e interromper o cadastro. | Segurança | ( ) | (X) |
| **NF1.2** Dados obrigatórios | O sistema deve associar obrigatoriamente à conta: nome completo, e-mail, senha, CPF, telefone, data de nascimento e endereço. | Segurança | ( ) | (X) |
| **NF1.3** Dados opcionais | O sistema deve associar opcionalmente à conta: foto de perfil e complemento do endereço. | Interface | ( ) | (X) |
| **NF1.4** Unicidade da conta | Não poderá existir mais de uma conta com o mesmo CPF ou com o mesmo e-mail. | Segurança | ( ) | (X) |
| **NF1.5** Idade mínima | A data de nascimento deve indicar idade igual ou superior a 18 anos; caso contrário, o sistema deverá avisar o usuário e interromper o cadastro. | Legal | ( ) | (X) |
| **NF1.6** Política de senha | A senha deve ter no mínimo 8 caracteres, com ao menos uma letra e um número. | Segurança | ( ) | ( ) |
| **NF1.7** Termos de uso e privacidade | O cadastro só será concluído após o aceite dos Termos de Uso e da Política de Privacidade. | Legal | ( ) | (X) |
| **NF1.8** Confirmação de e-mail | O sistema enviará um link de confirmação para o e-mail informado. A conta só é ativada após a confirmação. | Segurança | (X) | (X) |

---

### F2 Login — Oculto ( )

**Descrição:** O sistema irá conter uma tela de login que solicitará o e-mail e a senha do usuário.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF2.1** Permissão de acesso | O usuário só terá acesso ao sistema caso esteja cadastrado, com conta ativa e a senha digitada corresponda à senha cadastrada. | Segurança | ( ) | (X) |
| **NF2.2** Recuperação de senha | O usuário poderá redefinir a senha por meio de um link enviado ao e-mail cadastrado. | Usabilidade | ( ) | (X) |

---

### F3 Editar dados da conta de usuário — Oculto ( )

**Descrição:** Os usuários poderão alterar alguns dados da conta, como nome, telefone, endereço, foto de perfil, e-mail e senha, e também solicitar a exclusão da conta.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF3.1** Dados não alteráveis | As informações de CPF e data de nascimento não poderão ser alteradas. | Segurança | ( ) | (X) |
| **NF3.2** Alteração de e-mail | A alteração do e-mail exige nova confirmação pelo novo endereço. | Segurança | (X) | (X) |
| **NF3.3** Alteração de senha | Para alterar a senha, o usuário deve informar a senha atual. | Segurança | ( ) | (X) |
| **NF3.4** Atualização da localização | Ao alterar o endereço, o sistema deve recalcular as coordenadas geográficas do usuário. | Usabilidade | ( ) | (X) |
| **NF3.5** Exclusão da conta | O usuário pode solicitar a exclusão da conta. As avaliações já feitas permanecerão, sem identificação do autor. Não é possível excluir a conta com solicitações em andamento. | Legal | ( ) | (X) |

---

### F4 Cadastrar perfil de prestador — Oculto ( )

**Descrição:** O sistema deverá permitir que um usuário cadastrado ative um perfil de prestador, informando uma apresentação profissional, o local base de atendimento (caso exista) e, opcionalmente, fotos de trabalhos já realizados.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF4.1** Conta única | O perfil de prestador fica vinculado à conta do usuário, que continua podendo contratar serviços como cliente. | Segurança | ( ) | (X) |
| **NF4.2** Privacidade do endereço | O endereço completo do prestador nunca é exibido publicamente. Apenas bairro, cidade e distância aproximada. | Segurança | ( ) | (X) |
| **NF4.3** Raio de deslocamento | O prestador pode definir a distância máxima (em km) que aceita se deslocar. Clientes fora desse raio não o encontrarão nas buscas. | Configurabilidade | (X) | ( ) |
| **NF4.4** Portfólio | O prestador pode adicionar até 10 fotos de trabalhos realizados. | Implementação | (X) | ( ) |
| **NF4.5** Desativação do perfil | O prestador pode desativar o perfil e deixar de aparecer nas buscas. Não é possível desativá-lo com solicitações em andamento. | Usabilidade | ( ) | (X) |

---

### F5 Gerenciar serviços oferecidos — Oculto ( )

**Descrição:** O prestador poderá cadastrar, editar e remover os serviços que oferece, informando para cada um: categoria, título, descrição, faixa de preço (valor mínimo e máximo) e unidade de cobrança.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF5.1** Seleção de categoria | A categoria deve ser escolhida em uma lista pré-definida e não digitada livremente. | Interface | ( ) | (X) |
| **NF5.2** Faixa de preço | Os valores devem ser informados em reais com valor mínimo menor ou igual ao valor máximo. | Interface | ( ) | (X) |
| **NF5.3** Unidade de cobrança | A unidade de cobrança será escolhida entre: por hora, por diária ou por serviço. | Configurabilidade | ( ) | ( ) |
| **NF5.4** Um serviço por categoria | O prestador pode ter no máximo um serviço em cada categoria, evitando que apareça repetido nos resultados de uma busca. | Configurabilidade | ( ) | ( ) |
| **NF5.5** Remoção de serviço | Um serviço com solicitações em andamento não pode ser removido. | Configurabilidade | ( ) | (X) |

---

### F6 Definir disponibilidade — Oculto ( )

**Descrição:** O prestador poderá informar os dias da semana e turnos em que costuma atender, bem como marcar períodos de indisponibilidade temporária (ex.: férias).

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF6.1** Grade semanal | A disponibilidade é informada marcando os dias da semana e os turnos (manhã, tarde e noite) de atendimento. | Interface | (X) | (X) |
| **NF6.2** Indisponibilidade temporária | Durante um período marcado como indisponível, o prestador não aparece nas buscas. | Usabilidade | (X) | (X) |
| **NF6.3** Exibição no perfil | A grade de disponibilidade é exibida no perfil do prestador. | Interface | (X) | (X) |

---

### F7 Obter localização geográfica — Oculto (X)

**Descrição:** O sistema obtém as coordenadas geográficas dos usuários: para prestadores, a partir do endereço base de atendimento. Para clientes, a partir do endereço cadastrado.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF7.1** Obtenção de coordenadas | A conversão de endereço em coordenadas será feita por uma API externa de geocodificação. | Implementação | ( ) | ( ) |
| **NF7.2** Armazenamento das coordenadas | As coordenadas dos prestadores são calculadas uma única vez, no cadastro ou na alteração do endereço, e armazenadas, evitando geocodificar a cada busca. | Desempenho | ( ) | (X) |
| **NF7.3** Endereço não localizado | Caso o endereço não seja localizado pela API, o sistema deve avisar o usuário e permitir ajustar a posição em um mapa. | Usabilidade | (X) | ( ) |
| **NF7.4** Outro ponto de partida | O cliente pode buscar a partir de outro endereço ou CEP sem alterar o seu cadastro. | Usabilidade | (X) | (X) |

---

### F8 Buscar prestadores por categoria — Oculto ( )

**Descrição:** O cliente seleciona uma categoria de serviço e o sistema identifica todos os prestadores com serviço ativo nessa categoria dentro de um raio de distância configurável a partir da localização do cliente, exibindo uma lista ordenada pela combinação de proximidade geográfica e nota média das avaliações (F9).

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF8.1** Raio configurável | O cliente define o raio de busca. | Configurabilidade | ( ) | ( ) |
| **NF8.2** Cálculo da distância | A distância é calculada em linha reta entre as coordenadas do cliente e do prestador. | Implementação | ( ) | ( ) |
| **NF8.3** Prestadores exibidos | Não são exibidos na lista: o próprio usuário, prestadores com perfil excluído ou prestadores em período de indisponibilidade e prestadores cujo raio de deslocamento não alcança o cliente. | Usabilidade | ( ) | (X) |
| **NF8.4** Informações da lista | Cada item exibe: nome e foto do prestador, título do serviço, faixa de preço, nota média (estrelas), quantidade de avaliações e distância aproximada. | Interface | ( ) | (X) |
| **NF8.5** Nenhum resultado | Caso nenhum prestador seja encontrado no raio, o sistema informa o cliente e sugere ampliar o raio de busca. | Usabilidade | (X) | (X) |
| **NF8.6** Filtros adicionais | A lista pode ser filtrada por faixa de preço, nota mínima e disponibilidade (dia e turno). | Configurabilidade | (X) | (X) |
| **NF8.7** Visualização em mapa | O cliente pode alternar entre a lista e um mapa com a posição aproximada dos prestadores encontrados. | Interface | (X) | ( ) |

---

### F9 Calcular pontuação de recomendação — Oculto (X)

**Descrição:** Para cada prestador encontrado na busca, o sistema calcula uma pontuação que combina a proximidade geográfica e a nota do prestador. Essa pontuação define a ordem da lista de resultados.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF9.1** Fórmula de pontuação | Fórmula a definir. Mas atribuirá um peso maior para a pontuação em relação à proximidade geográfica. | Especificação | ( ) | ( ) |
| **NF9.2** Critério de desempate | Em caso de empate, aparece primeiro o prestador com mais serviços concluídos e, depois, o mais próximo. | Especificação | (X) | ( ) |

---

### F10 Visualizar perfil do prestador — Oculto ( )

**Descrição:** O cliente poderá acessar o perfil de um prestador, que exibe: nome, foto, apresentação, serviços oferecidos (categoria, descrição, faixa de preço e unidade de cobrança), disponibilidade, bairro e cidade, distância aproximada, nota média, quantidade de avaliações, quantidade de serviços concluídos, avaliações recebidas e portfólio.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF10.1** Privacidade do contato | O telefone do prestador só é exibido ao cliente depois que o prestador aceitar uma solicitação dele. | Segurança | ( ) | ( ) |
| **NF10.2** Lista de avaliações | As avaliações são exibidas das mais recentes para as mais antigas e podem ser filtradas por nota. | Configurabilidade | (X) | (X) |
| **NF10.3** Distribuição das notas | O perfil exibe a quantidade de avaliações recebidas em cada nota (1 a 5 estrelas). | Interface | (X) | ( ) |

---

### F11 Solicitar serviço — Oculto ( )

**Descrição:** O cliente poderá enviar uma solicitação de serviço a um prestador, escolhendo um dos serviços oferecidos e informando a descrição da necessidade, a data e o turno desejados e o endereço onde o serviço será realizado.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF11.1** Dados da solicitação | São obrigatórios: serviço escolhido, descrição da necessidade, data desejada e turno. | Interface | ( ) | (X) |
| **NF11.2** Data válida | A data desejada deve ser igual ou posterior à data atual. | Interface | ( ) | (X) |
| **NF11.3** Autossolicitação | O usuário não pode enviar solicitação ao seu próprio perfil de prestador. | Segurança | ( ) | (X) |
| **NF11.4** Notificação ao prestador | Ao ser criada a solicitação, o prestador recebe uma notificação por e-mail. | Interface | (X) | (X) |
| **NF11.5** Limite de solicitações pendentes | Cada cliente pode ter no máximo 10 solicitações pendentes (sem resposta) ao mesmo tempo, evitando envios em massa. | Desempenho | (X) | ( ) |
| **NF11.6** Cancelamento pelo cliente | O cliente pode cancelar a solicitação enquanto ela estiver pendente, sem necessidade de justificativa. | Usabilidade | ( ) | (X) |
| **NF11.7** Expiração | Solicitações não respondidas em 72 horas expiram automaticamente. | Usabilidade | (X) | ( ) |

---

### F12 Responder solicitação — Oculto ( )

**Descrição:** O prestador poderá aceitar ou recusar as solicitações recebidas. Ao aceitar, pode fazer observações em relação ao serviço que será prestado.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF12.1** Motivo da recusa | Ao recusar, o prestador pode selecionar um motivo (ex.: sem disponibilidade, fora da área de atendimento, serviço não realizado). | Usabilidade | (X) | (X) |
| **NF12.2** Notificação ao cliente | O cliente é notificado da resposta do prestador. | Interface | (X) | (X) |
| **NF12.3** Liberação dos contatos | Após o aceite, cliente e prestador passam a visualizar o telefone um do outro para combinar os detalhes. | Segurança | ( ) | (X) |
| **NF12.4** Atalho para WhatsApp | O sistema oferece um botão que abre a conversa no WhatsApp com o contato liberado. | Interface | (X) | ( ) |

---

### F13 Concluir serviço — Oculto ( )

**Descrição:** Após a realização do serviço, o prestador registra a conclusão da solicitação e o cliente confirma que o serviço foi realizado. A conclusão confirmada habilita a avaliação do prestador (F14). Antes da conclusão, a solicitação aceita pode ser cancelada por qualquer uma das partes.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF13.1** Estados da solicitação | Uma solicitação pode estar nos estados: Pendente, Aceita, Recusada, Expirada, Cancelada e Concluída. | Implementação | ( ) | ( ) |
| **NF13.2** Confirmação do cliente | O serviço só é considerado concluído após a confirmação do cliente. | Usabilidade | ( ) | ( ) |
| **NF13.3** Valor final | Ao registrar a conclusão, o cliente pode informar o valor efetivamente cobrado. | Usabilidade | (X) | (X) |
| **NF13.4** Cancelamento | Cliente ou prestador podem cancelar uma solicitação aceita, informando o motivo. O cancelamento fica registrado no histórico de ambos. | Segurança | ( ) | (X) |
| **NF13.5** Pedido de avaliação | Ao ser confirmada a conclusão, o cliente recebe uma notificação convidando-o a avaliar o prestador. | Interface | ( ) | (X) |

---

### F14 Avaliar prestador — Oculto ( )

**Descrição:** Após a conclusão de um serviço, o cliente poderá avaliar o prestador atribuindo uma nota de 1 a 5 estrelas e, opcionalmente, um comentário.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF14.1** Direito de avaliar | Somente o cliente de uma solicitação concluída pode avaliá-la, e cada solicitação admite uma única avaliação. | Segurança | ( ) | (X) |
| **NF14.2** Escala da nota | A nota é um número inteiro de 1 a 5, selecionado por estrelas. | Interface | ( ) | (X) |
| **NF14.3** Comentário | O comentário é opcional, assim como anexos. | Interface | ( ) | (X) |
| **NF14.4** Prazo para avaliar | A avaliação pode ser feita em até 7 dias após a conclusão do serviço. | Usabilidade | (X) | ( ) |

---

### F15 Atualizar reputação do prestador — Oculto (X)

**Descrição:** A cada avaliação registrada, editada ou removida, o sistema recalcula a reputação do prestador (nota média e quantidade de avaliações), que passa a ser utilizada no processo de recomendação (F9).

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF15.1** Atualização imediata | A reputação deve ser recalculada no momento em que a avaliação é registrada, editada ou removida. | Desempenho | ( ) | (X) |

---

### F16 Responder avaliação — Oculto ( )

**Descrição:** O prestador poderá publicar uma resposta a uma avaliação recebida, exibida logo abaixo dela no seu perfil.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF16.1** Resposta única | Cada avaliação admite uma única resposta do prestador. | Interface | (X) | (X) |

---

### F17 Consultar histórico de solicitações — Oculto ( )

**Descrição:** Clientes e prestadores poderão consultar o histórico das solicitações enviadas e recebidas, com o estado de cada uma e os dados do serviço.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF17.1** Permissão de acesso | Cada usuário só visualiza as solicitações em que é o cliente ou o prestador. | Segurança | ( ) | (X) |
| **NF17.2** Separação por papel | Usuários que também são prestadores visualizam separadamente os serviços que contrataram e os serviços que prestaram. | Interface | ( ) | (X) |
| **NF17.3** Filtro por estado | O histórico pode ser filtrado pelo estado da solicitação. | Configurabilidade | (X) | (X) |
| **NF17.4** Ordenação do histórico | O histórico pode ser ordenado por data. | Configurabilidade | (X) | (X) |

---

### F18 Denunciar conteúdo — Oculto ( )

**Descrição:** Qualquer usuário poderá denunciar um perfil de outro ou uma avaliação que considere inadequado, informando o motivo.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF18.1** Motivo da denúncia | O motivo é escolhido de uma lista pré-definida com descrição opcional. | Interface | ( ) | ( ) |
| **NF18.2** Denúncia única | Um usuário só pode denunciar o mesmo item uma vez. | Segurança | ( ) | (X) |
| **NF18.3** Sigilo do denunciante | A identidade do denunciante não é revelada ao usuário denunciado. | Segurança | ( ) | (X) |
| **NF18.4** Aviso ao administrador | Cada nova denúncia gera um aviso no painel do administrador. | Interface | (X) | (X) |

---

### F19 Moderar denúncias — Oculto ( )

**Descrição:** O administrador analisa as denúncias recebidas e decide entre arquivá-las ou aplicar uma medida: remover a avaliação denunciada ou advertir, suspender ou banir o usuário.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF19.1** Acesso restrito | Apenas usuários com perfil de administrador podem acessar a moderação. | Segurança | ( ) | (X) |
| **NF19.2** Remoção de avaliação | A remoção de uma avaliação dispara o recálculo da reputação do prestador. | Implementação | ( ) | (X) |
| **NF19.3** Suspensão de usuário | Um usuário suspenso não consegue fazer login durante a suspensão. Se for prestador, deixa de aparecer nas buscas e suas solicitações pendentes são canceladas. | Segurança | ( ) | (X) |
| **NF19.4** Registro das decisões | Toda decisão de moderação é registrada com data, administrador responsável e justificativa. | Segurança | ( ) | (X) |
| **NF19.5** Notificação do resultado | O denunciante e o usuário denunciado são notificados da decisão, sem que o denunciante seja identificado. | Interface | (X) | (X) |

---

### F20 Gerenciar categorias de serviço — Oculto ( )

**Descrição:** O administrador poderá cadastrar, editar e desativar as categorias de serviço disponíveis na plataforma (ex.: jardinagem, aulas particulares, faxina, etc).

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **NF20.1** Nome único | Não podem existir duas categorias com o mesmo nome. | Segurança | ( ) | (X) |
| **NF20.2** Exclusão de categoria | Uma categoria com serviços associados não pode ser excluída, apenas desativada. Categorias desativadas não aparecem nas buscas nem no cadastro de novos serviços. | Especificação | ( ) | (X) |
| **NF20.3** Ícone da categoria | Cada categoria possui um ícone, exibido na tela de busca. | Interface | (X) | (X) |
| **NF20.4** Carga inicial | O sistema será implantado com as categorias: Jardinagem, Aulas particulares, Pequenos reparos domésticos, Faxina, Pintura, Montagem de móveis e Cuidado de animais. | Implementação | ( ) | ( ) |
| **NF20.5** Sugestão de categoria | Prestadores podem sugerir uma nova categoria, que fica pendente até a aprovação do administrador. | Usabilidade | (X) | ( ) |
