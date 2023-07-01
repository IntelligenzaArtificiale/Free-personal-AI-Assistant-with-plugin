import io
import random
import shutil
import string
from zipfile import ZipFile
import streamlit as st
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
from promptTemplate import prompt4conversation, prompt4Data, prompt4Code, prompt4Context, prompt4Audio, prompt4YT
from promptTemplate import prompt4conversationInternet
# FOR DEVELOPMENT NEW PLUGIN 
# from promptTemplate import yourPLUGIN
from exportchat import export_chat
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from HuggingChatAPI import HuggingChat
from langchain.embeddings import HuggingFaceHubEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import pdfplumber
import docx2txt
from duckduckgo_search import DDGS
from itertools import islice
from os import path
from pydub import AudioSegment
import os


hf = None
repo_id = "sentence-transformers/all-mpnet-base-v2"

if 'hf_token' in st.session_state:
    if 'hf' not in st.session_state:
        hf = HuggingFaceHubEmbeddings(
            repo_id=repo_id,
            task="feature-extraction",
            huggingfacehub_api_token=st.session_state['hf_token'],
        ) # type: ignore
        st.session_state['hf'] = hf



st.set_page_config(
    page_title="Talk with evrythings💬", page_icon="🤗", layout="wide", initial_sidebar_state="expanded"
)

st.markdown('<style>.css-w770g5{\
            width: 100%;}\
            .css-b3z5c9{    \
            width: 100%;}\
            .stButton>button{\
            width: 100%;}\
            .stDownloadButton>button{\
            width: 100%;}\
            </style>', unsafe_allow_html=True)






# Sidebar contents for logIN, choose plugin, and export chat
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

                    try:
                    
                        sign = Login(st.session_state['hf_email'], st.session_state['hf_pass'])
                        cookies = sign.login()
                        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
                    except Exception as e:
                        st.error(e)
                        st.info("⚠️ Please check your credentials and try again.")
                        st.error("⚠️ dont abuse the API")
                        st.warning("⚠️ If you don't have an account, you can register [here](https://huggingface.co/join).")
                        from time import sleep
                        sleep(3)
                        del st.session_state['hf_email']
                        del st.session_state['hf_pass']
                        del st.session_state['hf_token']
                        st.experimental_rerun()

                    st.session_state['chatbot'] = chatbot

                    id = st.session_state['chatbot'].new_conversation()
                    st.session_state['chatbot'].change_conversation(id)

                    st.session_state['conversation'] = id
                    # Generate empty lists for generated and past.
                    ## generated stores AI generated responses
                    if 'generated' not in st.session_state:
                        st.session_state['generated'] = ["I'm **IA ITALIA chat**, How may I help you ? "]
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
    

        # FOR DEVELOPMENT NEW PLUGIN YOU MUST ADD IT HERE INTO THE LIST 
        # YOU NEED ADD THE NAME AT 144 LINE

        #plugins for conversation
        plugins = ["🛑 No PLUGIN","🌐 Web Search", "🔗 Talk with Website" , "📋 Talk with your DATA", "📝 Talk with your DOCUMENTS", "🎧 Talk with your AUDIO", "🎥 Talk with YT video", "🧠 GOD MODE" ,"💾 Upload saved VectorStore"]
        if 'plugin' not in st.session_state:
            st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=0)
        else:
            if st.session_state['plugin'] == "🛑 No PLUGIN":
                st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=plugins.index(st.session_state['plugin']))


# FOR DEVELOPMENT NEW PLUGIN FOLLOW THIS TEMPLATE
# PLUGIN TEMPLATE
# if st.session_state['plugin'] == "🔌 PLUGIN NAME" and 'PLUGIN NAME' not in st.session_state:
#     # PLUGIN SETTINGS
#     with st.expander("🔌 PLUGIN NAME Settings", expanded=True):
#         if 'PLUGIN NAME' not in st.session_state or st.session_state['PLUGIN NAME'] == False:
#             # PLUGIN CODE
#             st.session_state['PLUGIN NAME'] = True
#         elif st.session_state['PLUGIN NAME'] == True:
#             # PLUGIN CODE
#             if st.button('🔌 Disable PLUGIN NAME'):
#               st.session_state['plugin'] = "🛑 No PLUGIN"
#               st.session_state['PLUGIN NAME'] = False
#               del ALL SESSION STATE VARIABLES RELATED TO PLUGIN
#               st.experimental_rerun()
#       # PLUGIN UPLOADER
#       if st.session_state['PLUGIN NAME'] == True:
#           with st.expander("🔌 PLUGIN NAME Uploader", expanded=True):
#               # PLUGIN UPLOADER CODE
#               load file
#               if load file and st.button('🔌 Upload PLUGIN NAME'):
#                   qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
#                   st.session_state['PLUGIN DB'] = qa
#                   st.experimental_rerun()
# 



