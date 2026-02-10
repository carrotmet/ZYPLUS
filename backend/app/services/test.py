import lazyllm
chat= lazyllm.OnlineChatModule()

history=[]

while True:
    query= input("u quit")
    if query=="quit":
        break
    res = chat(query,llm_chat_history=history)
    print(f"answer:{res}")
    history.append([query,res])