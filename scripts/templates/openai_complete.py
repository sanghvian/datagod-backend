from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv
chat = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0)
load_dotenv()
def openai_complete(prompt):
    template="You are an AI agent answering a question from a human. The human asks you the following question: ""{text}"". You are to answer the question in the following format: ""{content}"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="Give a answer in string format using the query and the context"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': prompt, 'content': 'Give a answer in string format using the query and the context'})
    return result
