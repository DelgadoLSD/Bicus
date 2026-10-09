# F1 – Concepção do Bicus

Entrega da fase de **Concepção (RUP)**: análise e especificação de requisitos do Bicus, no formato do `Docs/Exemplo_Concepção.pdf` e de acordo com a aula *"Análise e especificação de requisitos funcionais e não-funcionais"* (Wazlawick).

## O que tem nesta pasta

| Arquivo | Para quê |
|---|---|
| **Bicus - F1 Concepção.docx** | Documento final, editável. Para entregar em PDF: no Word, *Arquivo > Salvar como > PDF*. |
| `1 - Requisitos Funcionais.md` | F1–F20 com os seus NFs, índice e resumo. |
| `2 - Requisitos Suplementares.md` | S1–S8. |
| `3 - Organização dos Requisitos.md` | Casos de uso, diagramas, conceitos (CRUD), consultas e uma **matriz de rastreabilidade**, que serve só para conferência. |
| `4 - Planejamento Preliminar.md` | Ciclos iterativos e cronograma. |
| `diagramas/` | Diagrama de casos de uso e modelo conceitual (`.svg` editável e `.png`). |
| `_gerador/` | Fonte única do conteúdo (`conteudo.py`) e o script que gera tudo (`gerar.py`). |

Os `.md` existem para facilitar a revisão, seção por seção. O conteúdo deles é idêntico ao do `.docx`, porque os dois são gerados da mesma fonte (`conteudo.py`).

## Como o documento está organizado hoje

Capa → Concepção (Requisitos funcionais, Requisitos suplementares) → Organização dos requisitos (Casos de Uso, diagramas, Conceitos, Consultas) → Planejamento Preliminar (ciclos, cronograma). Sem sumário e sem uma seção de "Visão Geral" separada — o documento começa direto nos requisitos, como no `Exemplo_Concepção.pdf`.

## Números da especificação

- **20 requisitos funcionais**: 3 deles são ocultos (F7 localização, F9 pontuação, F15 reputação).
- **84 requisitos não-funcionais**.
- **8 requisitos suplementares**.
- **6 casos de uso**: Contratar serviço, Responder solicitação, Concluir serviço, Avaliar prestador, Tornar-se prestador e Moderar denúncia.
- **8 conceitos** e **6 consultas**.
- **4 ciclos de 400 h**, totalizando 1.600 h em 100 dias úteis.

Todos os F estão rastreados em pelo menos um caso de uso, conceito ou consulta (o "ALERTA" do slide 41). O gerador confere isso automaticamente.

## Histórico — como chegamos aqui

A primeira versão foi toda gerada por mim (Claude). O Luis Felipe revisou e editou o `.docx` diretamente no Word (commit `920619c`, 02/10/2026): ajustou o modelo conceitual, os conceitos, as consultas e o planejamento, cortou vários requisitos não-funcionais e removeu a seção "Visão Geral do Sistema", o Sumário e a "4.3 Prioridade para melhores práticas do RUP". Em 08/10/2026, a pedido do Lucas, sincronizei `conteudo.py`/`gerar.py` com esse estado, extraindo o texto exato do `.docx` (não reconstruí de memória). O texto removido (Visão Geral, Atores, Escopo, RUP) continua arquivado em `conteudo.py`, nas constantes terminadas em `_ARQUIVADO`, caso o grupo decida restaurar algo depois.

## Como alterar

- **Pequenos ajustes de texto:** editem direto o `.docx` no Word.
- **Mudanças estruturais** (novo requisito, novo caso de uso, renumeração): editem `_gerador/conteudo.py` e rodem:

```
cd "_gerador"
python gerar.py
```

Isso gera `.md`, diagramas e `.docx` de uma vez, já com o sumário/numeração conferidos e as referências cruzadas validadas (o script avisa se algo quebrar).

Atenção: regenerar sobrescreve o `.docx`. Edições feitas à mão no Word se perdem, a menos que sejam repassadas também para o `conteudo.py`.