# WEB SEARCH PLUGIN
        if st.session_state['plugin'] == "🌐 Web Search" and 'web_search' not in st.session_state:
            # web search settings
            with st.expander("🌐 Web Search Settings", expanded=True):
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
            with st.expander("🌐 Web Search Settings", expanded=True):
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

# GOD MODE PLUGIN
        if st.session_state['plugin'] == "🧠 GOD MODE" and 'god_mode' not in st.session_state:
            with st.expander("🧠 GOD MODE Settings", expanded=True):
                if 'god_mode' not in st.session_state or st.session_state['god_mode'] == False:
                    topic = st.text_input('🔎 Topic', "Artificial Intelligence in Finance")
                    web_result = st.checkbox('🌐 Web Search', value=True, disabled=True)
                    yt_result = st.checkbox('🎥 YT Search', value=True, disabled=True)
                    website_result = st.checkbox('🔗 Website Search', value=True, disabled=True)
                    deep_of_search = st.slider('📊 Deep of Search', min_value=1, max_value=5, value=2, step=1) 
                    if st.button('🧠✅ Give knowledge to the model'):
                        full_text = []
                        links = []
                        news = []
                        yt_ids = []
                        source = []
                        if web_result == True:
                            internet_result = ""
                            internet_answer = ""
                            with DDGS() as ddgs:
                                with st.spinner('🌐 Searching on the web...'):
                                    ddgs_gen = ddgs.text(topic, region="us-en")
                                    for r in islice(ddgs_gen, deep_of_search):
                                        l = r['href']
                                        source.append(l)
                                        links.append(l)
                                        internet_result += str(r) + "\n\n"
                                        
                                    fast_answer = ddgs.news(topic)
                                    for r in islice(fast_answer, deep_of_search):
                                        internet_answer += str(r) + "\n\n" 
                                        l = r['url']
                                        source.append(l)
                                        news.append(r)

                                
                            full_text.append(internet_result)
                            full_text.append(internet_answer)

                        if yt_result == True:
                            with st.spinner('🎥 Searching on YT...'):
                                from youtubesearchpython import VideosSearch
                                videosSearch = VideosSearch(topic, limit = deep_of_search)
                                yt_result = videosSearch.result()
                                for i in yt_result['result']: # type: ignore
                                    duration = i['duration'] # type: ignore
                                    duration = duration.split(':')
                                    if len(duration) == 3:
                                        #skip videos longer than 1 hour
                                        if int(duration[0]) > 1:
                                            continue
                                    if len(duration) == 2:
                                        #skip videos longer than 30 minutes
                                        if int(duration[0]) > 30:
                                            continue
                                    yt_ids.append(i['id']) # type: ignore
                                    source.append("https://www.youtube.com/watch?v="+i['id']) # type: ignore
                                    full_text.append(i['title']) # type: ignore


                        if website_result == True:
                            for l in links:
                                try:
                                    with st.spinner(f'👨‍💻 Scraping website : {l}'):
                                        r = requests.get(l)
                                        soup = BeautifulSoup(r.content, 'html.parser')
                                        full_text.append(soup.get_text()+"\n\n")
                                except:
                                    pass

                        for id in yt_ids:
                            try:
                                yt_video_txt= []
                                with st.spinner(f'👨‍💻 Scraping YT video : {id}'):
                                    transcript_list = YouTubeTranscriptApi.list_transcripts(id)
                                    transcript_en = None
                                    last_language = ""
                                    for transcript in transcript_list:
                                        if transcript.language_code == 'en':
                                            transcript_en = transcript
                                            break
                                        else:
                                            last_language = transcript.language_code
                                    if transcript_en is None:   
                                        transcript_en = transcript_list.find_transcript([last_language])
                                        transcript_en = transcript_en.translate('en')

                                    text = transcript_en.fetch()
                                    yt_video_txt.append(text)

                                    for i in range(len(yt_video_txt)):
                                        for j in range(len(yt_video_txt[i])):
                                            full_text.append(yt_video_txt[i][j]['text'])


                            except:
                                pass

                        with st.spinner('🧠 Building vectorstore with knowledge...'):
                            full_text = "\n".join(full_text)
                            st.session_state['god_text'] = [full_text]
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents([full_text])
                            # Select embeddings
                            embeddings = st.session_state['hf']
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)

                        with st.spinner('🔨 Saving vectorstore...'):
                            # save vectorstore
                            db.persist()
                            #create .zip file of directory to download
                            shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 
                        
                        with st.spinner('🔨 Creating QA chain...'):
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                            st.session_state['god_mode'] = qa
                            st.session_state['god_mode_source'] = source
                            st.session_state['god_mode_info'] = "🧠 GOD MODE have builded a vectorstore about **" + topic + f"**. The knowledge is based on\n- {len(news)} news🗞\n- {len(yt_ids)} YT videos📺\n- {len(links)} websites🌐 \n"
                        
                        st.experimental_rerun()
                                

        if st.session_state['plugin'] == "🧠 GOD MODE" and 'god_mode' in st.session_state:
            with st.expander("**✅ GOD MODE is enabled 🚀**", expanded=True):
                st.markdown(st.session_state['god_mode_info'])
                if 'db' in st.session_state:
                    # leave ./ from name for download
                    file_name = st.session_state['db'][2:]
                    st.download_button(
                        label="📩 Download vectorstore",
                        data=open(file_name, 'rb').read(),
                        file_name=file_name,
                        mime='application/zip'
                    )
                if st.button('🧠🛑 Disable GOD MODE'):
                    del st.session_state['god_mode']
                    del st.session_state['db']
                    del st.session_state['god_text']
                    del st.session_state['god_mode_info']
                    del st.session_state['god_mode_source']
                    del st.session_state['plugin']
                    st.experimental_rerun()
            

