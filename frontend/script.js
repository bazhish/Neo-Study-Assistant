function addMessage(texto, tipo) {
  let chat = document.getElementById("chat");
  let msg = document.createElement("div");
  msg.classList.add("msg", tipo === "user" ? "msg-user" : "msg-neo");
  msg.innerText = texto;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

async function enviarArquivo() {
  let arquivo = document.getElementById("arquivo").files[0];
  let formData = new FormData();
  formData.append("file", arquivo);

  let resposta = await fetch("http://127.0.0.1:5000/upload", {
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

  let resposta = await fetch("http://127.0.0.1:5000/pergunta", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({pergunta: pergunta})
  });
  let dados = await resposta.json();
  addMessage(dados.resposta, "neo");
}

async function resetarMemoria() {
  let resposta = await fetch("http://127.0.0.1:5000/reset", {
    method: "POST"
  });
  let dados = await resposta.json();
  addMessage(dados.mensagem, "neo");
}