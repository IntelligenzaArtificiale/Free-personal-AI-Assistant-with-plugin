from hugchat import hugchat

import time 

from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


# THIS IS A CUSTOM LLM WRAPPER Based on hugchat library
# Reference :
# - Langchain custom LLM wrapper : https://python.langchain.com/docs/modules/model_io/models/llms/how_to/custom_llm
# - HugChat library : https://github.com/Soulter/hugging-chat-api
# - I am Alessandro Ciciarelli the owner of IntelligenzaArtificialeItalia.net , my dream is to democratize AI and make it accessible to everyone.

class HuggingChat(LLM):

    """HuggingChat LLM wrapper."""

    chatbot : Optional[hugchat.ChatBot] = None


    email: Optional[str] = None
    psw: Optional[str] = None
    cookie_path : Optional[str] = None

    conversation : Optional[str] = None
    model: Optional[int] = 0 # 0 = OpenAssistant/oasst-sft-6-llama-30b-xor , 1 = meta-llama/Llama-2-70b-chat-hf

    temperature: Optional[float] = 0.9
    top_p: Optional[float] = 0.95
    repetition_penalty: Optional[float] = 1.2
    top_k: Optional[int] = 50
    truncate: Optional[int] = 1024
    watermark: Optional[bool] = False
    max_new_tokens: Optional[int] = 1024
    stop: Optional[list] = ["</s>"]
    return_full_text: Optional[bool] = False
    stream_resp: Optional[bool] = True
    use_cache: Optional[bool] = False
    is_retry: Optional[bool] = False
    retry_count: Optional[int] = 5

    avg_response_time: float = 0.0
    log : Optional[bool] = False
    
    
    @property
    def _llm_type(self) -> str:
        return "🤗CUSTOM LLM WRAPPER Based on hugging-chat-api library"
    

    def create_chatbot(self) -> None:
        if not any([self.email, self.psw, self.cookie_path]):
            raise ValueError("email, psw, or cookie_path is required.")
        
        try:
            if self.email and self.psw:
                # Create a ChatBot using email and psw
                from hugchat.login import Login
                start_time = time.time()
                sign = Login(self.email, self.psw)
                cookies = sign.login()
                end_time = time.time()
                if self.log : print(f"\n[LOG] Login successfull in {round(end_time - start_time)} seconds")
            else:
                # Create a ChatBot using cookie_path
                cookies = self.cookie_path and hugchat.ChatBot(cookie_path=self.cookie_path)
            
            self.chatbot = cookies.get_dict() and hugchat.ChatBot(cookies=cookies.get_dict())
            if self.log : print(f"[LOG] LLM WRAPPER created successfully")
            
        except Exception as e:
            raise ValueError("LogIn failed. Please check your credentials or cookie_path. " + str(e))

        # Setup ChatBot info
        self.chatbot.switch_llm(self.model)
        if self.log : print(f"[LOG] LLM WRAPPER switched to model { 'OpenAssistant/oasst-sft-6-llama-30b-xor' if self.model == 0 else 'meta-llama/Llama-2-70b-chat-hf'}")

        self.conversation = self.conversation or self.chatbot.new_conversation()
        self.chatbot.change_conversation(self.conversation)
        if self.log : print(f"[LOG] LLM WRAPPER changed conversation to {self.conversation}\n")
        


    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop:
            raise ValueError("stop kwargs are not permitted.")
        
        self.create_chatbot() if not self.chatbot else None
        
        try:
            if self.log : print(f"[LOG] LLM WRAPPER called with prompt: {prompt}")
            start_time = time.time()
            resp = self.chatbot.chat(
                prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                repetition_penalty=self.repetition_penalty,
                top_k=self.top_k,
                truncate=self.truncate,
                watermark=self.watermark,
                max_new_tokens=self.max_new_tokens,
                stop=self.stop,
                return_full_text=self.return_full_text,
                stream=self.stream_resp,
                use_cache=self.use_cache,
                is_retry=self.is_retry,
                retry_count=self.retry_count,
            )

            end_time = time.time()
            
            self.avg_response_time = (self.avg_response_time + (end_time - start_time)) / 2 if self.avg_response_time else end_time - start_time
            
            if self.log : print(f"[LOG] LLM WRAPPER response time: {round(end_time - start_time)} seconds")
            if self.log : print(f"[LOG] LLM WRAPPER avg response time: {round(self.avg_response_time)} seconds")
            if self.log : print(f"[LOG] LLM WRAPPER response: {resp}\n\n")

            return str(resp)
            
        except Exception as e:
            raise ValueError("ChatBot failed, please check your parameters. " + str(e))

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        parms = { 
            "model": "HuggingChat",
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "top_k": self.top_k,
            "truncate": self.truncate,
            "watermark": self.watermark,
            "max_new_tokens": self.max_new_tokens,
            "stop": self.stop,
            "return_full_text": self.return_full_text,
            "stream": self.stream_resp,
            "use_cache": self.use_cache,
            "is_retry": self.is_retry,
            "retry_count": self.retry_count,
            "avg_response_time": self.avg_response_time,
        }
        return parms
    
    @property
    def _get_avg_response_time(self) -> float:
        """Get the average response time."""
        return self.avg_response_time



#HOW TO USE IT
# 1) Install the library : pip install -U hugchat langchain
# 2) Get your HuggingFace credentials : https://huggingface.co/
# 3) Import the library and enjoy it : from HCA import HCA 

# EXAMPLE 1 : Using email and psw
# llm = HCA(email="YOUR_EMAIL", psw="YOUR_psw")

# EXAMPLE 2 : Using cookie file
# llm = HCA(cookie_path="YOUR_COOKIE_PATH")

# EXAMPLE 3 : Modify the default parameters
# llm = HCA(email="YOUR_EMAIL", psw="YOUR_psw", log=True , model=1, temperature=0.9, top_p=0.95, repetition_penalty=1.2, top_k=50, truncate=1024, watermark=False, max_new_tokens=1024, stop=["</s>"], return_full_text=False, stream=True, use_cache=False, is_retry=False, retry_count=5)

# EXAMPLE 4 : Using the LLM
# print(llm("Hello, how are you?"))


# EXAMPLE 5 : simple use 
# from HCA import HCA
#llm = HCA(email="YOUR_EMAIL", psw="YOUR_psw" , log=True, model=1)
#txt = input("\n\nYou (write 'exit' for stop): ")
#while txt != "exit":
    #print("Bot : " + llm(txt) + "\n")
    #print("Avg response time : " + str(llm._get_avg_response_time))
    #txt = input("You : ")



#from hugchat import hugchat
#from hugchat.login import Login
#from langchain.llms.base import LLM
#from typing import Optional, List, Mapping, Any
#from time import sleep


# THIS IS A CUSTOM LLM WRAPPER Based on hugchat library
# Reference :
# - Langchain custom LLM wrapper : https://python.langchain.com/docs/modules/model_io/models/llms/how_to/custom_llm
# - HugChat library : https://github.com/Soulter/hugging-chat-api





#llm = HuggingChat(email = "YOUR-EMAIL" , psw = = "YOUR-PSW" ) #for start new chat


#print(llm("Hello, how are you?"))
#print(llm("what is AI?"))
#print(llm("Can you resume your previus answer?")) #now memory work well

