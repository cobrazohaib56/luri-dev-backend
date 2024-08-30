from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from chatbot_app.utils import required_env_var
from chatbot_app.openai_helper.extract_chat_context_helper import extract_chathistory_langchain_format, extract_prompt_template

def send_chat_request_gpt(chat_list, is_custom_prompt, custom_prompt):
    llm = ChatOpenAI(
        openai_api_key=required_env_var("CHATGPT_SECRET"),
        model='gpt-4o-mini',
        temperature=0.2
    )


    list_of_chat = chat_list[:-1]
    history = extract_chathistory_langchain_format(list_of_chat)
    # custom_prompt = custom_prompt
    
    memory = ConversationBufferWindowMemory(
        chat_memory = history,
        k=6,
        ai_prefix="God"
    )

    prompt = extract_prompt_template(is_custom_prompt, custom_prompt)
    conversation_buffer = ConversationChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory
    )
    
    recent_query_from_user = chat_list[-1]
    message = recent_query_from_user["message"]
    result = conversation_buffer(message)
    # print(conversation_buffer.prompt.template)
    # result = conversation_buffer({"custom_prompt": custom_prompt, "history": history, "input": message})
    # print("Result: ", result)
    return result["response"]