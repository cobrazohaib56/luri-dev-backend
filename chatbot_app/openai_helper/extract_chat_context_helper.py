from langchain.memory import ChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def extract_prompt_template(is_custom_prompt, custom_prompt):
    
    if is_custom_prompt and custom_prompt != "Chat":
        custom_prompt = f"You must put special emphasis on the theme {custom_prompt} and tailor your responses according to this theme"
    else:
        custom_prompt = ""
        
    template = f"""
        You are a legal assistant specializing in providing detailed and accurate responses and write drafts to legal inquiries based on the provided case data and your training dataset. Always give a response and make it long and detailed according to your training data. For each type of case, ensure to cover all relevant aspects and legal principles. Do not make it a letter. Make it a legal document.{custom_prompt}
        Current conversation:
        {{history}}
        Human: {{input}} 
    """
        
    # print("Template: ", template)

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )
    
    return prompt
        
    

def extract_chathistory_langchain_format(chat_list):
    history = ChatMessageHistory()
    for chat in chat_list:
        type = chat["type"]
        if type == "server":
            history.add_ai_message(chat["message"])
        else:
            history.add_user_message(chat["message"])
    return history