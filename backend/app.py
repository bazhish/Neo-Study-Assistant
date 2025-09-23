from flask import Flask, request, jsonify
from leitor import ler_arquivo
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from memoria import carregar_memoria, salvar_memoria
import os

import subprocess
import sys

# Função que instala pacotes automaticamente
def instalar_dependencias():
    try:
        import flask, transformers, torch, sentence_transformers, docx, pandas, openpyxl, pptx, PyPDF2
    except ImportError:
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

instalar_dependencias()


app = Flask(__name__)
UPLOAD_FOLDER = "backend/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Carrega memória no início
memoria = carregar_memoria()

# Modelos
modelo_embeddings = SentenceTransformer("all-MiniLM-L6-v2")
gerador = pipeline("text2text-generation", model="google/flan-t5-small")

# --- UPLOAD ---
@app.route("/upload", methods=["POST"])
def upload_file():
    global memoria
    if "file" not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"erro": "Nome de arquivo inválido"})
    caminho = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(caminho)

    conteudo = ler_arquivo(caminho)
    trechos = [p for p in conteudo.split("\n") if p.strip()]
    memoria["arquivos"][file.filename] = trechos

    # Criar resumo geral
    prompt = f"Resuma de forma clara o seguinte conteúdo:\n{conteudo[:2000]}"
    resumo = gerador(prompt, max_length=200, do_sample=False)[0]["generated_text"]
    memoria["resumo"] += f"\nResumo de {file.filename}: {resumo}"

    salvar_memoria(memoria)
    return jsonify({"mensagem": f"Arquivo {file.filename} carregado e processado com sucesso!"})

# --- PERGUNTA ---
@app.route("/pergunta", methods=["POST"])
def pergunta():
    global memoria
    dados = request.get_json()
    pergunta = dados.get("pergunta", "")

    if not memoria["arquivos"]:
        return jsonify({"resposta": "Nenhum arquivo carregado ainda."})

    # Junta todos os trechos
    todos_trechos = []
    for nome, trechos in memoria["arquivos"].items():
        todos_trechos.extend(trechos)

    # Busca trecho mais relevante
    emb_pergunta = modelo_embeddings.encode(pergunta, convert_to_tensor=True)
    emb_trechos = modelo_embeddings.encode(todos_trechos, convert_to_tensor=True)
    similaridades = util.cos_sim(emb_pergunta, emb_trechos)[0]
    melhor_indice = int(similaridades.argmax())
    trecho = todos_trechos[melhor_indice]

    # Contexto com histórico e resumos
    contexto = "\n".join([f"Você: {h['pergunta']} | Neo: {h['resposta']}" for h in memoria["historico"][-3:]])
    prompt = f"""
    Contexto anterior:
    {contexto}

    Resumo global dos arquivos:
    {memoria['resumo']}

    Pergunta atual: {pergunta}
    Trecho mais relevante: {trecho}

    Responda de forma clara e explicativa:
    """
    resposta = gerador(prompt, max_length=180, do_sample=True)[0]["generated_text"]

    # Atualiza histórico e salva
    memoria["historico"].append({"pergunta": pergunta, "resposta": resposta})
    salvar_memoria(memoria)

    return jsonify({"resposta": resposta})

@app.route("/reset", methods=["POST"])
def reset():
    global memoria
    memoria = {"arquivos": {}, "resumo": "", "historico": []}
    salvar_memoria(memoria)
    return jsonify({"mensagem": "Memória da Neo apagada com sucesso!"})


if __name__ == "__main__":
    app.run(debug=True)
