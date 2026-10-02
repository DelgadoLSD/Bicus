# 4. Planejamento Preliminar

## 4.1. Planejamento de ciclos iterativos

| Ciclo | Casos de uso | Manutenção de informações | Consultas | Observações | Esforço estimado |
|:-:|---|---|---|---|:-:|
| 1 | Contratar serviço (250h) | Categoria (50h) | - | Parte do mecanismo de persistência (banco de dados geoespacial) e integração com a API de geocodificação (100h). Prestadores de teste inseridos por stubs. | 400 h |
| 2 | Tornar-se prestador (160h)<br>Responder solicitação (120h) | Usuário (80h) | - | Terminar de implementar o mecanismo de persistência (40h). | 400 h |
| 3 | Concluir serviço (100h)<br>Avaliar prestador (160h) | Serviço (70h)<br>Prestador (70h) | - | - | 400 h |
| 4 | Moderar denúncia (130h) | Solicitação (30h)<br>Avaliação (30h)<br>Denúncia (30h)<br>Administrador (30h) | Todas (150h) | - | 400 h |
| **Total** | | | | | **1600 h** |

Os casos de uso foram priorizados por risco: primeiro os processos de negócio, depois a manutenção de informações (CRUD) e, por último, as consultas, que dependem de dados já estruturados. “Contratar serviço” vem no ciclo 1 por ser o núcleo do Bicus e o ponto de maior incerteza técnica (geolocalização, busca por raio e ranking). Nesse ciclo, os prestadores ainda não podem se cadastrar pelo sistema, então dados de teste são inseridos por stubs.

## 4.2. Cronograma para o desenvolvimento

| Dias | 1-5 | 6-10 | 11-15 | 16-20 | 21-25 | 26-30 | 31-35 | 36-40 | 41-45 | 46-50 | 51-55 | 56-60 | 61-65 | 66-70 | 71-75 | 76-80 | 81-85 | 86-90 | 91-95 | 96-100 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Ciclo 1 | A | A | P | P | I | I | T | C |  |  |  |  |  |  |  |  |  |  |  |  |
| Ciclo 2 |  |  |  |  | A | A | P | P | I | I | T | C |  |  |  |  |  |  |  |  |
| Ciclo 3 |  |  |  |  |  |  |  |  | A | A | P | P | I | I | T | C |  |  |  |  |
| Ciclo 4 |  |  |  |  |  |  |  |  |  |  |  |  | A | A | P | P | I | I | T |  |
| Implantação |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Impl. |

**Legenda:** Análise (A); Projeto (P); Implementação (I); Testes (T); Correções / folga (C); Implantação (Impl.).

| Fase | Responsável(is) | Cor |
|---|---|---|
| Análise (A) e Projeto (P) | Hugo Costa Araújo (analista-projetista) | Vermelho |
| Implementação (I) | Lucas Silva Delgado e Luis Felipe Martins Pereira (programadores-testadores) | Amarelo |
| Testes (T) | Lucas Silva Delgado e Luis Felipe Martins Pereira | Azul |
| Correções / folga (C) | Lucas Silva Delgado e Luis Felipe Martins Pereira | Cinza |
| Implantação | Toda a equipe | Verde |

**Obs.:** A estimativa considera uma equipe de 3 integrantes trabalhando 8 horas por dia útil: 1 analista-projetista e 2 programadores-testadores. Cada ciclo soma 400 horas: Análise (10 dias × 1 pessoa × 8h = 80h) + Projeto (10 × 1 × 8h = 80h) + Implementação (10 × 2 × 8h = 160h) + Testes (5 × 2 × 8h = 80h). Os 4 ciclos totalizam 1.600 horas em 100 dias úteis (cerca de 20 semanas), com cada ciclo durando 7 semanas.

Os ciclos se sobrepõem: enquanto os programadores implementam e testam um ciclo, o analista-projetista já trabalha na análise e no projeto do ciclo seguinte. Os 5 dias de “Correções / folga” (C) acomodam correções de defeitos e mudanças de requisitos antes do início da implementação seguinte. Após concluir o projeto do ciclo 4, o analista-projetista prepara a implantação (manual do usuário e testes de aceitação).

## 4.3. Prioridade para melhores práticas do RUP

**1. Desenvolva software iterativamente**

O valor do Bicus depende de uma regra que só pode ser validada com uso real: a ordenação dos prestadores por proximidade e nota. Entregar o sistema em ciclos permite que, ao fim de cada ciclo, clientes e prestadores façam testes de aceitação, e que pesos, raios e prazos sejam ajustados antes que o restante do sistema dependa deles.

**2. Gerencie requisitos**

O sistema atende a dois públicos com interesses diferentes (quem contrata e quem presta o serviço) e reúne muitas regras de negócio marcadas como transitórias, como prazos da solicitação, fórmula de pontuação e limites de busca. Manter os requisitos documentados e rastreados até os casos de uso permite avaliar o impacto de cada mudança.

**3. Verifique continuamente a qualidade**

A proposta do Bicus é oferecer informações confiáveis. Um defeito que permita avaliar sem ter contratado o serviço, ou que distorça o ranking, compromete a confiança na plataforma. Por isso, as regras de avaliação, reputação e permissões devem ser testadas em todos os ciclos, e não apenas no final.

**4. Controle as mudanças**

Vários requisitos foram marcados como transitórios (APIs externas, raio de busca, fórmula de pontuação e ausência de pagamento intermediado). Mudanças nesses pontos devem passar por um processo de solicitação que avalie viabilidade e impacto antes de serem incorporadas.

**5. Use arquiteturas baseadas em componentes**

As interfaces web e mobile consomem a mesma API (S3), e os serviços externos de CEP e geocodificação devem ficar isolados em componentes próprios, para que possam ser trocados sem afetar o restante do sistema.

**6. Modele visualmente o software**

Os diagramas UML (casos de uso e modelo conceitual) mantêm a equipe alinhada sobre o domínio. Por ser uma equipe pequena, com comunicação direta, esta prática recebe a menor prioridade.
