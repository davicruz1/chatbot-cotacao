from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # libera para chamadas externas (ex: FlutterFlow)

# Rota raiz para teste
@app.route("/")
def home():
    return "✅ API de cotação de moedas e criptos funcionando 🚀"

@app.route("/cotacao/moeda")
def cotacao_moeda():
    codigo = request.args.get("codigo", "").upper()
    if not codigo:
        return jsonify({"error": "Parâmetro 'codigo' é obrigatório."}), 400

    url = f"https://api.exchangerate.host/latest?base={codigo}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"error": "Erro ao acessar API externa.", "details": str(e)}), 502

    rates = data.get("rates")
    if not rates:
        return jsonify({"error": "Moeda inválida ou dados não disponíveis."}), 400

    usd = rates.get("USD")
    brl = rates.get("BRL")
    eur = rates.get("EUR")

    if usd is None or brl is None or eur is None:
        return jsonify({"error": "Algumas cotações não foram encontradas."}), 400

    return jsonify({
        "base": data.get("base"),
        "rates": {
            "USD": usd,
            "BRL": brl,
            "EUR": eur
        }
    })

@app.route("/cotacao/cripto")
def cotacao_cripto():
    nome = request.args.get("nome", "").lower()
    if not nome:
        return jsonify({"error": "Parâmetro 'nome' é obrigatório."}), 400

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={nome}&vs_currencies=usd,brl"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"error": "Erro ao acessar API externa.", "details": str(e)}), 502

    if nome not in data:
        return jsonify({"error": "Criptomoeda inválida ou não encontrada."}), 400

    entry = data[nome]
    usd = entry.get("usd")
    brl = entry.get("brl")

    if usd is None or brl is None:
        return jsonify({"error": "Cotações não disponíveis para essa criptomoeda."}), 400

    return jsonify({
        "id": nome,
        "usd": usd,
        "brl": brl
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
