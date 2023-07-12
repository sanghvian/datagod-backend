from scripts.kendra_index_retriever import KendraIndexRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import json
load_dotenv()


chat = ChatOpenAI(model_name='gpt-4-0613', temperature=0)

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    tokens = word_tokenize(text)
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words and token.isalnum()]
    preprocessed_text = ' '.join(filtered_tokens)
    return preprocessed_text

MAX_HISTORY_LENGTH = 6


# def transform_json_string(json_string):
#     data = json.loads(json_string)

#     transformed_data = {
#         "answer": data["answer"]
#     }

#     # Assuming you have source document information in the original JSON
#     for source_doc in data("source_documents"):
#         transformed_source_doc = {
#             "source": source_doc["source"],
#             "title": source_doc["title"],
#             "excerpt": source_doc["excerpt"]
#         }
#         transformed_feature["sourceDocuments"].append(transformed_source_doc)

#     transformed_layer["key_features"].append(transformed_feature)

#     return transformed_data



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

    retriever = KendraIndexRetriever(
        kendraindex=kendra_index_id,
        awsregion=region,
        k=6,
        return_source_documents=True
    )

    prompt_template = """
        You are a chatbot answering questions over enterprise data. Here's the question you have been asked - {question}. From whatever limited information is given, your task is to retrieve the relevant documents and generate an answer. The response should be STRICTLY in the following JSON format.
            {{
                answer: answer string,
                source_documents:[{{ source:string URL which is the metadata source of the feature, title: string - title of the source document, excerpt: string - excerpt of the source document }}] - where each source document has a unique title, document, string,summary:string which has to be technically sound
            }}. 
        
        Here's some background context for your reference {context}. Give the solution in the requested JSON format:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    return ConversationalRetrievalChain.from_llm(
        llm=chat,  
        retriever=retriever, 
        condense_question_prompt=PROMPT, 
        return_source_documents=True
    )


def run_chain(chain, prompt: str, history=[]):
    preprocessed_query_text = preprocess_text(prompt)[:1000]
    result = chain({"question": preprocessed_query_text, "chat_history": history})
    return result


def get_rag_answer(query):
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
    
    # struc_answer = transform_json_string(restructure_answer(result['answer']))
    return {'data':result['answer'], 'source_docs': source_docs}

