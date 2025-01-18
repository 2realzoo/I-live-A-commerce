from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from live_prompt import calling_prompt

def calling_llm(category, channel_num, request):
    llm_model = ''
   
    llm_prompt = calling_prompt(category, channel_num)
   
    memory = ConversationBufferMemory() #초기화되므로 로직 고민 필요
    
    llm_chain = ConversationChain(
        llm=llm_model,
        prompt=llm_prompt,
        memory=memory
    )
    
    response = llm_chain.invoke(request)['response']
    response = response.split('\n')
    
    return response