# DATA PLUGIN
        if st.session_state['plugin'] == "📋 Talk with your DATA" and 'df' not in st.session_state:
            with st.expander("📋 Talk with your DATA", expanded= True):
                upload_csv = st.file_uploader("Upload your CSV", type=['csv'])
                if upload_csv is not None:
                    df = pd.read_csv(upload_csv)
                    st.session_state['df'] = df
                    st.experimental_rerun()
        if st.session_state['plugin'] == "📋 Talk with your DATA":
            if st.button('🛑📋 Remove DATA from context'):
                if 'df' in st.session_state:
                    del st.session_state['df']
                del st.session_state['plugin']
                st.experimental_rerun()



# DOCUMENTS PLUGIN
        if st.session_state['plugin'] == "📝 Talk with your DOCUMENTS" and 'documents' not in st.session_state:
            with st.expander("📝 Talk with your DOCUMENT", expanded=True):  
                upload_pdf = st.file_uploader("Upload your DOCUMENT", type=['txt', 'pdf', 'docx'], accept_multiple_files=True)
                if upload_pdf is not None and st.button('📝✅ Load Documents'):
                    documents = []
                    with st.spinner('🔨 Reading documents...'):
                        for upload_pdf in upload_pdf:
                            print(upload_pdf.type)
                            if upload_pdf.type == 'text/plain':
                                documents += [upload_pdf.read().decode()]
                            elif upload_pdf.type == 'application/pdf':
                                with pdfplumber.open(upload_pdf) as pdf:
                                    documents += [page.extract_text() for page in pdf.pages]
                            elif upload_pdf.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                text = docx2txt.process(upload_pdf)
                                documents += [text]
                    st.session_state['documents'] = documents
                    # Split documents into chunks
                    with st.spinner('🔨 Creating vectorstore...'):
                        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                        texts = text_splitter.create_documents(documents)
                        # Select embeddings
                        embeddings = st.session_state['hf']
                        # Create a vectorstore from documents
                        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                        db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)

                    with st.spinner('🔨 Saving vectorstore...'):
                        # save vectorstore
                        db.persist()
                        #create .zip file of directory to download
                        shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                        # save in session state and download
                        st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 
                    
                    with st.spinner('🔨 Creating QA chain...'):
                        # Create retriever interface
                        retriever = db.as_retriever()
                        # Create QA chain
                        qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever,  return_source_documents=True)
                        st.session_state['pdf'] = qa

                    st.experimental_rerun()

        if st.session_state['plugin'] == "📝 Talk with your DOCUMENTS":
            if 'db' in st.session_state:
                # leave ./ from name for download
                file_name = st.session_state['db'][2:]
                st.download_button(
                    label="📩 Download vectorstore",
                    data=open(file_name, 'rb').read(),
                    file_name=file_name,
                    mime='application/zip'
                )
            if st.button('🛑📝 Remove PDF from context'):
                if 'pdf' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['pdf']
                    del st.session_state['documents']
                del st.session_state['plugin']
                    
                st.experimental_rerun()

