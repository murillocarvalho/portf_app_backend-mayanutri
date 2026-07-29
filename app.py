from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)
# Allow all origins during development to avoid CORS blocking from the frontend
CORS(app)

@app.route("/insert", methods=["POST"])
def insert():
    # accept JSON or form data
    payload = None
    if request.is_json:
        payload = request.get_json()
    else:
        payload = request.form

    usuario = payload.get('usuario') if payload else None
    if not usuario:
        return jsonify({"success": False, "message": "Campo 'usuario' obrigatório"}), 400

    try:
        response = supabase.table("HelloWorld").insert({"name": usuario}).execute()
        return jsonify({"success": True, "message": "Usuário inserido com sucesso!", "data": response.data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Erro ao inserir usuário", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)