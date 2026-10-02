# F1 – Concepção do Bicus

> **⚠️ ATENÇÃO – gerador e Markdown desatualizados (02/10/2026)**
>
> O documento oficial agora é o **`Bicus - F1 Concepção.docx`** (e o `.pdf` gerado a partir dele), editado diretamente no Word.
> A pasta `_gerador/` e os arquivos `.md` correspondem a uma versão anterior do conteúdo e **não refletem mais o documento**.
> **Não rode o `gerar.py`**: ele sobrescreve o `.docx` e os diagramas com o conteúdo antigo.
> O diagrama `diagramas/modelo_conceitual` (.svg/.png) já está atualizado e igual ao do documento.


Entrega da fase de **Concepção (RUP)**: análise e especificação de requisitos do Bicus, no formato do `Docs/Exemplo_Concepção.pdf` e de acordo com a aula *"Análise e especificação de requisitos funcionais e não-funcionais"* (Wazlawick).

## O que tem nesta pasta

| Arquivo | Para quê |
|---|---|
| **Bicus - F1 Concepção.docx** | Documento final, editável, no formato do exemplo (capa, sumário, seções 1 a 4). Para entregar em PDF: no Word, *Arquivo > Salvar como > PDF*. |
| `1 - Visão Geral.md` | Problema, proposta, atores e escopo. |
| `2.1 - Requisitos Funcionais.md` | F1–F20 com os seus NFs, índice e resumo; inclui um **exemplo numérico do ranking** (F9). |
| `2.2 - Requisitos Suplementares.md` | S1–S15. |
| `3 - Organização dos Requisitos.md` | Casos de uso, diagramas, conceitos (CRUD), consultas e uma **matriz de rastreabilidade**, que serve só para conferência. |
| `4 - Planejamento Preliminar.md` | Ciclos iterativos, cronograma e prioridades do RUP. |
| `diagramas/` | Diagrama de casos de uso e modelo conceitual (`.svg` editável e `.png`). |
| `_gerador/` | Fonte única do conteúdo (`conteudo.py`) e scripts que regeneram tudo. |

Os `.md` existem para facilitar a revisão, seção por seção. O conteúdo deles é idêntico ao do `.docx`, porque os dois são gerados da mesma fonte.

## Números da especificação

- **20 requisitos funcionais**: 3 deles são ocultos (F7 localização, F9 pontuação, F15 reputação).
- **104 requisitos não-funcionais**.
- **15 requisitos suplementares**.
- **6 casos de uso**: Contratar serviço, Responder solicitação, Concluir serviço, Avaliar prestador, Tornar-se prestador e Moderar denúncia.
- **8 conceitos** e **6 consultas**.
- **4 ciclos de 400 h**, totalizando 1.600 h em 100 dias úteis.

Todos os F estão rastreados em pelo menos um caso de uso, conceito ou consulta (o "ALERTA" do slide 41). O gerador confere isso automaticamente.

## Decisões que tomei e que o grupo precisa validar

O tema não definia estes pontos, então tive que escolher:

1. **Conta única.** Todo usuário é cliente e pode "virar" prestador (F4). No exemplo, cada tipo de usuário era escolhido no cadastro. Aqui, uma mesma pessoa pode contratar e prestar serviços. No diagrama, isso aparece como **Prestador especializando Cliente**.
2. **Ciclo da solicitação (F11–F13).** O tema diz que o cliente avalia "após a conclusão de cada serviço". Para garantir que só avalia quem realmente contratou, criei o fluxo *solicitar → aceitar/recusar → concluir → confirmar → avaliar*, com os estados definidos em NF13.1.
3. **Ator Administrador.** Não aparece no tema. Incluí para manter as categorias (F20) e moderar denúncias (F18/F19).
4. **Sem chat e sem pagamento.** O contato é liberado após o aceite, com atalho para o WhatsApp (NF12.3 e NF12.5). A plataforma não intermedia pagamento (S8, marcado como *transitório* justamente por poder mudar no futuro).
5. **Fórmula do ranking (F9).** Combina distância e uma **nota ajustada por média bayesiana**, com pesos configuráveis. Resolve o problema do "prestador novo" descrito no tema: sem avaliações, ele recebe a média da plataforma em vez de zero. O exemplo numérico está em `2.1 - Requisitos Funcionais.md`.
6. **Valores arbitrados.** Raio de 1 a 50 km (padrão 10 km), expiração em 72 h, confirmação automática em 7 dias, 30 dias para avaliar, limites de caracteres etc. Ajustem à vontade.
7. **Categoria "Especificação" nos NF.** Usei essa categoria para regras de negócio puras (ex.: NF5.7, NF9.1). Ela aparece no exemplo do Wazlawick que está nos slides da aula (slide 27). As demais categorias seguem a tabela do slide 20.
8. **Obrigatoriedade no cabeçalho dos F.** O slide 25 da aula cita "obrigatoriedade" também para requisitos funcionais, mas o exemplo só marca *Oculto*. Mantive o formato do exemplo. Se quiserem, dá para acrescentar "Desejável ( )" no cabeçalho de cada F.
9. **Cronograma.** Segue a mesma premissa do exemplo (8 h/dia). Os papéis foram atribuídos pela ordem dos nomes no tema: **Hugo** como analista-projetista; **Lucas** e **Luis Felipe** como programadores-testadores. Troquem se preferirem.
10. **Linguagem e tecnologias.** Não fixei a linguagem de programação. Se já tiverem decidido (há um `main.py` na raiz do projeto), vale acrescentar um requisito suplementar de *Implementação*, como no exemplo da aula ("O sistema deve ser desenvolvido com a linguagem…").
11. **Numeração das seções.** O exemplo pula de 3.2 para 3.4. Aqui a numeração é sequencial (3.1 a 3.5).

## Como alterar

- **Pequenos ajustes de texto:** editem direto o `.docx` no Word.
- **Mudanças estruturais** (novo requisito, renumeração, novo caso de uso): editem `_gerador/conteudo.py` e rodem os comandos abaixo. Os códigos NF são renumerados sozinhos, e o gerador avisa se alguma referência cruzada quebrar.

```
cd "_gerador"
python gerar.py                                                # gera .md, diagramas e .docx
powershell -ExecutionPolicy Bypass -File atualizar_sumario.ps1 # preenche o sumário no Word
```

(Se preferirem, em vez do script: abram o .docx, cliquem com o botão direito no sumário e escolham *Atualizar campo*.)

Atenção: regenerar sobrescreve o `.docx`. Edições feitas à mão no Word se perdem, a menos que sejam repassadas também para o `conteudo.py`.
