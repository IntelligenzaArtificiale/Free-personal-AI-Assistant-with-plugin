"""
This file contains the template for the prompt to be used for injecting the context into the model.

With this technique we can use different plugin for different type of question and answer.
Like :
- Internet
- Data
- Code
- PDF
- Audio
- Video

"""

from datetime import datetime
now = datetime.now()

def prompt4conversation(prompt,context):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Alessandro Ciciarelli the owener of intelligenzaartificialeitalia.net 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt} . 
                        WRITE THE ANSWER :"""
    return final_prompt

def prompt4conversationInternet(prompt,context, internet, resume):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Alessandro Ciciarelli the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}.
                        INTERNET RESULT TO USE TO ANSWER : ({internet})
                        INTERNET RESUME : ({resume})
                        NOW THE USER ASK : {prompt}.
                        WRITE THE ANSWER BASED ON INTERNET INFORMATION :"""
    return final_prompt

def prompt4Data(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , YOU MUST MAKE THE CORRECT ANSWER MORE ARGUMENTED ! IF THE CORRECT ANSWER CONTAINS CODE YOU ARE OBLIGED TO INSERT IT IN YOUR NEW ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        MAKE THE ANSWER MORE ARGUMENTED, WITHOUT CHANGING ANYTHING OF THE CORRECT ANSWER :"""
    return final_prompt

def prompt4Code(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli  the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , THE CORRECT ANSWER CONTAINS CODE YOU ARE OBLIGED TO INSERT IT IN YOUR NEW ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CODE FOR THE ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF THE CODE of CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED INCLUDING THE CORRECT CODE :"""
    return final_prompt


def prompt4Context(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli  the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt


def prompt4Audio(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli  the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER based on Audio text gived in input : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt

def prompt4YT(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli  the owener of intelligenzaartificialeitalia.net
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER based on Youtube video gived in input : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt


#HOW TO ADD YOUR OWN PROMPT :
# 1) ADD YOUR FUNCTION HERE, for example : def prompt4Me(prompt, context):
# 2) WRITE THE PROMPT TEMPLATE FOR YOUR FUNCTION, for example : template = f"YOU IS : {context} , NOW THE USER ASK : {prompt} . WRITE THE ANSWER :"
# 3) RETURN THE TEMPLATE, for example : return template
# 4) IMPORT YOUR FUNCTION IN THE MAIN FILE (streamlit_app.py) , for example : from promptTemplate import prompt4Me
# 5) FOLLOW OTHER SPTEP IN THE MAIN FILE (streamlit_app.py)