# Próximos passos da F4 (entrega: 22/11)

Estado do módulo "Contratar serviço" e o que falta para fechar as histórias. Critérios completos em
`docs/F4 - Implementação/Plano da F4.txt`, seção 4. Estrutura do código em `ESTRUTURA.md`.

Quase tudo que falta é lógica interna (services, models e testes). Nenhum item exige tela nova:
os efeitos aparecem nas telas que já existem (quem aparece na busca, a ordem da lista e as mensagens
de erro em vermelho, via `flash`).

## Como está hoje

O fluxo completo funciona: **Entrar como → Buscar → Solicitar → modal → Minhas solicitações → Cancelar**.

| Arquivo | O que faz |
|---|---|
| `services/distancia_service.py` | `distancia_km(origem, destino)`: Haversine (NF8.2) |
| `services/busca_service.py` | `buscar_prestadores(categoria_id, cliente, raio_km, hoje)` → lista de `ResultadoBusca`, com todos os filtros do NF8.3 (H03) e já ordenada pela recomendação (H04) |
| `services/pontuacao_service.py` | `calcular_pontuacao(nota, distancia, raio)`: a fórmula do F9 |
| `services/solicitacoes_service.py` | `criar_solicitacao` (H01, com as regras), `listar_solicitacoes`, `cancelar_solicitacao` e a exceção `SolicitacaoInvalidaError` |
| `models/solicitacao.py` | `Solicitacao.pode_cancelar()` |
| `controllers/busca_controller.py` | `GET /busca` |
| `controllers/solicitacoes_controller.py` | `GET /solicitacoes` (lista + modal se vier `?servico=`), `POST /solicitacoes` (criar), `POST /solicitacoes/<id>/cancelar` |
| `views/solicitacoes/lista.html` | lista, selos coloridos por estado e modal de confirmação do cancelamento |
| `views/solicitacoes/nova.html` | modal de nova solicitação (incluído na lista) |
| `static/js/solicitacoes.js` | abre o modal de nova solicitação e preenche o de cancelamento |

## O que falta

### 1. Testes unitários (prioridade: o professor exige a suíte)

As quatro histórias (H01 a H04) estão testadas, em `tests/unit/` e `tests/integration/`. Cada
teste monta só os dados de que precisa, com as funções de `tests/fabricas.py`
(`criar_usuario`, `criar_prestador`, `criar_servico`, `nova_solicitacao` e `ponto_ao_norte`, que
cria um ponto a uma distância exata do Centro) e as fixtures
`app` e `db` do `tests/conftest.py` (banco SQLite em memória). Datas sempre por parâmetro, nunca
`date.today()`. Rodar: `.\.venv\Scripts\pytest`.

- ~~`tests/unit/test_distancia_service.py` e `tests/unit/test_busca_service.py`: um teste por
  regra da busca~~ (feito)
- ~~`tests/unit/test_solicitacoes_service.py`: validações do H01; lista e cancelamento do H02~~
  (feito)

### 2. H01: validações ao criar a solicitação (feito)

`criar_solicitacao(cliente, dados, hoje)` em `solicitacoes_service.py`, com os dados do formulário
em `DadosSolicitacao`. Recusa com `SolicitacaoInvalidaError` e mensagem: campos obrigatórios
(NF11.1), serviço inexistente/inativo ou prestador desativado, data anterior a hoje (NF11.2), o
próprio serviço (NF11.3, `Servico.oferecido_por`) e mais de `LIMITE_PENDENTES` = 10 pendentes
(NF11.5). Endereço vazio usa o do cliente. A rota mostra a mensagem em vermelho e reabre o modal.

### 3. H03: filtros que faltam na busca (feito)

A busca recebe `hoje` e descarta, além do que já descartava, quem está indisponível hoje
(`Prestador.indisponivel_em`, NF6.2, primeiro e último dia inclusos) e quem não se desloca até o
cliente (`Prestador.alcanca`, NF4.3; raio vazio = qualquer distância). A tabela mostra os números
no formato brasileiro e a nota com estrela (`bicus/formatos.py`).

### 4. H04: pontuação e ordenação (feito)

`calcular_pontuacao` em `services/pontuacao_service.py`: `0,6 × (nota / 5) + 0,4 × (1 −
distância / raio)`, com sem avaliação = nota 3,0 (pesos e nota neutra em constantes com nome). A
busca devolve `ResultadoBusca(prestador, servico, distancia_km, pontuacao)` ordenados pela
pontuação; no empate, mais avaliações e depois o mais próximo (`ordenar_por_recomendacao`, NF9.2).
Nos dados simulados, Helena e Rosa (Faxina) mostram a ordem funcionando.

### 5. Fechamento

- [ ] `ruff check .` e `pytest` passando localmente e no Actions
- [ ] README: fluxo do modal e o que ficou fora do escopo (grade semanal do F6 e filtros por
      dia/turno do NF8.6)
- [ ] commits citando a história (`H01: ...`, `H03: ...`), direto na `main`
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