# AUDIO PLUGIN
        if st.session_state['plugin'] == "🎧 Talk with your AUDIO" and 'audio' not in st.session_state:
            with st.expander("🎙 Talk with your AUDIO", expanded=True):
                f = st.file_uploader("Upload your AUDIO", type=['wav', 'mp3'])
                if f is not None:
                    if f.type == 'audio/mpeg':
                        #convert mp3 to wav
                        with st.spinner('🔨 Converting mp3 to wav...'):
                            #save mp3
                            with open('audio.mp3', 'wb') as out:
                                out.write(f.read())
                            #convert to wav
                            sound = AudioSegment.from_mp3("audio.mp3")
                            sound.export("audio.wav", format="wav")
                            file_name = 'audio.wav'
                    else:
                        with open(f.name, 'wb') as out:
                            out.write(f.read())
      
                        bytes_data = f.read()
                        file_name = f.name
                    
                    r = sr.Recognizer()
                    #Given audio file must be a filename string or a file-like object


                    with st.spinner('🔨 Reading audio...'):
                        with sr.AudioFile(file_name) as source:
                            # listen for the data (load audio to memory)
                            audio_data = r.record(source)
                            # recognize (convert from speech to text)
                            text = r.recognize_google(audio_data)
                    data = [text]
                    # data = query(bytes_data)
                    with st.spinner('🎙 Creating Vectorstore...'):

                        #split text into chunks
                        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                        texts = text_splitter.create_documents(text)

                        embeddings = st.session_state['hf']
                        # Create a vectorstore from documents
                        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                        db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)
                        # save vectorstore
                    
                    with st.spinner('🎙 Saving Vectorstore...'):
                        db.persist()
                        #create .zip file of directory to download
                        shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                        # save in session state and download
                        st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 

                    with st.spinner('🎙 Creating QA chain...'):
                        # Create retriever interface
                        retriever = db.as_retriever()
                        # Create QA chain
                        qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                        st.session_state['audio'] = qa
                        st.session_state['audio_text'] = text
                    st.experimental_rerun()
                    
        if st.session_state['plugin'] == "🎧 Talk with your AUDIO":
            if 'db' in st.session_state:
                    # leave ./ from name for download
                    file_name = st.session_state['db'][2:]
                    st.download_button(
                        label="📩 Download vectorstore",
                        data=open(file_name, 'rb').read(),
                        file_name=file_name,
                        mime='application/zip'
                    )
            if st.button('🛑🎙 Remove AUDIO from context'):
                if 'audio' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['audio']
                    del st.session_state['audio_text']
                del st.session_state['plugin']
                st.experimental_rerun()


# YT PLUGIN
        if st.session_state['plugin'] == "🎥 Talk with YT video" and 'yt' not in st.session_state:
            with st.expander("🎥 Talk with YT video", expanded=True):
                yt_url = st.text_input("1.📺 Enter a YouTube URL")
                yt_url2 = st.text_input("2.📺 Enter a YouTube URL")
                yt_url3 = st.text_input("3.📺 Enter a YouTube URL")
                if yt_url is not None and st.button('🎥✅ Add YouTube video to context'):
                    if yt_url != "":
                        video = 1
                        yt_url = yt_url.split("=")[1]
                        if yt_url2 != "":
                            yt_url2 = yt_url2.split("=")[1]
                            video = 2
                        if yt_url3 != "":
                            yt_url3 = yt_url3.split("=")[1]
                            video = 3

                        text_yt = []
                        text_list = []
                        for i in range(video):
                            with st.spinner(f'🎥 Extracting TEXT from YouTube video {str(i)} ...'):
                                #get en subtitles
                                transcript_list = YouTubeTranscriptApi.list_transcripts(yt_url)
                                transcript_en = None
                                last_language = ""
                                for transcript in transcript_list:
                                    if transcript.language_code == 'en':
                                        transcript_en = transcript
                                        break
                                    else:
                                        last_language = transcript.language_code
                                if transcript_en is None:   
                                    transcript_en = transcript_list.find_transcript([last_language])
                                    transcript_en = transcript_en.translate('en')

                                text = transcript_en.fetch()
                                text_yt.append(text)

                        for i in range(len(text_yt)):
                            for j in range(len(text_yt[i])):
                                text_list.append(text_yt[i][j]['text'])
                        
                        # creating a vectorstore

                        with st.spinner('🎥 Creating Vectorstore...'):
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents(text_list)
                            # Select embeddings
                            embeddings = st.session_state['hf']
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)

                        with st.spinner('🎥 Saving Vectorstore...'):
                            # save vectorstore
                            db.persist()
                            #create .zip file of directory to download
                            shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 

                        with st.spinner('🎥 Creating QA chain...'):
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                            st.session_state['yt'] = qa
                            st.session_state['yt_text'] = text_list
                        st.experimental_rerun()

        if st.session_state['plugin'] == "🎥 Talk with YT video":
            if 'db' in st.session_state:
                # leave ./ from name for download
                file_name = st.session_state['db'][2:]
                st.download_button(
                    label="📩 Download vectorstore",
                    data=open(file_name, 'rb').read(),
                    file_name=file_name,
                    mime='application/zip'
                )

            if st.button('🛑🎥 Remove YT video from context'):
                if 'yt' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['yt']
                    del st.session_state['yt_text']
                del st.session_state['plugin']
                st.experimental_rerun()

