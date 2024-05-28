import time
import traceback
import gradio as gr
import os
import asyncio
from pymongo import MongoClient
#from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()

import json


## Connect to MongoDB Atlas local cluster
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_ATLAS_URI')
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI, appname="devrel.content.python")
db_name = 'docs'
collection_name = 'embeddings'
collection = client[db_name][collection_name]

try:
   
    
    llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)
    prompt = ChatPromptTemplate.from_messages([
    ("system", "AI Chatbot"),
    ("user", "Answer user query {currentMessageContent}")])
    
    chain = prompt | llm | output_parser

except Exception as e:

    vector_store = None
    print("An error occurred: \n" + traceback.format_exc())

def get_chat_response(message, history):

    try:

        print_llm_text = chain.invoke({"vectorSearch": input, "currentMessageContent": message, "history": str(history) })
    
        for i in range(len(print_llm_text)):
            time.sleep(0.05)
            yield  print_llm_text[: i+1]
    except Exception as e:
        error_message = traceback.format_exc()
        print("An error occurred: \n" + error_message)
        yield "Please clone the repo and add your open ai key as well as your MongoDB Atlas URI in the Secret Section of you Space\n OPENAI_API_KEY (your Open AI key) and MONGODB_ATLAS_URI (0.0.0.0/0 whitelisted instance with Vector index created) \n\n For more information : https://mongodb.com/products/platform/atlas-vector-search"
        
    

demo = gr.ChatInterface(get_chat_response, examples=["How to install the FancyWidget?"], title="FancyWidget chatbot",description="This small chat uses a similarity search to find relevant docs, it uses MongoDB Atlas Vector Search read more here: https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-tutorial",submit_btn="Search").queue()

if __name__ == "__main__":
    demo.launch()
