from flask import Flask, request, jsonify
import openai
import os
import json
from flask_cors import CORS
from scripts.get_rag_answer import get_rag_answer
from scripts.openai_complete import openai_complete
from dotenv import load_dotenv

load_dotenv()

# Set up Google Cloud credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials.json"

app = Flask(__name__)
CORS(app)
# TODO - Apply CORS properly else openai will be fucked
# CORS(app, origins=["http://localhost:3000", "https://example.com"])

app.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY


@app.route('/hello', methods=['GET'])
def hello():
    return 'active', 200

@app.route('/chat', methods=['POST'])
def get_ans_and_docs():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = get_rag_answer(prompt)
    return jsonify(result), 200

@app.route('/llm', methods=['POST'])
def questions_gen():
    data = request.get_json()
    prompt = data.get('bizProb')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = openai_complete(prompt)
    return json.loads(result), 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
