# External modules
import os
import json
import openai
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from langchain.document_loaders import PyPDFLoader, UnstructuredImageLoader, UnstructuredPowerPointLoader, Docx2txtLoader, TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
import pinecone

# Custom modules
from scripts.get_rag_answer import get_rag_answer
from scripts.openai_complete import openai_complete
from scripts.pinecone_retriever import pine_retrieve


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
    prompt = data.get('query')

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
    source_url = request.form['source_url']
    file_name = secure_filename(file.filename)
    file_path = '/tmp/' + file_name
    file.save(os.path.join('/tmp', file_name))

    # Determine the file loader based on file type
    if file_type == '.pdf':
        loader = PyPDFLoader(file_path=file_path)
    elif file_type == '.jpg':
        loader = UnstructuredImageLoader(file_path=file_path)
    elif file_type == '.ppt':
        loader = UnstructuredPowerPointLoader(file_path=file_path)
    elif file_type == '.docx' or file_type == '.doc':
        loader = Docx2txtLoader(file_path=file_path)
    elif file_type == '.txt':
        loader = TextLoader(file_path=file_path)
    else:
        return 'Unsupported file type', 400

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=2048, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    try:
        # initialize pinecone
        pinecone.init(
            api_key=os.environ.get("PINECONE_API_KEY"),
            environment="asia-southeast1-gcp-free"
        )
        index_name = "chat-verlab"
        # Create metadata for your file
        metadata = {
            "source_url": source_url,
            "file_type": file_type,
            # add other metadata as needed
        }
        # pinecone_index = pinecone.Index(index_name=index_name)
        Pinecone.from_documents(
            docs, 
            embeddings, 
            index_name=index_name, 
            metadata=metadata,
            source_url=source_url,
        )
        
        # Remove the file from the '/tmp' directory
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'status': 'success', 'code': 200}), 200
    except Exception as e:
        # Remove the file from the '/tmp' directory even if an error occurred
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/pinechat', methods=['POST'])
def pinechat():
    data = request.get_json()
    english_statement = data.get('query')
    if not english_statement:
        return jsonify({'error': 'Query is missing'}), 400
    
    # Return the query result as JSON
    data = pine_retrieve(english_statement)
    answer = data
    response = {
        'answer':answer
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
