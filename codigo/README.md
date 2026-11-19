# Bicus – Contratação de serviço

Implementação de um módulo do **Bicus**, marketplace de bicos e pequenos serviços locais, feita na
disciplina INF323 – Engenharia de Software II (UFV).

O módulo cobre o fluxo principal do cliente:

1. Busca de prestadores por categoria, perto do cliente, ordenada pela pontuação de recomendação.
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
├── domain/          enums (Turno, EstadoSolicitacao, UnidadeCobranca) e Coordenada
├── seeds/           dados simulados e o comando `flask carregar-dados`
└── static/          css/js/imagens
migrations/          histórico do schema (Flask-Migrate)
tests/               unit/ e integration/
```

Divisão entre as partes:

| Parte | Controller | Templates | Rotas |
|---|---|---|---|
| A – Solicitação (H01, H02) | `controllers/solicitacoes_controller.py` | `views/solicitacoes/` | `/solicitacoes/nova/<servico_id>`, `/solicitacoes` |
| B – Busca e recomendação (H03, H04) | `controllers/busca_controller.py` | `views/busca/` | `/busca` |

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
- Pelo NF4.2, a busca mostra bairro e distância, nunca o endereço completo do prestador.

## Convenções

- **Mensagens na tela:** `flash("texto", "erro")` (vermelha) ou `flash("texto", "sucesso")` (verde).
- **Mudou um modelo?** `flask db migrate -m "descrição"`, confira o arquivo gerado em
  `migrations/versions/` e rode `flask db upgrade`. A migração vai no mesmo commit da mudança.
- **Commits direto na `main`**, sem branches. Antes de começar, `git pull`; o histórico fica em
  linha reta, sem commit de merge.
- **Commits:** citam o cartão, ex.: `H03: filtra prestador fora do raio (#3)`.
- **Uma vez por computador:** `git config --global pull.rebase true`.
