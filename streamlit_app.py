import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
import pandas as pd
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
import sketch
from langchain.text_splitter import CharacterTextSplitter
from promptTemplate import prompt4conversation, prompt4Data, prompt4Code, prompt4PDF, prompt4Audio
from promptTemplate import prompt4conversationInternet
from exportchat import export_chat
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from HuggingChatAPI import HuggingChat
from langchain.embeddings import HuggingFaceHubEmbeddings
import pdfplumber
import docx2txt
from duckduckgo_search import DDGS
from itertools import islice
import requests
import json
import os


hf = None
repo_id = "sentence-transformers/all-mpnet-base-v2"
if 'hf_token' in st.session_state:
    hf = HuggingFaceHubEmbeddings(
        repo_id=repo_id,
        task="feature-extraction",
        huggingfacehub_api_token=st.session_state['hf_token'],
    ) # type: ignore

st.set_page_config(page_title="HugChat - An LLM-powered Streamlit app")
st.markdown('<style>.css-w770g5{\
            width: 100%;}\
            .css-b3z5c9{    \
            width: 100%;}</style>', unsafe_allow_html=True)






# Sidebar contents
with st.sidebar:
    st.title('🤗💬 PersonalChat App')
    
    if 'hf_email' not in st.session_state or 'hf_pass' not in st.session_state:
        with st.expander("ℹ️ Login in Hugging Face", expanded=True):
            st.write("⚠️ You need to login in Hugging Face to use this app. You can register [here](https://huggingface.co/join).")
            st.header('Hugging Face Login')
            hf_email = st.text_input('Enter E-mail:')
            hf_pass = st.text_input('Enter password:', type='password')
            hf_token = st.text_input('Enter API Token:', type='password')
            if st.button('Login 🚀') and hf_email and hf_pass and hf_token: 
                with st.spinner('🚀 Logging in...'):
                    st.session_state['hf_email'] = hf_email
                    st.session_state['hf_pass'] = hf_pass
                    st.session_state['hf_token'] = hf_token
                    sign = Login(st.session_state['hf_email'], st.session_state['hf_pass'])
                    cookies = sign.login()
                    sign.saveCookies()
                    # Create ChatBot                        
                    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
                    st.session_state['chatbot'] = chatbot
                    id = st.session_state['chatbot'].new_conversation()
                    st.session_state['chatbot'].change_conversation(id)
                    st.session_state['conversation'] = id
                    # Generate empty lists for generated and past.
                    ## generated stores AI generated responses
                    if 'generated' not in st.session_state:
                        st.session_state['generated'] = ["I'm IA ITALIA chat, How may I help you?"]
                    ## past stores User's questions
                    if 'past' not in st.session_state:
                        st.session_state['past'] = ['Hi!']
                    st.session_state['LLM'] =  HuggingChat(email=st.session_state['hf_email'], psw=st.session_state['hf_pass'])
                    st.experimental_rerun()
    else:
        with st.expander("ℹ️ Advanced Settings"):
            #temperature: Optional[float]. Default is 0.5
            #top_p: Optional[float]. Default is 0.95
            #repetition_penalty: Optional[float]. Default is 1.2
            #top_k: Optional[int]. Default is 50
            #max_new_tokens: Optional[int]. Default is 1024

            temperature = st.slider('🌡 Temperature', min_value=0.1, max_value=1.0, value=0.5, step=0.01)
            top_p = st.slider('💡 Top P', min_value=0.1, max_value=1.0, value=0.95, step=0.01)
            repetition_penalty = st.slider('🖌 Repetition Penalty', min_value=1.0, max_value=2.0, value=1.2, step=0.01)
            top_k = st.slider('❄️ Top K', min_value=1, max_value=100, value=50, step=1)
            max_new_tokens = st.slider('📝 Max New Tokens', min_value=1, max_value=1024, value=1024, step=1)
    
        #plugins for conversation
        plugins = ["🛑 No PLUGIN","🌐 Web Search", "📋 Talk with your DATA", "📝 Talk with your DOCUMENTS", "🎧 Talk with your AUDIO", "🎥 Talk with your VIDEO"]
        if 'plugin' not in st.session_state:
            st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=0)
        else:
            if st.session_state['plugin'] == "🛑 No PLUGIN":
                st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=plugins.index(st.session_state['plugin']))




