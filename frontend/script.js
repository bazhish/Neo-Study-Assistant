let URL_BASE = "https://neo.onrender.com";  // link do Render

async function enviarArquivo() {
  let arquivo = document.getElementById("arquivo").files[0];
  let formData = new FormData();
  formData.append("file", arquivo);

  let resposta = await fetch(`${URL_BASE}/upload`, {
    method: "POST",
    body: formData
  });
  let dados = await resposta.json();
  addMessage(dados.mensagem, "neo");
}

async function fazerPergunta() {
  let pergunta = document.getElementById("pergunta").value;
  if (!pergunta) return;

  addMessage(pergunta, "user");
  document.getElementById("pergunta").value = "";

  let resposta = await fetch(`${URL_BASE}/pergunta`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({pergunta: pergunta})
  });
  let dados = await resposta.json();
  addMessage(dados.resposta, "neo");
}

async function resetarMemoria() {
  let resposta = await fetch(`${URL_BASE}/reset`, { method: "POST" });
  let dados = await resposta.json();
  addMessage(dados.mensagem, "neo");
}
