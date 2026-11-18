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
