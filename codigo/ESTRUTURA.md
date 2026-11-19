# Estrutura do projeto

Como o código do Bicus está organizado, o papel de cada pasta e arquivo e como as peças se ligam.

## 1. Visão geral

```
codigo/
├── bicus/                     pacote da aplicação
│   ├── __init__.py            create_app: monta o app (app factory)
│   ├── config.py              configuração por ambiente (lida das variáveis de ambiente)
│   ├── extensions.py          db (SQLAlchemy) e migrate (Flask-Migrate)
│   ├── formatos.py            números no formato brasileiro (filtros do Jinja)
│   ├── domain/                vocabulário do sistema: enums e objetos de valor
│   ├── models/                MODEL: tabelas do banco (SQLAlchemy)
│   ├── services/              regras de negócio em Python puro
│   ├── controllers/           CONTROLLER: rotas (blueprints)
│   ├── views/                 VIEW: templates Jinja + Bootstrap
│   ├── static/                css, js e imagens servidos sem processamento
│   └── seeds/                 dados simulados e o comando flask carregar-dados
├── migrations/                histórico do schema do banco (gerado pelo Flask-Migrate)
├── tests/                     conftest.py (fixtures), unit/ e integration/
├── instance/                  banco SQLite local (fora do git)
├── wsgi.py                    ponto de entrada: flask run e gunicorn
├── pyproject.toml             regras do ruff e configuração do pytest
├── requirements.txt           dependências de produção
├── requirements-dev.txt       produção + pytest, ruff, python-dotenv
├── .env.example               variáveis de ambiente (copiar para .env)
└── .python-version            versão do Python (usada pelo CI)

.github/workflows/ci.yml       pipeline do GitHub Actions (na raiz do repositório)
```

## 2. As camadas e o caminho de uma requisição

```
navegador
   │  GET /busca?categoria=4&raio=5
   ▼
controllers/busca_controller.py   lê a requisição e a sessão, chama o service, escolhe o template
   │
   ▼
services/busca_service.py         aplica as regras (filtros, distância, pontuação) — sem Flask
   │
   ▼
models/                   consulta e grava no banco via SQLAlchemy
   │
   ▼
controllers/busca_controller.py   recebe o resultado
   │
   ▼
views/busca/index.html    monta o HTML com os dados
   │
   ▼
navegador
```

`domain/` é usado por todas as camadas (um modelo guarda um `Turno`, um service valida um `Turno`,
um controller lê um `Turno` do formulário).

**Regra das dependências:** cada camada só conhece as de baixo.

| Camada | Pode usar | Não pode usar |
|---|---|---|
| `controllers/` | services, models, domain, Flask | — |
| `services/` | models, domain | `request`, `session`, `flash`, templates |
| `models/` | domain, `extensions.db` | services, controllers |
| `domain/` | só a biblioteca padrão | Flask, SQLAlchemy |

Por isso os services e o domain podem ser testados direto no pytest, sem subir servidor.

## 3. Cada parte em detalhe

### App factory (`__init__.py`), `config.py` e `extensions.py`

- `create_app(config)` cria um app novo a cada chamada: liga o `db` e o `migrate`, carrega os
  modelos, registra os blueprints e o comando de carga. Os testes chamam
  `create_app(TestConfig)`; o `wsgi.py` chama `create_app()`.
- `config.py` lê `SECRET_KEY`, `DATABASE_URL` e `MODO_DEMO` do ambiente. Localmente vêm do `.env`;
  no CI e em produção, das variáveis do serviço. Nada de senha ou chave no código.
- `extensions.py` cria `db` e `migrate` sem app, para os modelos poderem importar o `db` sem
  importação circular. O vínculo com o app acontece dentro da factory (`db.init_app(app)`).

### `domain/`

| Arquivo | Conteúdo |
|---|---|
| `enums.py` | `Turno`, `EstadoSolicitacao` (os 6 estados do NF13.1), `UnidadeCobranca`, `OrdemBusca` (NF8.8) |
| `coordenada.py` | `Coordenada(latitude, longitude)`, imutável |

Evita texto solto (`"manha"`) e pares de floats soltos (obsessão por primitivos).

### `models/`

Um arquivo por classe do modelo conceitual da F2 (recorte do módulo):

| Modelo | Destaques |
|---|---|
| `Usuario` | conta; `.localizacao` devolve uma `Coordenada`; `.prestador` é o perfil de prestador ou `None` |
| `Prestador` | perfil 1:1 do usuário (`usuario_id` único, NF4.1); raio, indisponibilidade, ativo, nota |
| `Categoria` | as 7 do NF20.4 |
| `Servico` | do prestador, numa categoria; faixa de preço, unidade de cobrança, ativo |
| `Solicitacao` | do cliente para um serviço; nasce `PENDENTE` com a data de criação |

Os modelos guardam dados e o comportamento de **um objeto só** (ex.: `pode_cancelar()`). Regras
que envolvem vários objetos ficam nos services.

### `services/`