# WEB SEARCH PLUGIN
        if st.session_state['plugin'] == "🌐 Web Search" and 'web_search' not in st.session_state:
            # web search settings
            with st.expander("🌐 Web Search Settings"):
                if 'web_search' not in st.session_state or st.session_state['web_search'] == False:
                    reg = ['us-en', 'uk-en', 'it-it']
                    sf = ['on', 'moderate', 'off']
                    tl = ['d', 'w', 'm', 'y']
                    if 'region' not in st.session_state:
                        st.session_state['region'] = st.selectbox('🗺 Region', reg, index=1)
                    else:
                        st.session_state['region'] = st.selectbox('🗺 Region', reg, index=reg.index(st.session_state['region']))
                    if 'safesearch' not in st.session_state:
                        st.session_state['safesearch'] = st.selectbox('🚨 Safe Search', sf, index=1)
                    else:
                        st.session_state['safesearch'] = st.selectbox('🚨 Safe Search', sf, index=sf.index(st.session_state['safesearch']))
                    if 'timelimit' not in st.session_state:
                        st.session_state['timelimit'] = st.selectbox('📅 Time Limit', tl, index=1)
                    else:
                        st.session_state['timelimit'] = st.selectbox('📅 Time Limit', tl, index=tl.index(st.session_state['timelimit']))
                    if 'max_results' not in st.session_state:
                        st.session_state['max_results'] = st.slider('📊 Max Results', min_value=1, max_value=5, value=2, step=1)
                    else:
                        st.session_state['max_results'] = st.slider('📊 Max Results', min_value=1, max_value=5, value=st.session_state['max_results'], step=1)
                    if st.button('🌐 Save change'):
                        st.session_state['web_search'] = "True"
                        st.experimental_rerun()

        elif st.session_state['plugin'] == "🌐 Web Search" and st.session_state['web_search'] == 'True':
            with st.expander("🌐 Web Search Settings"):
                st.write('🚀 Web Search is enabled')
                st.write('🗺 Region: ', st.session_state['region'])
                st.write('🚨 Safe Search: ', st.session_state['safesearch'])
                st.write('📅 Time Limit: ', st.session_state['timelimit'])
                if st.button('🌐🛑 Disable Web Search'):
                    del st.session_state['web_search']
                    del st.session_state['region']
                    del st.session_state['safesearch']
                    del st.session_state['timelimit']
                    del st.session_state['max_results']
                    del st.session_state['plugin']
                    st.experimental_rerun()


# DATA PLUGIN
        if st.session_state['plugin'] == "📋 Talk with your DATA" and 'df' not in st.session_state:
            with st.expander("📋 Talk with your DATA"):
                upload_csv = st.file_uploader("Upload your CSV", type=['csv'])
                if upload_csv is not None:
                    df = pd.read_csv(upload_csv)
                    st.session_state['df'] = df
                    st.experimental_rerun()
        elif 'df' in st.session_state and st.session_state['plugin'] == "📋 Talk with your DATA":
            if st.button('📋 Remove DATA from context'):
                del st.session_state['df']
                del st.session_state['plugin']
                st.experimental_rerun()



