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

        # Se a API retorna erro (ex: {"success": false, ...})
        if not data.get("success", True):
            return jsonify({"error": f"Moeda '{codigo}' inválida ou não suportada."}), 400

    except Exception as e:
        return jsonify({"error": "Erro ao acessar API externa.", "details": str(e)}), 502

    rates = data.get("rates")
    if not rates:
        return jsonify({"error": f"Moeda '{codigo}' inválida ou dados não disponíveis."}), 400

    # Só pega moedas que existem no retorno
    retorno = {k: rates.get(k) for k in ["USD", "BRL", "EUR"] if k in rates}

    if not retorno:
        return jsonify({"error": "Nenhuma das moedas desejadas foi encontrada."}), 400

    return jsonify({
        "base": data.get("base"),
        "rates": retorno
    })
