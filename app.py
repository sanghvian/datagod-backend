# External modules
import os
import json
import openai
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from langchain.document_loaders import PyPDFLoader, UnstructuredImageLoader, UnstructuredPowerPointLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
import pinecone

# Custom modules
from scripts.get_rag_answer import get_rag_answer
from scripts.openai_complete import openai_complete


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

@app.route('/custom-index', methods=['POST'])
def process_file():
    # Save the uploaded file
    file = request.files['file']
    file_type = request.form['file_type']
    file_name = secure_filename(file.filename)
    file.save(os.path.join('/tmp', file_name))

    # Determine the file loader based on file type
    if file_type == '.pdf':
        loader = PyPDFLoader(file_path=file_name)
    elif file_type == '.jpg':
        loader = UnstructuredImageLoader(file_path=file_name)
    elif file_type == '.ppt':
        loader = UnstructuredPowerPointLoader(file_path=file_name)
    else:
        return 'Unsupported filie type', 400

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=2048, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    # initialize pinecone
    pinecone.init(
        api_key=os.environ.get("PINECONE_API_KEY"),
        environment="asia-southeast1-gcp-free"
)
    index_name = "chat-verlab"
    # pinecone_index = pinecone.Index(index_name=index_name)

    # print("Creating 🍍 index...")
    Pinecone.from_documents(docs, embeddings, index_name=index_name)

    return 'File successfully processed and indexed', 200



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
