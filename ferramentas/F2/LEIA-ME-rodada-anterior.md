# F2 – Análise de Pontos de Função do Bicus

Entrega da fase **F2**: protótipos das telas principais, medição do tamanho funcional por Análise de Pontos de Função (APF) e projeção de tempo e custo. Segue a aula *"Métricas – Análise de Pontos de Função"* e o exemplo `Docs/MediçãoAPF - sistema locadora.pdf`.

Como pede o enunciado, o documento é **integrado ao da fase anterior**: contém toda a F1 e, em seguida, as seções novas.

As seções da F2 trazem só **resultados e critérios** (listas e tabelas), sem explicar o método ao professor. As explicações para o grupo ficam neste LEIA-ME.

## O que tem nesta pasta

| Arquivo | Para quê |
|---|---|
| **Bicus - F2 Análise de Pontos de Função.docx** | Documento final (F1 + F2). Para entregar em PDF: no Word, *Arquivo > Salvar como > PDF*. |
| `1 - Protótipos.md` | As 9 pranchas de protótipos, com a lista de telas (T01 a T29). |
| `2 - Contagem de Pontos de Função.md` | Critérios, modelo conceitual revisado (figura, alterações em relação à F1, tipos e enumerações), todas as funções com AR/TD listados um a um, PFB, fator de ajuste e PFA. Também traz uma tabela de rastreabilidade RF → funções, só para conferência (não vai no documento). |
| `3 - Estimativas.md` | Parâmetros com o critério de cada um, cenários de produtividade, projeção adotada (fórmula e cálculo) e comparação com o planejamento da F1. |
| `prototipos/` | Pranchas em `.svg` (editável) e `.png`. |
| `diagramas/` | Modelo conceitual revisado, com herança, multiplicidades, o código de cada ALI e a AIE da geocodificação (`.svg` e `.png`). |
| `_gerador/` | `conteudo_f2.py` (dados da contagem), `prototipos.py` (desenho das telas) e `gerar.py`. |

## Resultado

| Etapa | Valor |
|---|---|
| Funções de dados | 8 ALI + 1 AIE = 61 PF |
| Funções de transação | 48 EE (173 PF) + 17 CE (62 PF) + 8 SE (45 PF) |
| **PFB** | **341** |
| Com margem de 30% | 444 |
| NI / FA | 35 / 1,00 |
| **PFA** | **444 pontos de função** |
| **Projeção realista** | 4.107 h · 10,53 meses com 3 pessoas · **R$ 232.126,80** |

## Pontos para o grupo validar

