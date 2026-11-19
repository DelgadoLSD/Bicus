// Data desejada: campo "dd/mm/aaaa" que aceita digitar ou escolher num calendário (flatpickr).
// O cliente vê e digita dd/mm/aaaa; o servidor recebe aaaa-mm-dd. Dias antes de hoje
// (data-minimo, vindo do servidor) ficam bloqueados; o servidor confere de novo (NF11.2).
const campoData = document.querySelector("[data-calendario]");

// Lê "dd/mm/aaaa" (o que o cliente digita) ou "aaaa-mm-dd" (o que vem do servidor) e só aceita
// datas que existem: 31/02 é recusado, em vez de virar 03/03.
function lerData(texto, formato) {
  const [a, b, c] = texto.split(/[-/]/).map(Number);
  const [dia, mes, ano] = formato === "Y-m-d" ? [c, b, a] : [a, b, c];
  const data = new Date(ano, mes - 1, dia);
  const existe =
    data.getFullYear() === ano && data.getMonth() === mes - 1 && data.getDate() === dia;
  return existe ? data : undefined;
}

if (campoData) {
  const erro = document.querySelector('[data-campo="erro-data"]');
  const botaoCalendario = document.querySelector("[data-abrir-calendario]");
  const calendario = flatpickr(campoData, {
    locale: "pt",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "d/m/Y",
    altInputClass: "form-control",
    allowInput: true,
    clickOpens: false, // o calendário só abre pelo botão ao lado do campo
    ignoredFocusElements: [botaoCalendario], // clicar no botão não conta como "clicar fora"
    static: true, // calendário dentro do modal: o modal do Bootstrap não deixa o foco sair dele
    minDate: campoData.dataset.minimo,
    parseDate: lerData,
    onChange: () => mostrarErro(false),
  });
  botaoCalendario.addEventListener("click", () => calendario.toggle());
  const campoVisivel = calendario.altInput;
  let digitado = "";

  function mostrarErro(ativo) {
    campoVisivel.classList.toggle("is-invalid", ativo);
    erro.hidden = !ativo;
  }

  // Máscara: o cliente digita só os números e as barras aparecem sozinhas (25112026 -> 25/11/2026).
  campoVisivel.inputMode = "numeric";
  campoVisivel.addEventListener("input", () => {
    digitado = campoVisivel.value.replace(/\D/g, "").slice(0, 8);
    const partes = [digitado.slice(0, 2), digitado.slice(2, 4), digitado.slice(4)];
    campoVisivel.value = partes.filter(Boolean).join("/");
    mostrarErro(false);
  });

  // Ao sair do campo o flatpickr lê o que foi digitado; se não virou uma data aceita, avisa.
  campoVisivel.addEventListener("blur", () => {
    mostrarErro(digitado !== "" && calendario.selectedDates.length === 0);
  });
}

// Abre o modal de nova solicitação quando a página vem da busca (?servico=<id>).
// O template só gera o modal nesse caso e o marca com data-abrir="sim".
const modalNovaSolicitacao = document.getElementById("nova-solicitacao");

if (modalNovaSolicitacao?.dataset.abrir === "sim") {
  new bootstrap.Modal(modalNovaSolicitacao).show();
}

// Modal de confirmação do cancelamento: um só para a página inteira.
// Ao abrir, copia do botão clicado a rota (data-acao) e o nome do serviço (data-servico).
const modalCancelamento = document.getElementById("confirmar-cancelamento");

modalCancelamento?.addEventListener("show.bs.modal", (evento) => {
  const botao = evento.relatedTarget;
  modalCancelamento.querySelector("form").action = botao.dataset.acao;
  modalCancelamento.querySelector('[data-campo="servico"]').textContent = botao.dataset.servico;
});
