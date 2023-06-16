from scripts.kendra_index_retriever import KendraIndexRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain import OpenAI
import os
from dotenv import load_dotenv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import json
load_dotenv()
chat = ChatOpenAI(model_name='gpt-4', temperature=0)

nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokens = word_tokenize(text)
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words and token.isalnum()]
    preprocessed_text = ' '.join(filtered_tokens)
    return preprocessed_text


load_dotenv()

MAX_HISTORY_LENGTH = 6


def transform_json_string(json_string):
    data = json.loads(json_string)

    transformed_data = {
        "title": data["title"],
        "introduction": data["introduction"],
        "layers": []
    }

    for layer in data["layers"]:
        transformed_layer = {
            "title": layer["title"],
            "services": layer["services"],
            "purpose": layer["purpose"],
            "key_features": []
        }

        for feature in layer["key_features"]:
            transformed_feature = {
                "feature": feature["feature"],
                "explanation": feature["explanation"],
                "sourceDocuments": []
            }
            
            # Assuming you have source document information in the original JSON
            for source_doc in feature.get("sourceDocuments", []):
                transformed_source_doc = {
                    "source": source_doc["source"],
                    "title": source_doc["title"],
                    "excerpt": source_doc["excerpt"]
                }
                transformed_feature["sourceDocuments"].append(transformed_source_doc)

            transformed_layer["key_features"].append(transformed_feature)

        transformed_data["layers"].append(transformed_layer)

    return transformed_data



def restructure_answer(prompt):
    template="I want to extract and restructure the following content - ""{content}"" into the following JSON object form: The response should be STRICTLY in the following JSON format.{{title:string - name of the cloud architecture, introduction:string layers:[{{title:title string of layer, services: services used for this layer[], purpose:string, key_features:[{{ feature:string, explanation:string which explains the feature in about 50 words}}],}}].Give the answer response STRICTLY ONLY in the requested JSON format:"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="Strictly return code into the requested JSON format"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': prompt, 'content': prompt})
    return result

def build_chain():
    region = os.environ["AWS_REGION"]
    kendra_index_id = os.environ["KENDRA_INDEX_ID"]

    llm = OpenAI(model_name="gpt-4",
                 temperature=0, max_tokens=4000)

    retriever = KendraIndexRetriever(
        kendraindex=kendra_index_id,
        awsregion=region,
        k=6,
        return_source_documents=True
    )

    prompt_template = """I am providing business requirements - {question}. I want you to provide me with a technical cloud architecture solution document that details usage of which AWS cloud services to use, architecture, performance, speed and other important metrics for security, reliability,. From whatever limited information is given, your task is to suggest the best possible system design document for cloud infrastructure by leveraging cloud services. Feel free to choose any service from AWS. The answer should be at least 1500 words long with suitable headings and subheadings. The response should be STRICTLY in the following JSON format.{{title:string of the project, introduction:string layers:[{{title:title string of layer, services: services used for this layer[], purpose:string, key_features:[{{ feature:string, explanation:string which explains the feature in about 50 words, sourceDocuments:[{{ source:string URL which is the metadata source of the feature, title: string - title of the source document, excerpt: string - excerpt of the source document }}] }}],}}] - where each source document has a unique title, document, string,summary:string which has to be technically sound}}. Here's some background context for your reference {context}. Give the solution in the requested JSON format:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    return ConversationalRetrievalChain.from_llm(llm=llm,  retriever=retriever, condense_question_prompt=PROMPT, return_source_documents=True)


def run_chain(chain, prompt: str, history=[]):
    preprocessed_query_text = preprocess_text(prompt)[:1000]
    result = chain({"question": preprocessed_query_text, "chat_history": history})
    return result


def get_cloud_architecture(query):
    qa = build_chain()
    chat_history = []
    if (query.strip().lower().startswith("new search:")):
        query = query.strip().lower().replace("new search:", "")
        chat_history = []
    elif (len(chat_history) == MAX_HISTORY_LENGTH):
        chat_history.pop(0)
    result = run_chain(qa, query, chat_history)
    chat_history.append((query, result["answer"]))
    source_docs = []
    if 'source_documents' in result:
        for d in result['source_documents']:
            metadata = d.metadata
            json_document = {
                "source": metadata["source"],
                "title": metadata["title"],
                "excerpt": metadata["excerpt"]
            }
            source_docs.append(json_document)
    struc_answer = transform_json_string(restructure_answer(result['answer']))
    return {'data':struc_answer, 'source_docs': source_docs}

