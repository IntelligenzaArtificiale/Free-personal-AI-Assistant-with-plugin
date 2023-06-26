
from hugchat import hugchat
from hugchat.login import Login
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from time import sleep



class HuggingChat(LLM):
    
    history_data: Optional[List] = []
    chatbot : Optional[hugchat.ChatBot] = None
    conversation : Optional[str] = ""
    email : Optional[str]
    psw : Optional[str]
    #### WARNING : for each api call this library will create a new chat on chat.openai.com
    
    
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            pass
            #raise ValueError("stop kwargs are not permitted.")
        #token is a must check
        if self.chatbot is None:
            if self.email is None and self.psw is None:
                ValueError("Email and Password is required, pls check the documentation on github")
            else: 
                if self.conversation == "":
                    sign = Login(self.email, self.psw) # type: ignore
                    cookies = sign.login()

                    # Save cookies to usercookies/<email>.json
                    sign.saveCookies()

                    # Create a ChatBot
                    self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict()) 
                
                    id = self.chatbot.new_conversation()
                    self.chatbot.change_conversation(id)
                    self.conversation = id
                    
                else:
                    raise ValueError("Something went wrong")
            
        
        sleep(2)
        data = self.chatbot.chat(prompt, temperature=0.5, stream=False) # type: ignore
    
        
        #add to history
        self.history_data.append({"prompt":prompt,"response":data})     # type: ignore
        
        return data # type: ignore

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": "HuggingCHAT"}



#llm = HuggingChat(email = "YOUR-COOKIES-PATH" , psw ) #for start new chat


#print(llm("Hello, how are you?"))
#print(llm("what is AI?"))
#print(llm("Can you resume your previus answer?")) #now memory work well