# WEBSITE PLUGIN
        if st.session_state['plugin'] == "🔗 Talk with Website" and 'web_sites' not in st.session_state:
            with st.expander("🔗 Talk with Website", expanded=True):
                web_url = st.text_area("🔗 Enter a website URLs , one for each line")
                if web_url is not None and st.button('🔗✅ Add website to context'):
                    if web_url != "":
                        text = []
                        #max 10 websites
                        with st.spinner('🔗 Extracting TEXT from Websites ...'):
                            for url in web_url.split("\n")[:10]:
                                page = requests.get(url)
                                soup = BeautifulSoup(page.content, 'html.parser')
                                text.append(soup.get_text())
                            # creating a vectorstore

                        with st.spinner('🔗 Creating Vectorstore...'):
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents(text)
                            # Select embeddings
                            embeddings = st.session_state['hf']
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)
                        
                        with st.spinner('🔗 Saving Vectorstore...'):
                            # save vectorstore
                            db.persist()
                            #create .zip file of directory to download
                            shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 
                        
                        with st.spinner('🔗 Creating QA chain...'):
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                            st.session_state['web_sites'] = qa
                            st.session_state['web_text'] = text
                        st.experimental_rerun()
        
        if st.session_state['plugin'] == "🔗 Talk with Website":
            if 'db' in st.session_state:
                # leave ./ from name for download
                file_name = st.session_state['db'][2:]
                st.download_button(
                    label="📩 Download vectorstore",
                    data=open(file_name, 'rb').read(),
                    file_name=file_name,
                    mime='application/zip'
                )

            if st.button('🛑🔗 Remove Website from context'):
                if 'web_sites' in st.session_state:
                    del st.session_state['db']
                    del st.session_state['web_sites']
                    del st.session_state['web_text']
                del st.session_state['plugin']
                st.experimental_rerun()

                            
# UPLOAD PREVIUS VECTORSTORE
        if st.session_state['plugin'] == "💾 Upload saved VectorStore" and 'old_db' not in st.session_state:
            with st.expander("💾 Upload saved VectorStore", expanded=True):
                db_file = st.file_uploader("Upload a saved VectorStore", type=["zip"])
                if db_file is not None and st.button('✅💾 Add saved VectorStore to context'):
                    if db_file != "":
                        with st.spinner('💾 Extracting VectorStore...'):
                            # unzip file in a new directory
                            with ZipFile(db_file, 'r') as zipObj:
                                # Extract all the contents of zip file in different directory
                                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                                zipObj.extractall("chroma_db_" + random_str)
                            # save in session state the path of the directory
                            st.session_state['old_db'] = "chroma_db_" + random_str
                            hf = st.session_state['hf']
                            # Create retriever interface
                            db = Chroma("chroma_db_" + random_str, embedding_function=hf)

                        with st.spinner('💾 Creating QA chain...'):
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever, return_source_documents=True)
                            st.session_state['old_db'] = qa
                            st.experimental_rerun()

        if st.session_state['plugin'] == "💾 Upload saved VectorStore":
            if st.button('🛑💾 Remove VectorStore from context'):
                if 'old_db' in st.session_state:
                    del st.session_state['old_db']
                del st.session_state['plugin']
                st.experimental_rerun()


