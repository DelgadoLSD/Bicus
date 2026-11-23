# Bicus – F4: módulo Contratação de serviço

Trabalho da disciplina INF323 – Engenharia de Software II (UFV), fase F4.

**Integrantes:** Hugo Costa Araújo, Lucas Silva Delgado e Luis Felipe Martins Pereira.

O tema do projeto está em [Tema do Projeto.pdf](Tema%20do%20Projeto.pdf).

## Como rodar o site

É preciso ter **Python 3.14** e **git**.

**Windows (PowerShell):**

```powershell
git clone https://github.com/DelgadoLSD/Bicus.git
cd Bicus\codigo
py -3.14 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\flask db upgrade
.venv\Scripts\flask carregar-dados
.venv\Scripts\flask run
```

**Linux ou macOS:**

```bash
git clone https://github.com/DelgadoLSD/Bicus.git
cd Bicus/codigo
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/flask db upgrade
.venv/bin/flask carregar-dados
.venv/bin/flask run
```

Depois, abra http://127.0.0.1:5000 no navegador. Para parar o servidor, use Ctrl+C no terminal.
Nas próximas vezes, basta o último comando (`flask run`).

O `flask db upgrade` cria o banco (SQLite, no arquivo `codigo/instance/bicus.db`) e o
`flask carregar-dados` coloca nele os dados de exemplo. Para recomeçar do zero, apague esse
arquivo e rode os dois comandos de novo.

Cadastro e login não fazem parte do módulo: a tela inicial, **Entrar como**, lista usuários de
exemplo. Um bom caminho para ver tudo: entre como **Ana**, busque **Faxina** com raio de **5 km**,
troque a ordem clicando em Preço, Avaliação ou Distância, clique em **Solicitar** numa das
prestadoras e, depois, veja e cancele o pedido em **Minhas solicitações**.

## Como rodar os testes

Dentro da pasta `codigo`, com o ambiente acima já criado:

```powershell
.venv\Scripts\pytest        # Windows
.venv/bin/pytest            # Linux ou macOS
```

Os testes unitários das regras ficam em `tests/unit` e os testes das páginas em
`tests/integration`. Cada teste cria o próprio banco, em memória, então eles não dependem do
banco do site nem dos dados de exemplo. Para o lint, que confere o estilo e a complexidade do
código: `.venv\Scripts\ruff check .` (ou `.venv/bin/ruff check .`).

## Onde está cada coisa

- [codigo/README.md](codigo/README.md): as histórias implementadas, com os requisitos e os testes
  de cada uma, o que é simulado, o que ficou fora do escopo e as decisões tomadas.
- [codigo/ESTRUTURA.md](codigo/ESTRUTURA.md): a organização do código em camadas e o papel de
  cada pasta.
- `.github/workflows/ci.yml`: roda o lint e os testes a cada push.
