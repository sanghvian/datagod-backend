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
def calculate_cost_cloudplan(bizProb, recentArchitecture,chatHistory):
    template="""Here is the business problem: {bizProb}. You are a cloud architect and you have been asked to design a system to solve this problem.
    Here is the architecture already designed: {recentArchitecture} and here's the conversation for improving it, made between human and AI: {chatHistory}. I know you can't use real-time pricing so perform step by step rough cost estimate of the same and approximately tell the total annual cost of the cloud architecture proposed. STRICTLY Return ONLY a JSON object of the form {{totalCost: number value containing the total cost of the architecture, stepByStepCost: string array containing the cost of each step of the architecture}}. No need to give accurate realtime costs, just return the approximate cost in the JSON format asked"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="STRICTLY Return ONLY a JSON object of the form {{totalCost: number value containing the total cost of the architecture, stepByStepCost: string array containing the cost of each step of the architecture}}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': "STRICTLY Return ONLY a JSON object of the form {{totalCost: number value containing the total cost of the architecture, stepByStepCost: string array containing the cost of each step of the architecture}}", 'bizProb': bizProb, 'recentArchitecture': recentArchitecture, 'chatHistory': chatHistory})
    return result
