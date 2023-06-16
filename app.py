from flask import Flask, request, jsonify
import openai
import os
import json
from flask_cors import CORS
from scripts.get_cloud_architecture import get_cloud_architecture
from scripts.get_system_diagram import return_infra_code,generate_diagram_image_and_upload_to_s3
from scripts.get_cloud_iac import return_iac_code
from scripts.generate_questions import return_questions
from scripts.iterate_cloud_architecture import iterate_cloudplan
from scripts.get_cloud_cost import calculate_cost_cloudplan
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


@app.route('/get-cloud-architecture', methods=['POST'])
def cloud_archi_generate():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = get_cloud_architecture(prompt)
    return jsonify(result), 200

@app.route('/get-system-diagram', methods=['POST'])
def system_diagram_generate():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = return_infra_code(prompt)
    img_url = generate_diagram_image_and_upload_to_s3(result, "cloudpilot-systems-design-diagrams")
    return jsonify({'img_url':img_url}), 200


@app.route('/get-cloud-iac', methods=['POST'])
def cloud_iac_code_gen():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = return_iac_code(prompt)
    return jsonify({'yaml-code':result}), 200

@app.route('/get-complete-cloud-architecture', methods=['POST'])
def cloud_complete_archi_generate():
    data = request.get_json()
    prompt = data.get('bizProb') + ". " + ". ".join(data.get('answers'))

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = get_cloud_architecture(prompt)
    return jsonify(result), 200

@app.route('/generate-questions', methods=['POST'])
def questions_gen():
    data = request.get_json()
    prompt = data.get('bizProb')

    if not prompt:
        return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = return_questions(prompt)
    return json.loads(result), 200


@app.route('/iterate-architecture', methods=['POST'])
def iterate_archi():
    data = request.get_json()
    bizProb = data.get('bizProb')
    recentArchitecture = data.get('recentArchitecture')
    constraint = data.get('constraint')

    # if not bizProb or not recentArchitecture or not constraint:
    #     return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = iterate_cloudplan(bizProb, json.dumps(recentArchitecture), constraint)
    return jsonify({'data':result}), 200

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()
    bizProb = data.get('bizProb')
    recentArchitecture = data.get('recentArchitecture')
    chatHistory = data.get('chatHistory')

    # if not bizProb or not recentArchitecture or not constraint:
    #     return jsonify({'error': 'Statement is missing'}), 400

    # Return the query result as JSON
    result = calculate_cost_cloudplan(bizProb, json.dumps(recentArchitecture),chatHistory)
    return json.loads(result), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
