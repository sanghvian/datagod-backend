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
def return_iac_code(prompt):
    template="I want to create an Infrastructure as Code - 'AWS CloudFormation' template for the following cloud solution as follows: ""{content}"". Generate a string of code to make the diagram in python. Just return ONLY the CloudFormation YAML code as a STRING in your answer response and no other data AT ALL. Think of the technical requirements, specifications for this and come up with a cloud solution and generate its Cloudformation YAML template for the following requirements and solutions, and return the ONLY the STRING response of YAML code and no extra string data of any sort"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="Strictly return only the CloudFormation YAML code in string format and no other extra string data"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': prompt, 'content': 'Strictly return only the CloudFormation YAML code in string format and no other extra string data'})
    return result
