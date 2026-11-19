# Bicus – Contratação de serviço

Implementação de um módulo do **Bicus**, marketplace de bicos e pequenos serviços locais, feita na
disciplina INF323 – Engenharia de Software II (UFV).

O módulo cobre o fluxo principal do cliente:

1. Busca de prestadores por categoria, perto do cliente, ordenada pela pontuação de recomendação
   ou, se o cliente preferir, por avaliação, distância ou preço.
2. Envio de uma solicitação de serviço.
3. Lista das próprias solicitações, com cancelamento das pendentes.

**Grupo:** Hugo Costa Araújo, Lucas Silva Delgado e Luis Felipe Martins Pereira.

## Como rodar

Requisitos: Python 3.14 e git.

```powershell
cd codigo
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env                # Linux/Mac: cp .env.example .env
flask db upgrade                      # cria o banco (instance/bicus.db)
flask carregar-dados                  # dados simulados
flask run
```

Abra http://127.0.0.1:5000 e escolha um usuário em "Entrar como".

Para recomeçar o banco do zero: apague `instance/bicus.db` e rode `flask db upgrade` e
`flask carregar-dados` de novo.

## Como usar

1. Em **Entrar como**, escolha um usuário de exemplo: por exemplo, Ana (no Centro) ou Bruno (no
   Ramos). Os prestadores também aparecem na lista, porque também podem contratar.
2. Em **Buscar prestadores**, escolha a categoria e o raio. A lista vem do mais para o menos
   recomendado; clicando nos títulos Preço, Avaliação ou Distância, ela muda de ordem.
3. Em **Solicitar**, o formulário abre numa janela sobre a página Minhas solicitações, já com o
   serviço escolhido e o endereço do cliente. Falta informar a descrição, a data (digitando ou
   pelo calendário ao lado do campo) e o turno. Se algo estiver errado, a mensagem aparece em
   vermelho e o formulário reabre.
4. Em **Minhas solicitações**, a solicitação aparece como Pendente e pode ser cancelada; a
   cancelada continua na lista, no histórico.

Bons exemplos com os dados simulados, entrando como Ana: Faxina com 5 km mostra quatro
prestadoras e as ordens possíveis; Montagem de móveis e Pequenos reparos domésticos não mostram
ninguém (um prestador está indisponível e o outro não se desloca até a Ana).

## Histórias implementadas

Os códigos de requisito são os da F1/F2.

| História | Requisitos | Testes |
|---|---|---|
| H01 – Solicitar serviço | F11: NF11.1, NF11.2, NF11.3, NF11.5, NF13.1 | `unit/test_solicitacoes_service.py`, `integration/test_solicitacoes_rotas.py` |
| H02 – Ver e cancelar minhas solicitações | F17 (simplificado), NF11.6 | `unit/test_solicitacoes_service.py`, `unit/test_modelos.py`, `integration/test_solicitacoes_rotas.py` |
| H03 – Buscar prestadores por categoria e raio | F8, F7: NF5.1, NF8.1 a NF8.5, NF4.3, NF6.2 | `unit/test_busca_service.py`, `unit/test_distancia_service.py`, `unit/test_modelos.py`, `unit/test_formatos.py`, `integration/test_busca_rotas.py` |
| H04 – Ver primeiro os mais recomendados | F9: NF9.1, NF9.2 | `unit/test_pontuacao_service.py`, `unit/test_busca_service.py`, `integration/test_busca_rotas.py` |
| H05 – Escolher a ordem da lista | NF8.8 (requisito acrescentado na F4) | `unit/test_busca_service.py`, `integration/test_busca_rotas.py` |

O NF8.8 não está na F1/F2; foi acrescentado pelo grupo durante a F4: a lista vem, por padrão,
pela recomendação (F9), e o cliente pode ordená-la por avaliação, distância ou preço.

## Testes e lint

```powershell
pytest
ruff check .
```

Os testes usam um banco em memória criado do zero a cada teste (fixtures em `tests/conftest.py`:
`app`, `db` e `client`). Cada teste monta só os dados de que precisa; os dados simulados não são
usados nos testes. Regras que dependem da data de hoje recebem a data como parâmetro.

O GitHub Actions (`.github/workflows/ci.yml`) roda, a cada push: o ruff, as migrações num Postgres
vazio, a conferência entre modelos e migrações e o pytest.

## Fora do escopo

O módulo é a contratação de serviço pelo cliente. Ficaram de fora, por pertencerem a outros
módulos ou por serem desejáveis:

- cadastro, login e gestão da conta (F1, F2, F3), substituídos pela tela "Entrar como";
- área do prestador: perfil e serviços (F4, F5), disponibilidade com grade semanal (F6) e resposta
  e conclusão das solicitações (F12, F13);
- perfil do prestador (F10), avaliações (F14 a F16), denúncias (F18) e administração (F19, F20);
- na busca: filtros adicionais (NF8.6), mapa (NF8.7), outro ponto de partida (NF7.4) e foto do
  prestador (NF8.4);
- na solicitação: notificação por e-mail (NF11.4) e expiração em 72 horas (NF11.7);
- em Minhas solicitações: filtros e ordenação (resto do F17).

## Estrutura