Regras do módulo, em funções Python que recebem tudo por parâmetro (inclusive a data de hoje) e
devolvem resultados ou erros: `distancia_service.py`, `busca_service.py`,
`pontuacao_service.py` e `solicitacoes_service.py`.

### `controllers/`

| Arquivo | Blueprint | Rotas |
|---|---|---|
| `saude_controller.py` | `saude` | `GET /saude` (health check) |
| `sessao_controller.py` | `sessao` | `/`, `/entrar`, `POST /entrar/<id>`, `POST /sair` |
| `busca_controller.py` | `busca` | `GET /busca` (Parte B) |
| `solicitacoes_controller.py` | `solicitacoes` | `/solicitacoes/nova/<servico_id>`, `/solicitacoes` (Parte A) |
| `__init__.py` | — | `registrar_blueprints(app)`: único lugar onde os blueprints entram no app |

`sessao_controller.py` também fornece o que as outras rotas usam:
- `usuario_logado()`: o `Usuario` da sessão, ou `None`;
- `@usuario_obrigatorio`: manda para `/entrar` quem não estiver logado;
- `usuario_atual`: disponível em todos os templates.

O "Entrar como" substitui o login (fora desta fase). Um login de verdade, no futuro, só muda este
arquivo: ele gravaria a mesma `session["usuario_id"]`.

### `views/` e `static/`

```
views/
├── base.html                  Bootstrap (CDN), menu, mensagens flash; todas as telas herdam dele
├── sessao/entrar.html         "Entrar como"
├── busca/index.html           T07 (Parte B)
└── solicitacoes/
    ├── nova.html              T09 (Parte A)
    └── lista.html             T12 (Parte A)
```

Um template de tela segue sempre o mesmo formato:

```html
{% extends "base.html" %}
{% block titulo %}Buscar prestadores{% endblock %}
{% block conteudo %}
  ...
{% endblock %}
```

Mensagens: `flash("texto", "erro")` aparece vermelha; `flash("texto", "sucesso")`, verde.
Números: `{{ distancia|numero }}` mostra `3,7` e `{{ preco|dinheiro }}` mostra `R$ 100,00`
(funções em `formatos.py`, registradas no `create_app`).
`static/` guarda arquivos usados pelas telas, referenciados com
`url_for('static', filename='...')`.

### Banco: `migrations/` e `seeds/`

- **Migrações** criam e alteram a **estrutura** (tabelas, colunas). Mudou um modelo:
  `flask db migrate -m "descrição"` gera o arquivo em `migrations/versions/`; confira e aplique com
  `flask db upgrade`. A migração vai no mesmo commit da mudança no modelo.
- **Seeds** preenchem o **conteúdo** simulado: `dados_simulados.py` tem só os dados,
  `carga.py` os transforma em objetos, e `flask carregar-dados` executa (não duplica se o banco
  já tiver dados).

### `tests/`

- `conftest.py`: fixtures `app`, `db` (banco criado do zero a cada teste) e `client`.
- `unit/`: services, domain e métodos dos modelos.
- `integration/`: rotas, usando o `client`.

### Qualidade e pipeline

- `pyproject.toml`: o ruff barra complexidade acima de 8, mais de 5 parâmetros, mais de 30 comandos
  por função e números mágicos (fora dos testes).
- `.github/workflows/ci.yml`, a cada push:
  - `lint`: ruff;
  - `testes`: Postgres 17 → migrações do zero → `flask db check` → uma única head → pytest.
  - reservados para a F5: `smells` e `deploy`.

## 4. Sugestão de implementação

Uma forma de encaixar cada parte na estrutura, cada uma mexendo só nos próprios arquivos:

| | Parte A – Solicitação (H01, H02) | Parte B – Busca e recomendação (H03, H04) |
|---|---|---|
| services | `solicitacoes_service.py` | `busca_service.py`, `distancia_service.py`, `pontuacao_service.py` |
| controller | `solicitacoes_controller.py` (já existe) | `busca_controller.py` (já existe) |
| views | `solicitacoes/nova.html`, `lista.html` | `busca/index.html` |
| métodos de modelo | `Solicitacao.pode_cancelar()`, `Servico.disponivel()`, `Servico.oferecido_por(usuario)` | `Prestador.indisponivel_em(data)`, `Prestador.alcanca(distancia)` |
| testes | `unit/test_solicitacoes_service.py`, `unit/test_modelos.py`, `integration/test_solicitacoes_rotas.py` | `unit/test_busca_service.py`, `unit/test_distancia_service.py`, `unit/test_modelos.py`, `unit/test_pontuacao_service.py`, `integration/test_busca_rotas.py` |

Ponto de integração: o botão "Solicitar" da busca aponta para a rota da Parte A:

```html
<a class="btn btn-primary" href="{{ url_for('solicitacoes.nova', servico_id=servico.id) }}">Solicitar</a>
```

Arquivos compartilhados (mexer só combinando com o grupo): atributos em `models/`, `domain/`,
`views/base.html`, `seeds/`, `migrations/`, `tests/conftest.py`, `pyproject.toml`, `.github/`.

As histórias, os requisitos de cada uma e onde estão os testes ficam no `README.md` (seção
"Histórias implementadas").
