# Planejamento Preliminar

## Planejamento de ciclos iterativos

| Ciclo | Casos de uso | Manutenção de informações | Consultas | Observações | Esforço estimado |
|:-:|---|---|---|---|:-:|
| 1 | Contratar serviço (250h) | Categoria (50h) | - | Parte do mecanismo de persistência (banco de dados geoespacial) e integração com a API de geocodificação (100h). Clientes e prestadores de teste inseridos por stubs. | 400 h |
| 2 | Tornar-se prestador (160h)<br>Responder solicitação (120h) | Usuário (80h) | - | Terminar de implementar o mecanismo de persistência (40h). | 400 h |
| 3 | Concluir serviço (100h)<br>Avaliar prestador (160h) | Serviço (70h)<br>Prestador (70h) | - | - | 400 h |
| 4 | Moderar denúncia (130h) | Solicitação (30h)<br>Avaliação (30h)<br>Denúncia (30h)<br>Administrador (30h) | Todas (150h) | - | 400 h |
| **Total** | | | | | **1600 h** |

Os casos de uso foram priorizados por risco: primeiro os processos de negócio, depois a manutenção de informações (CRUD) e, por último, as consultas, que dependem de dados já estruturados. “Contratar serviço” vem no ciclo 1 por ser o núcleo do Bicus e o ponto de maior incerteza técnica (geolocalização, busca por raio e ranking). Nesse ciclo, clientes e prestadores ainda não podem se cadastrar pelo sistema (o cadastro de usuários entra no ciclo 2), então dados de teste são inseridos por stubs.

## Cronograma para o desenvolvimento

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

**Obs.:** A estimativa considera uma equipe de 3 integrantes trabalhando 8 horas por dia útil: 1 analista-projetista e 2 programadores-testadores. Cada ciclo soma 400 horas: Análise (10 dias × 1 pessoa × 8h = 80h) + Projeto (10 × 1 × 8h = 80h) + Implementação (10 × 2 × 8h = 160h) + Testes (5 × 2 × 8h = 80h). Os 4 ciclos totalizam 1.600 horas em 100 dias úteis (cerca de 20 semanas). Cada ciclo dura 8 semanas (o ciclo 4, sem a etapa de correções, dura 7). Os 5 dias de “Correções / folga” (C) não entram nas 400 horas de cada ciclo: funcionam como reserva.

Os ciclos se sobrepõem: enquanto os programadores implementam e testam um ciclo, o analista-projetista já trabalha na análise e no projeto do ciclo seguinte. Os 5 dias de “Correções / folga” (C) acomodam correções de defeitos e mudanças de requisitos antes do início da implementação seguinte. Após concluir o projeto do ciclo 4, o analista-projetista prepara a implantação (manual do usuário e testes de aceitação).