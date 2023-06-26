from datetime import datetime
now = datetime.now()

def prompt4conversation(prompt,context):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Alessandro Ciciarelli) 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt} . 
                        WRITE THE ANSWER :"""
    return final_prompt

def prompt4conversationInternet(prompt,context, internet, resume):
    final_prompt = f""" GENERAL INFORMATION : ( today is {now.strftime("%d/%m/%Y %H:%M:%S")} , You is built by Alessandro Ciciarelli) 
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}.
                        INTERNET RESULT TO USE TO ANSWER : ({internet})
                        INTERNET RESUME : ({resume})
                        NOW THE USER ASK : {prompt}.
                        WRITE THE ANSWER BASED ON INTERNET INFORMATION :"""
    return final_prompt

def prompt4Data(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , YOU MUST MAKE THE CORRECT ANSWER MORE ARGUMENTED ! IF THE CORRECT ANSWER CONTAINS CODE YOU ARE OBLIGED TO INSERT IT IN YOUR NEW ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        MAKE THE ANSWER MORE ARGUMENTED, WITHOUT CHANGING ANYTHING OF THE CORRECT ANSWER :"""
    return final_prompt

def prompt4Code(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE , THE CORRECT ANSWER CONTAINS CODE YOU ARE OBLIGED TO INSERT IT IN YOUR NEW ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CODE FOR THE ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF THE CODE of CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED INCLUDING THE CORRECT CODE :"""
    return final_prompt


def prompt4PDF(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt


def prompt4Audio(prompt, context, solution):
    final_prompt = f"""GENERAL INFORMATION : You is built by Alessandro Ciciarelli
                        ISTRUCTION : IN YOUR ANSWER NEVER INCLUDE THE USER QUESTION or MESSAGE ,WRITE ALWAYS ONLY YOUR ACCURATE ANSWER!
                        PREVIUS MESSAGE : ({context})
                        NOW THE USER ASK : {prompt}
                        THIS IS THE CORRECT ANSWER based on Audio text gived in input : ({solution}) 
                        WITHOUT CHANGING ANYTHING OF CORRECT ANSWER , MAKE THE ANSWER MORE DETALIED:"""
    return final_prompt