# Próximos passos da F4 (entrega: 22/11)

Estado do módulo "Contratar serviço" e o que falta para fechar as histórias. Critérios completos em
`F4 - Implementação/Plano da F4.txt`, seção 4. Estrutura do código em `ESTRUTURA.md`.

Quase tudo que falta é lógica interna (services, models e testes). Nenhum item exige tela nova:
os efeitos aparecem nas telas que já existem (quem aparece na busca, a ordem da lista e as mensagens
de erro em vermelho, via `flash`).

## Como está hoje

O fluxo completo funciona: **Entrar como → Buscar → Solicitar → modal → Minhas solicitações → Cancelar**.

| Arquivo | O que faz |
|---|---|
| `services/distancia_service.py` | `distancia_km(origem, destino)`: Haversine (NF8.2) |
| `services/busca_service.py` | `buscar_prestadores(categoria_id, cliente, raio_km)` → lista de `(prestador, servico, distancia)` |
| `services/solicitacoes_service.py` | `listar_solicitacoes`, `cancelar_solicitacao` e a exceção `SolicitacaoInvalidaError` |
| `models/solicitacao.py` | `Solicitacao.pode_cancelar()` |
| `controllers/busca_controller.py` | `GET /busca` |
| `controllers/solicitacoes_controller.py` | `GET /solicitacoes` (lista + modal se vier `?servico=`), `POST /solicitacoes` (criar), `POST /solicitacoes/<id>/cancelar` |
| `views/solicitacoes/lista.html` | lista, selos coloridos por estado e modal de confirmação do cancelamento |
| `views/solicitacoes/nova.html` | modal de nova solicitação (incluído na lista) |
| `static/js/solicitacoes.js` | abre o modal de nova solicitação e preenche o de cancelamento |

## O que falta

### 1. Testes unitários (prioridade: o professor exige a suíte)

Hoje não há nenhum teste. Cada teste monta só os dados de que precisa (fixtures `app` e `db` do
`tests/conftest.py`, banco SQLite em memória). Datas sempre por parâmetro, nunca `date.today()`.

- `tests/unit/test_distancia_service.py`: dois pontos conhecidos; mesmo ponto = 0
- `tests/unit/test_busca_service.py`: um teste por regra
  - fora do raio da busca
  - próprio usuário fora da lista
  - perfil desativado; serviço inativo
  - (depois do item 3) prestador indisponível; raio de deslocamento que não alcança o cliente
- `tests/unit/test_solicitacoes_service.py`
  - lista só as do cliente, a mais recente primeiro
  - cancelar pendente → Cancelada
  - cancelar solicitação de outro cliente → erro
  - cancelar solicitação que não está pendente → erro
  - (depois do item 2) as validações do H01

### 2. H01: validações ao criar a solicitação

Hoje a rota `criar` monta a `Solicitacao` e grava direto, sem validar nada. Mover para o service:

- `criar_solicitacao(cliente, dados, hoje) -> Solicitacao` em `solicitacoes_service.py`, com os
  dados do formulário numa dataclass `DadosSolicitacao` (evita muitos parâmetros)
- regras, cada uma levantando `SolicitacaoInvalidaError` com a mensagem para o usuário:
  - campos obrigatórios: serviço, descrição, data desejada e turno (NF11.1)
  - data desejada ≥ hoje (NF11.2)
  - não solicitar o próprio serviço: `servico.prestador.id == cliente.id` (NF11.3)
  - no máximo 10 solicitações pendentes por cliente (NF11.5)
- a rota fica: `try` → `criar_solicitacao(...)` → `flash` de sucesso; `except SolicitacaoInvalidaError`
  → `flash(str(erro), "erro")` e `redirect` para `/solicitacoes?servico=<id>` (o modal reabre sozinho)

### 3. H03: filtros que faltam na busca (NF8.3)

- **indisponibilidade**: método `Prestador.indisponivel_em(data) -> bool` no model; a busca recebe
  `hoje` por parâmetro e descarta quem está indisponível
- **raio de deslocamento**: descartar quem tem `distancia > prestador.raio_deslocamento_km`
  (decidir: `None` = sem limite?)
- os dois entram no `for` de `buscar_prestadores` (são regras em Python, não no `where`)
- se a função passar de 5 parâmetros (limite do ruff), agrupar numa dataclass `FiltroBusca`

### 4. H04: pontuação e ordenação

- `services/pontuacao_service.py`: `0,6 × (nota / 5) + 0,4 × (1 − distância / raio)`; sem
  avaliação → nota 3,0 (constantes com nome, nada de número solto)
- trocar a tupla da busca por uma dataclass `ResultadoBusca(prestador, servico, distancia_km, pontuacao)`
  e ajustar o `{% for %}` do `busca/index.html`
- ordenar pela pontuação (maior primeiro); empate → mais próximo
- testes: ordenação; prestador sem avaliação

### 5. Fechamento

- [ ] `ruff check .` e `pytest` passando localmente e no Actions
- [ ] README: fluxo do modal e o que ficou fora do escopo (grade semanal do F6 e filtros por
      dia/turno do NF8.6)
- [ ] commits citando a história (`H01: ...`, `H03: ...`), PR para a `main`, "Rebase and merge"
- [ ] teste do fluxo completo, entrando como Ana e como Bruno

## Combinados do código

- **Nomes de arquivo**: `*_controller.py` em `controllers/` e `*_service.py` em `services/`
- **Regras no service**, não no controller. O controller só lê a requisição, chama o service e
  escolhe a resposta
- **Erros de regra** = `SolicitacaoInvalidaError("mensagem")` no service; o controller mostra com `flash`
- **JavaScript só em `static/js/`**, carregado pelo `{% block scripts %}`; dados do servidor vão
  por atributos `data-*` no HTML, nunca `<script>` com código dentro do template
- **Depois de todo POST, `redirect`** (evita reenviar o formulário no F5)
- **Banco**: categorias vêm da migração (`flask db upgrade`); usuários e serviços de exemplo vêm do
  `flask carregar-dados`. Mudou modelo → `flask db migrate`, conferir o arquivo, `flask db upgrade`

## Observações

- NF5.4 (um serviço por categoria por prestador) não é garantido pelo banco; avaliar
  `UniqueConstraint("prestador_id", "categoria_id")` em `Servico`
