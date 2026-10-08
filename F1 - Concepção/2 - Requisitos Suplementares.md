# Requisitos suplementares

Restrições que se aplicam ao sistema como um todo, e não a uma função específica.

| Nome | Restrição | Categoria | Desejável | Permanente |
|---|---|---|:---:|:---:|
| **S1** Interface web | O sistema terá uma interface web responsiva, que se adapta a telas de computadores e smartphones e pode ser usada pelo navegador, sem necessidade de instalação. | Interface | ( ) | (X) |
| **S2** Aplicativo mobile | O sistema terá também um aplicativo nativo para smartphones (Android e iOS), com as mesmas funcionalidades da versão web. | Interface | (X) | ( ) |
| **S3** Idade mínima | O sistema deve ser usado somente por maiores de 18 anos. | Legal | ( ) | (X) |
| **S4** Proteção de dados pessoais | O tratamento de dados pessoais deve seguir a Lei Geral de Proteção de Dados: coleta apenas dos dados necessários, finalidade informada, consentimento e direito de acesso, correção e exclusão. | Legal | ( ) | (X) |
| **S5** Segurança das senhas | As senhas são armazenadas apenas na forma de hash, com algoritmo próprio para senhas. | Segurança | ( ) | (X) |
| **S6** Intermediação do serviço | A plataforma apenas aproxima clientes e prestadores: não processa pagamentos nem se responsabiliza pela execução do serviço. Preço e forma de pagamento são combinados diretamente entre as partes, conforme os Termos de Uso. | Legal | ( ) | ( ) |
| **S7** Idioma e formatos | Interface em português do Brasil; valores em reais, datas no formato dd/mm/aaaa e distâncias em quilômetros. | Interface | ( ) | (X) |
| **S8** Distribuição | A versão web será hospedada em um serviço de nuvem. | Empacotamento | (X) | ( ) |
