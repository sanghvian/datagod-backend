from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv
chat = ChatOpenAI(model_name='gpt-4', temperature=0)
load_dotenv()
def openai_complete(prompt):
    template="""Business Issue: {content}This is the input given by an engineer regarding a business problem. You have to help him find the best cloud services to leverage. You have to generate three questions, which are atleast 50 words long to gain more context about the problem before addressing it. Do not ask any questions regarding budget. The response should be strictly in the following JSON format without any preceding number:{{questions:string[]}} The questions should not have preceding numbers."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="Strictly return the questions in the asked format and nothing else"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': prompt, 'content': 'Strictly return the questions in the asked format and nothing else'})
    return result