# END OF PLUGIN
    add_vertical_space(4)
    if 'hf_email' in st.session_state:
        if st.button('🗑 Logout'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.experimental_rerun()

    export_chat()
    add_vertical_space(5)
    html_chat = '<center><h6>🤗 Support the project with a donation for the development of new features 🤗</h6>'
    html_chat += '<br><a href="https://rebrand.ly/SupportAUTOGPTfree"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal donate button" /></a><center><br>'
    st.markdown(html_chat, unsafe_allow_html=True)
    st.write('Made with ❤️ by [Alessandro CIciarelli](https://intelligenzaartificialeitalia.net)')

##### End of sidebar


# User input
# Layout of input/response containers
input_container = st.container()
response_container = st.container()
data_view_container = st.container()
loading_container = st.container()



## Applying the user input box
with input_container:
        input_text = st.chat_input("🧑‍💻 Write here 👇", key="input")

with data_view_container:
    if 'df' in st.session_state:
        with st.expander("🤖 View your **DATA**"):
            st.data_editor(st.session_state['df'], use_container_width=True)
    if 'pdf' in st.session_state:
        with st.expander("🤖 View your **DOCUMENTs**"):
            st.write(st.session_state['documents'])
    if 'audio' in st.session_state:
        with st.expander("🤖 View your **AUDIO**"):
            st.write(st.session_state['audio_text'])
    if 'yt' in st.session_state:
        with st.expander("🤖 View your **YT video**"):
            st.write(st.session_state['yt_text'])
    if 'web_text' in st.session_state:
        with st.expander("🤖 View the **Website content**"):
            st.write(st.session_state['web_text'])
    if 'old_db' in st.session_state:
        with st.expander("🗂 View your **saved VectorStore**"):
            st.success("📚 VectorStore loaded")
    if 'god_mode_source' in st.session_state:
        with st.expander("🌍 View source"):
            for s in st.session_state['god_mode_source']:
                st.markdown("- " + s)

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    make_better = True
    source = ""

    with loading_container:

        # FOR DEVELOPMENT PLUGIN
        # if st.session_state['plugin'] == "🔌 PLUGIN NAME" and 'PLUGIN DB' in st.session_state:
        #     with st.spinner('🚀 Using PLUGIN NAME...'):
        #         solution = st.session_state['PLUGIN DB']({"query": prompt})
        #         final_prompt = YourCustomPrompt(prompt, context)
        

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


        elif st.session_state['plugin'] == "📝 Talk with your DOCUMENTS" and 'pdf' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['pdf']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"


        elif st.session_state['plugin'] == "🧠 GOD MODE" and 'god_mode' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['god_mode']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"


        elif st.session_state['plugin'] == "🔗 Talk with Website" and 'web_sites' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['web_sites']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"
                    


        elif st.session_state['plugin'] == "💾 Upload saved VectorStore" and 'old_db' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['old_db']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"


        elif st.session_state['plugin'] == "🎧 Talk with your AUDIO" and 'audio' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['audio']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Audio(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"


        elif st.session_state['plugin'] == "🎥 Talk with YT video" and 'yt' in st.session_state:
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['yt']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4YT(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"
    

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

        if make_better:
            with st.spinner('🚀 Generating response...'):
                print(final_prompt)
                response = st.session_state['chatbot'].chat(final_prompt, temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty, top_k=top_k, max_new_tokens=max_new_tokens)
                response += source
        else:
            print(final_prompt)
            response = final_prompt

    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if input_text and 'hf_email' in st.session_state and 'hf_pass' in st.session_state:
        response = generate_response(input_text)
        st.session_state.past.append(input_text)
        st.session_state.generated.append(response)
    

    #print message in normal order, frist user then bot
    if 'generated' in st.session_state:
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                with st.chat_message(name="user"):
                    st.markdown(st.session_state['past'][i])
                
                with st.chat_message(name="assistant"):
                    if len(st.session_state['generated'][i].split("✅Source:")) > 1:
                        source = st.session_state['generated'][i].split("✅Source:")[1]
                        mess = st.session_state['generated'][i].split("✅Source:")[0]

                        st.markdown(mess)
                        with st.expander("📚 Source of message number " + str(i+1)):
                            st.markdown(source)

                    else:
                        st.markdown(st.session_state['generated'][i])

            st.markdown('', unsafe_allow_html=True)
            
            
    else:
        st.info("👋 Hey , we are very happy to see you here 🤗")
        st.info("👉 Please Login to continue, click on top left corner to login 🚀")
        st.error("👉 If you are not registered on Hugging Face, please register first and then login 🤗")