# DOCUMENTS PLUGIN
        if st.session_state['plugin'] == "📝 Talk with your DOCUMENTS" and 'documents' not in st.session_state:
            with st.expander("📝 Talk with your DOCUMENT"):
                upload_pdf = st.file_uploader("Upload your DOCUMENT", type=['txt', 'pdf', 'docx'])
                if upload_pdf is not None:
                    documents = []
                    print(upload_pdf.type)
                    if upload_pdf.type == 'text/plain':
                        documents = [upload_pdf.read().decode()]
                    elif upload_pdf.type == 'application/pdf':
                        with pdfplumber.open(upload_pdf) as pdf:
                            documents = [page.extract_text() for page in pdf.pages]
                    elif upload_pdf.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = docx2txt.process(upload_pdf)
                        documents = [text]
                    st.session_state['documents'] = documents
                    # Split documents into chunks
                    with st.spinner('🔨 Creating vectorstore...'):
                        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                        texts = text_splitter.create_documents(documents)
                        # Select embeddings
                        embeddings = hf
                        # Create a vectorstore from documents
                        db = Chroma.from_documents(texts, embeddings)
                        # Create retriever interface
                        retriever = db.as_retriever()
                        # Create QA chain
                        qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever)
                        st.session_state['pdf'] = qa
                    st.experimental_rerun()
        elif 'pdf' in st.session_state and st.session_state['plugin'] == "📝 Talk with your DOCUMENTS":
            if st.button('📝 Remove PDF from context'):
                del st.session_state['pdf']
                del st.session_state['plugin']
                del st.session_state['documents']
                st.experimental_rerun()

