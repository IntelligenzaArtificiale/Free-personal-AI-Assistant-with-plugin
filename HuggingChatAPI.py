
from hugchat import hugchat
from hugchat.login import Login
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from time import sleep


# THIS IS A CUSTOM LLM WRAPPER Based on hugchat library
# Reference :
# - Langchain custom LLM wrapper : https://python.langchain.com/docs/modules/model_io/models/llms/how_to/custom_llm
# - HugChat library : https://github.com/Soulter/hugging-chat-api

class HuggingChat(LLM):
    """HuggingChat LLM wrapper."""
    chatbot : Optional[hugchat.ChatBot] = None
    conversation : Optional[str] = ""
    email : Optional[str]
    psw : Optional[str]

    
    
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            pass

        if self.chatbot is None:
            if self.email is None and self.psw is None:
                ValueError("Email and Password is required, pls check the documentation on github : https://github.com/Soulter/hugging-chat-api")
            else: 
                if self.conversation == "":
                    sign = Login(self.email, self.psw) # type: ignore
                    cookies = sign.login()

                    # Create a ChatBot
                    self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict()) 
                
                    id = self.chatbot.new_conversation()
                    self.chatbot.change_conversation(id)
                    self.conversation = id         
                else:
                    self.chatbot.change_conversation(self.conversation) # type: ignore
            
    
        data = self.chatbot.chat(prompt, temperature=0.4, stream=False) # type: ignore
        return data # type: ignore

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": "HuggingCHAT"}



#llm = HuggingChat(email = "YOUR-EMAIL" , psw = = "YOUR-PSW" ) #for start new chat


#print(llm("Hello, how are you?"))
#print(llm("what is AI?"))
#print(llm("Can you resume your previus answer?")) #now memory work well