```
bicus/
├── __init__.py      create_app (app factory)
├── config.py        configuração lida das variáveis de ambiente
├── extensions.py    db e migrate
├── formatos.py      números no formato brasileiro nas páginas (filtros do Jinja)
├── models/          Model: classes do SQLAlchemy
├── views/           View: templates Jinja + Bootstrap
├── controllers/     Controller: blueprints com as rotas
├── services/        regras do módulo, em Python puro (busca, pontuação, solicitação)
├── domain/          enums (Turno, EstadoSolicitacao, UnidadeCobranca, OrdemBusca) e Coordenada
├── seeds/           dados simulados e o comando `flask carregar-dados`
└── static/          css/js/imagens
migrations/          histórico do schema (Flask-Migrate)
tests/               unit/ e integration/
```

Divisão entre as partes:

| Parte | Controller | Templates | Rotas |
|---|---|---|---|
| A – Solicitação (H01, H02) | `controllers/solicitacoes_controller.py` | `views/solicitacoes/` | `GET /solicitacoes` (com `?servico=<id>` abre o formulário), `POST /solicitacoes`, `POST /solicitacoes/<id>/cancelar` |
| B – Busca e recomendação (H03 a H05) | `controllers/busca_controller.py` | `views/busca/` | `GET /busca?categoria=<id>&raio=<km>&ordem=<ordem>` |

Nas rotas que exigem usuário, use `@usuario_obrigatorio`; para obter o usuário da sessão, use
`usuario_logado()` (ambos em `controllers/sessao_controller.py`).

## O que é simulado

Cadastro, login, área do prestador, avaliações e geocodificação pertencem a outros módulos e não
foram implementados. No lugar deles:

- **Login:** a tela "Entrar como" lista os usuários de exemplo; escolher um grava
  `session["usuario_id"]`, sem senha. Desligada com `MODO_DEMO=0`.
- **Usuários, prestadores e serviços:** carregados por `flask carregar-dados`
  (`bicus/seeds/dados_simulados.py`). As 7 categorias do NF20.4 não são simuladas: são dados de
  referência, criados pela migração `categorias_iniciais` no `flask db upgrade`. Cada prestador
  exercita um caso da busca (raio curto, indisponível, perfil desativado, serviço inativo, sem
  avaliação); na Faxina, quatro prestadoras mostram a ordem da recomendação (H04).
- **Avaliações:** `nota_media` e `total_avaliacoes` são colunas preenchidas pela carga (na F2 são
  atributos derivados das avaliações).
- **Localização:** coordenadas fixas por bairro de Viçosa, no lugar da API de geocodificação (F7).

## Decisões de modelagem

- **Prestador como perfil 1:1 do usuário** (chave primária compartilhada: `prestador.id` é o
  `usuario.id`), e não como subclasse
  como no modelo conceitual da F2: pelo NF4.1, o usuário vira prestador e continua contratando
  como cliente.
- **Enums gravados como texto**, para acrescentar valores sem migração complicada.
- **Raio de deslocamento vazio** (`raio_deslocamento_km` = `None`): o prestador atende qualquer
  distância. O NF4.3 diz que ele "pode" definir o raio, ou seja, é opcional.
- **Indisponibilidade** (NF6.2): o prestador some da busca se hoje está dentro do período marcado,
  contando o primeiro e o último dia; sem data de fim, continua indisponível.
- **Pontuação de recomendação** (F9, NF9.1): `0,6 × nota/5 + 0,4 × (1 − distância/raio da busca)`,
  de 0 a 1; a nota vale até 0,6 e a proximidade até 0,4. Prestador sem avaliação conta como nota
  3 (neutra). Não aparece na tela: só define a ordem da lista.
- **Desempate** (NF9.2): mais avaliações (no lugar de "serviços concluídos", que o sistema não
  registra; cada avaliação vem de um serviço concluído) e, depois, o mais próximo.
- **Ordem escolhida pelo cliente** (NF8.8, requisito acrescentado na F4): a recomendação é a
  ordem padrão; clicando no título da coluna, o cliente ordena por avaliação (maior primeiro; sem
  avaliação no fim), distância (mais perto) ou preço (mais barato). No empate, a recomendação.
- Pelo NF4.2, a busca mostra bairro e distância, nunca o endereço completo do prestador.

## Convenções

- **Nomes de arquivo:** `*_controller.py` em `controllers/` e `*_service.py` em `services/`.
- **Regras no service**, não no controller: o controller só lê a requisição, chama o service e
  escolhe a resposta. Regra recusada = `SolicitacaoInvalidaError("mensagem")` no service; o
  controller mostra a mensagem com `flash`.
- **JavaScript só em `static/js/`** (e CSS em `static/css/`), carregado pelos blocos do
  `base.html`; dados do servidor vão por atributos `data-*` no HTML, nunca por código dentro do
  template.
- **Depois de todo POST, `redirect`**, para o navegador não reenviar o formulário ao recarregar.
- **Dados do banco:** as categorias vêm da migração (`flask db upgrade`); usuários e serviços de
  exemplo vêm do `flask carregar-dados`.
- **Mensagens na tela:** `flash("texto", "erro")` (vermelha) ou `flash("texto", "sucesso")` (verde).
- **Mudou um modelo?** `flask db migrate -m "descrição"`, confira o arquivo gerado em
  `migrations/versions/` e rode `flask db upgrade`. A migração vai no mesmo commit da mudança.
- **Commits direto na `main`**, sem branches. Antes de começar, `git pull`; o histórico fica em
  linha reta, sem commit de merge.
- **Commits:** citam o cartão, ex.: `H03: filtra prestador fora do raio (#3)`.
- **Uma vez por computador:** `git config --global pull.rebase true`.