# AUDIO PLUGIN
        if st.session_state['plugin'] == "🎧 Talk with your AUDIO" and 'audio' not in st.session_state:
            with st.expander("🎙 Talk with your AUDIO"):
                f = st.file_uploader("Upload your AUDIO", type=['wav', 'mp3', 'flac'])
                if f is not None:
                    path_in = f.name
                    # Get file size from buffer
                    # Source: https://stackoverflow.com/a/19079887
                    old_file_position = f.tell()
                    f.seek(0, os.SEEK_END)
                    getsize = f.tell()  # os.path.getsize(path_in)
                    f.seek(old_file_position, os.SEEK_SET)
                    getsize = round((getsize / 1000000), 1)
                    # st.caption("The size of this file is: " + str(getsize) + "MB")
                    # getsize

                    if getsize < 30:  # File more than 30MB

                        # To read file as bytes:
                        bytes_data = f.getvalue()

                        api_token = st.session_state['hf_token']

                        headers = {"Authorization": f"Bearer {api_token}"}
                        API_URL = "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"

                        def query(data):
                            response = requests.request(
                                "POST", API_URL, headers=headers, data=data
                            )
                            return json.loads(response.content.decode("utf-8"))

                        with st.spinner('🎙 Transcribing your audio...'):
                                data = query(bytes_data)

                        # data = query(bytes_data)
                        with st.spinner('🎙 Creating Vectorstore...'):
                            values_view = data.values()
                            value_iterator = iter(values_view)
                            text_value = next(value_iterator)
                            text_value = text_value.lower()

                            #split text into chunks
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents([text_value])

                            embeddings = hf
                            # Create a vectorstore from documents
                            db = Chroma.from_documents(texts, embeddings)
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever)
                            st.session_state['audio'] = qa
                            st.session_state['audio_text'] = text_value
                        st.experimental_rerun()
                    else:
                        st.error("The file is too big. Please upload a file smaller than 30MB")
        elif 'audio' in st.session_state and st.session_state['plugin'] == "🎧 Talk with your AUDIO":
            if st.button('🎙 Remove AUDIO from context'):
                del st.session_state['audio']
                del st.session_state['audio_text']
                del st.session_state['plugin']
                st.experimental_rerun()


 
    

    if 'hf_email' in st.session_state:
        if st.button('🗑 Logout'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.experimental_rerun()

    add_vertical_space(7)
    st.write('Made with ❤️ by [Alessandro CIciarelli](https://intelligenzaartificialeitalia.net)')


keys = list(st.session_state.keys())
for key in keys:
    print(st.session_state[key])


# User input
# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-70')
response_container = st.container()


## Function for taking user provided prompt as input
def get_text():
    input_text = st.text_input("🧑‍💻 YOU 👇", "", key="input")
    if 'df' in st.session_state:
        with st.expander("🗂 View your DATA"):
            st.data_editor(st.session_state['df'], use_container_width=True)
    if 'pdf' in st.session_state:
        with st.expander("🗂 View your DOCUMENT"):
            st.write(st.session_state['documents'])
    if 'audio' in st.session_state:
        with st.expander("🗂 View your AUDIO"):
            st.write(st.session_state['audio_text'])
    return input_text


## Applying the user input box
with input_container:
    user_input = get_text()

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    if st.session_state['plugin'] == "📋 Talk with your DATA" and 'df' in st.session_state:
        #get only last message
        context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
        if prompt.find('python') != -1 or prompt.find('Code') != -1 or prompt.find('code') != -1 or prompt.find('Python') != -1:
            with st.spinner('🚀 Using tool for python code...'):
                solution = "\n```python\n" 
                solution += st.session_state['df'].sketch.howto(prompt, call_display=False)
                solution += "\n```\n\n"
                final_prompt = prompt4Code(prompt, context, solution)
        else:  
            with st.spinner('🚀 Using tool to get information...'):
                solution = st.session_state['df'].sketch.ask(prompt, call_display=False)
                final_prompt = prompt4Data(prompt, context, solution)
        print(final_prompt)

    elif st.session_state['plugin'] == "📄 Talk with your DOCUMENT" and 'pdf' in st.session_state:
        #get only last message
        context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
        with st.spinner('🚀 Using tool to get information...'):
            solution = st.session_state['pdf'].run(prompt)
            final_prompt = prompt4PDF(prompt, context, solution)
        print(final_prompt)

    elif st.session_state['plugin'] == "🎧 Talk with your AUDIO" and 'audio' in st.session_state:
        #get only last message
        context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
        with st.spinner('🚀 Using tool to get information...'):
            solution = st.session_state['audio'].run(prompt)
            final_prompt = prompt4Audio(prompt, context, solution)
        print(final_prompt)


    else:
        #get last message if exists
        if len(st.session_state['past']) == 1:
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
        else:
            context = f"User: {st.session_state['past'][-2]}\nBot: {st.session_state['generated'][-2]}\nUser: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
        
        if 'web_search' in st.session_state:
            if st.session_state['web_search'] == "True":
                with st.spinner('🚀 Using internet to get information...'):
                    internet_result = ""
                    internet_answer = ""
                    with DDGS() as ddgs:
                        ddgs_gen = ddgs.text(prompt, region=st.session_state['region'], safesearch=st.session_state['safesearch'], timelimit=st.session_state['timelimit'])
                        for r in islice(ddgs_gen, st.session_state['max_results']):
                            internet_result += str(r) + "\n\n"
                        fast_answer = ddgs.answers(prompt)
                        for r in islice(fast_answer, 2):
                            internet_answer += str(r) + "\n\n"

                    final_prompt = prompt4conversationInternet(prompt, context, internet_result, internet_answer)
            else:
                final_prompt = prompt4conversation(prompt, context)
        else:
            final_prompt = prompt4conversation(prompt, context)

        print(final_prompt)
    
    with st.spinner('🚀 Generating response...'):
        response = st.session_state['chatbot'].chat(final_prompt, temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty, top_k=top_k, max_new_tokens=max_new_tokens)
    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input and 'hf_email' in st.session_state and 'hf_pass' in st.session_state and st.button('Send🤗'):
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
    

    #print message in reverse order frist message always bot
    if 'generated' in st.session_state:
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])-1, -1, -1):
                message(st.session_state["generated"][i], key=str(i+100))
                message(st.session_state['past'][i], is_user=True, key=str(i+100) + '_user')
            st.markdown('<br><hr><br>', unsafe_allow_html=True)
            export_chat()
            
    else:
        st.info("👋 Hey , we are very happy to see you here 🤗")
        st.info("👉 Please Login to continue, click on top left corner to login 🚀")
        st.error("👉 If you are not registered on Hugging Face, please register first and then login 🤗")