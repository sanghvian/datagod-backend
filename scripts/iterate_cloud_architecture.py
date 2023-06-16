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
def iterate_cloudplan(bizProb, recentArchitecture, constraint):
    template="""Here is the business problem: {bizProb}. You are a cloud architect and you have been asked to design a system to solve this problem.
    Here is the architecture already designed: {recentArchitecture}. Now, you have been told that the system must have the following constraint: {constraint}.
    Please update the architecture to meet this constraint."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="Strictly return the answer to the question and nothing else"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result= chain.run({'text': "Improve the given cloud architecture", 'bizProb': bizProb, 'recentArchitecture': recentArchitecture, 'constraint': constraint})
    return result
