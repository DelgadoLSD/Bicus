# Bicus – Contratação de serviço

Implementação de um módulo do **Bicus**, marketplace de bicos e pequenos serviços locais, feita na
disciplina INF323 – Engenharia de Software II (UFV).

O módulo cobre o fluxo principal do cliente:

1. Busca de prestadores por categoria, perto do cliente, ordenada pela pontuação de recomendação.
2. Envio de uma solicitação de serviço.
3. Lista das próprias solicitações, com cancelamento das pendentes.

Cadastro, login, área do prestador e avaliações pertencem a outros módulos e não foram
implementados. Para o fluxo funcionar, o sistema vem com dados simulados:

- clientes de exemplo, escolhidos na tela "Entrar como" (sem senha), no lugar do login;
- prestadores, serviços e categorias, com nota média e número de avaliações já definidos;
- coordenadas fixas dos endereços (em Viçosa), no lugar de um serviço de geolocalização.

**Grupo:** Hugo Costa Araújo, Lucas Silva Delgado e Luis Felipe Martins Pereira.

## Como rodar

_(a preencher na Etapa 0: instalação das dependências, carga dos dados iniciais e comando para
subir o servidor)_

## Testes

_(a preencher na Etapa 0: comando do pytest)_
