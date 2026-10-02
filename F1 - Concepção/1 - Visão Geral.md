# 1. Visão Geral do Sistema

**Sistema:** Bicus — Marketplace online de bicos e pequenos serviços locais  
**Disciplina:** INF323 – Engenharia de Software II (Prof. Lucas Francisco da Matta Vegi)  
**Equipe:** Hugo Costa Araújo (112684); Lucas Silva Delgado (112685); Luis Felipe Martins Pereira (112710)

## 1.1. Problema

Quem presta pequenos serviços, como jardinagem, aulas particulares, pequenos reparos domésticos, faxina e reforço escolar, costuma divulgar seu trabalho de maneira informal: indicações boca a boca, grupos de WhatsApp e Facebook ou redes sociais pessoais. Para quem precisa contratar um serviço pontual, encontrar um prestador de confiança é um processo lento, baseado em recomendações de conhecidos ou em informações dispersas na internet. Também não é possível verificar rapidamente se o prestador está próximo, qual é o seu histórico de avaliações, sua disponibilidade e a qualidade dos serviços já realizados.

Essa falta de organização prejudica os dois lados. Prestadores novos, sem uma rede de indicações estabelecida, têm dificuldade em conseguir os primeiros trabalhos, mesmo sendo qualificados. Clientes acabam recorrendo sempre ao mesmo prestador por falta de uma forma fácil de comparar alternativas.

## 1.2. Proposta

O Bicus é uma plataforma online (web e mobile) que aproxima clientes e prestadores de pequenos serviços locais. Prestadores se cadastram informando categoria de atuação, descrição do serviço, faixa de preço e localização. Ao buscar por uma categoria, o cliente recebe a lista de prestadores daquela categoria dentro de um raio de distância configurável a partir da sua localização, ordenada pela combinação de proximidade geográfica e nota média das avaliações anteriores. Após a conclusão de cada serviço, o cliente avalia o prestador, alimentando um histórico de reputação que passa a fazer parte do processo de recomendação.

Principais funcionalidades:

- Cadastro de usuários e ativação de perfil de prestador, com serviços, faixa de preço, localização e disponibilidade;
- Busca de prestadores por categoria dentro de um raio configurável, com ordenação por proximidade e reputação;
- Solicitação de serviço ao prestador, com aceite ou recusa e liberação do contato após o aceite;
- Registro de conclusão do serviço e avaliação do prestador pelo cliente (nota e comentário);
- Histórico de reputação usado na recomendação, incluindo tratamento justo para prestadores novos;
- Denúncia de conteúdo inadequado e moderação pelo administrador.

## 1.3. Atores

| Ator | Descrição |
|---|---|
| **Cliente** | Qualquer pessoa cadastrada que busca e contrata serviços. Busca prestadores, envia solicitações, confirma a conclusão e avalia o prestador. |
| **Prestador** | Cliente que ativou um perfil de prestador. Além de contratar serviços, cadastra os serviços que oferece, define sua disponibilidade, responde às solicitações e registra a conclusão dos serviços. Na UML, é uma especialização do ator Cliente. |
| **Administrador** | Membro da equipe do Bicus. Mantém as categorias de serviço e modera as denúncias de conteúdo inadequado. |

## 1.4. Escopo

**Contemplado nesta versão:**

- Cadastro e autenticação de usuários; perfil de prestador, serviços oferecidos e disponibilidade;
- Busca geográfica por categoria e raio, com ranking por proximidade e nota;
- Ciclo da solicitação de serviço (envio, aceite/recusa, conclusão, cancelamento);
- Avaliação do prestador, reputação e resposta do prestador à avaliação;
- Denúncias, moderação e manutenção de categorias.

**Fora do escopo desta versão:**

- Pagamento intermediado pela plataforma: preço e pagamento são combinados diretamente entre cliente e prestador (ver S8);
- Chat interno: após o aceite, a conversa segue pelo telefone/WhatsApp liberado pelo sistema;
- Avaliação do cliente pelo prestador;
- Verificação de documentos ou antecedentes dos prestadores;
- Cálculo de rotas reais: a distância considerada é em linha reta.
