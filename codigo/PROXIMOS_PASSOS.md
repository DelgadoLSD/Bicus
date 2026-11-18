# Próximos passos — Parte B (H03 e H04)

Branch: `h03-busca`. Critérios completos em `F4 - Implementação/Plano da F4.txt`, seção 4.

## Onde estamos

- [x] Tela de busca (T07): categoria + raio, tabela de resultados, botão "Solicitar" (→ Parte A)
- [x] `services/distancia_service.py`: `distancia_km(origem, destino)`, Haversine (NF8.2)
- [x] `services/busca_service.py`: `buscar_prestadores(categoria_id, cliente, raio_km)`
  - no banco (`where`): categoria, serviço ativo, perfil ativo, não é o próprio usuário
  - no Python (`for`): distância ≤ raio da busca
- [x] Controller passa `resultados` (tuplas `prestador, servico, distancia`) para o template

## H03 — falta

1. **Indisponibilidade (NF8.3)**
   - método `Prestador.indisponivel_em(data) -> bool` no model (a regra é do prestador)
   - a busca recebe a data de hoje por parâmetro (`hoje: date`), para o teste não depender do relógio
2. **Raio de deslocamento do prestador (NF8.3)**
   - descartar quem tem `distancia > raio_deslocamento_km`
   - decidir com o grupo: `raio_deslocamento_km = None` significa "sem limite"?
3. **Testes unitários** (`tests/unit/`)
   - `test_distancia_service.py`: distância entre dois pontos conhecidos; mesmo ponto = 0
   - `test_busca_service.py`, um teste por regra:
     - fora do raio da busca
     - raio de deslocamento não alcança o cliente
     - prestador indisponível
     - perfil desativado / serviço inativo
     - o próprio usuário fora da lista
4. **Muitos parâmetros**: com `hoje`, a função chega a 4 parâmetros. Se passar de 5 (limite do ruff),
   agrupar numa dataclass `FiltroBusca`

## H04 — pontuação

- `services/pontuacao_service.py`:
  `0,6 × (nota / 5) + 0,4 × (1 − distância / raio)`; sem avaliação → nota 3,0 (constantes com nome)
- trocar a tupla por uma dataclass `ResultadoBusca(prestador, servico, distancia_km, pontuacao)`
- ordenar pela pontuação (maior primeiro); empate → mais próximo
- testes: ordenação, prestador sem avaliação

## Antes do PR

- [ ] `ruff check .` e `pytest` passando
- [ ] critérios do H03 conferidos na tela (entrar como Ana e como Bruno)
- [ ] PR com "Closes #N" → aprovação → Actions verde → "Rebase and merge"

## Observações

- NF5.4 (um serviço por categoria por prestador) não é garantido pelo banco; avaliar
  `UniqueConstraint("prestador_id", "categoria_id")` em `Servico` (arquivo compartilhado: combinar com o grupo)
- Arquivos renomeados nesta branch: `*_controller.py` e `*_service.py`; avisar a Parte A