1. **Convenções do professor.** Segui o exemplo da locadora ao pé da letra: menus e botões *Voltar* de telas de listagem contam como EE com 0 AR (como `MenuPrincipal` e `FecharGenero`); mensagens de alerta, botões dos alertas e o botão que abre o formulário (*Novo*, *Editar*) contam como TD. Isso soma 11 EEs de *Voltar* (33 PF brutos, cerca de 10% do total), proporção parecida com a do exemplo dele.
2. **Escopo completo.** A contagem inclui os requisitos desejáveis (filtros da busca, mapa, WhatsApp etc.), porque mede o sistema especificado.
3. **AIE de geocodificação.** A API externa do F7 foi contada como AIE, como o slide 27 permite ("tabelas que armazenam dados referenciados pela aplicação (APIs)").
4. **Telas de administradores (T28/T29).** Não há RF específico: derivei do CRUD completo de *Administrador* na tabela de Conceitos da F1. Se não quiserem essas telas, saem EE44–EE47 e CE16–CE17 (18 PF brutos a menos).
5. **Expiração automática (EE48).** É um processo sem tela, disparado pelo relógio (NF11.7).
6. **Produtividade de 9,25 h/PF.** É o ponto médio da faixa das linguagens orientadas a objeto da tabela da aula. Supus Python no servidor e JavaScript/TypeScript nas interfaces (há um `main.py` na raiz). Se a stack já estiver definida, ajustem a justificativa.
7. **Gastos extras.** São estimativas: hospedagem R$ 300/mês, internet e energia R$ 450/mês, contas nas lojas R$ 700 e domínio R$ 40. O valor da hora (R$ 45) e o lucro (20%) vêm da aula.
8. **Comparação com a F1.** No fim das estimativas há uma linha mostrando que a APF dá cerca de 2,6 vezes as 1.600 h do planejamento preliminar da Concepção. Pode ser removida se o grupo preferir.
9. **Modelo revisado só na F2.** A seção da F1 continua com o modelo preliminar, como foi entregue. A F2 traz o modelo revisado e uma tabela com cada alteração e o requisito que a justifica. Se preferirem, dá para trocar o modelo também na seção da F1.
10. **Regra de AR.** Agora o AR conta as leituras exigidas pelos requisitos: validações como "não excluir com solicitações em andamento" e o e-mail do destinatário das notificações. O professor faz isso no exemplo da locadora (`DelGenero`, 2 AR). Antes essas leituras ficavam de fora, e incluí-las levou o PFB de 325 para 341.
11. **Prazo da suspensão.** O modelo guarda `fimSuspensao` (NF19.3), mas a tela de moderação (T24) não tem campo de prazo. A proposta é ter prazos fixos na lista de medidas, por exemplo "suspender por 7 dias" e "suspender por 30 dias". Confirmem.
12. **O que não entrou no modelo.** Os tokens dos links de confirmação de e-mail e de redefinição de senha, e o e-mail novo enquanto não é confirmado (NF3.2), ficaram de fora: são dados técnicos dos links, não dados do negócio.

## Modelo conceitual revisado

Revisei o modelo preliminar contra todos os RF/NF, os suplementares, a tabela de conceitos, as consultas e as telas. As principais mudanças:

- **Prestador herda de Usuário.** No modelo preliminar era uma associação "atua como". Pela regra da aula, os dois ALIs ficam com TR = 2: a superclasse conta a subclasse e a subclasse conta a superclasse.
- **Atributos que faltavam:**
  - Usuário: senha, aceite dos termos, situação da conta (no lugar de `ativo`) e fim da suspensão;
  - Solicitação: quem cancelou e o registro de conclusão feito pelo prestador;
  - Avaliação: marcação de removida;
  - Administrador: senha e ativo.
- **A associação "mantém" saiu**, porque a categoria não guarda quem a mantém.
- **Multiplicidades e domínios:** todas as associações têm multiplicidade e todas as enumerações têm o domínio listado.

O gerador garante a coerência entre o desenho e a contagem:
- os TDs de cada ALI são calculados a partir do próprio modelo (atributos da classe mais FKs) e o TR, a partir da herança;
- toda enumeração tem domínio e todo tipo composto está definido;
- todos os conceitos da F1 têm classe no modelo;
- as linhas do desenho terminam nas bordas das caixas certas.

Se o modelo mudar em `conteudo_f2.py`, a figura, a tabela de ALIs e a contagem acompanham ao regerar.

## Como alterar

- **Pequenos ajustes de texto:** editem direto o `.docx` no Word.
- **Mudar a contagem** (uma função, um TD, um NI, a produtividade): editem `_gerador/conteudo_f2.py` e rodem:

```
cd "_gerador"
python gerar.py
```

O script recalcula complexidades, PFB, PFA e estimativas, refaz as pranchas e o documento inteiro, e avisa se algo ficar inconsistente: AR inexistente, tela sem função, RF da F1 sem nenhuma função APF etc.

- **Mudanças na F1:** a parte da F1 deste documento vem do gerador da F1, sem cópia. Depois de alterar e regerar a F1, rodem também o `gerar.py` da F2 para atualizar o documento integrado.

Atenção: regenerar sobrescreve o `.docx`. Edições feitas à mão no Word se perdem, a menos que sejam repassadas para o `conteudo_f2.py`.
