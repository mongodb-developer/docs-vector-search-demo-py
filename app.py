import os
from pymongo import MongoClient
#from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_mongodb import MongoDBAtlasVectorSearch
import chainlit as cl
import json


## Connect to MongoDB Atlas local cluster
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_ATLAS_URI')
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI, appname="devrel.content.python")
db_name = 'docs'
collection_name = 'embeddings'
collection = client[db_name][collection_name]

vector_store = MongoDBAtlasVectorSearch(collection=collection,embedding=OpenAIEmbeddings(), index_name='vector_index', text_key='text', embedding_key='embedding')
llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Ask a question",
            message="How do I use FancyWidget?",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(model="gpt-4o",streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a chatbot.",
            ),
            ("human", """You are a very enthusiastic FancyWidget representative who loves to help people! Given the following sections from the FancyWidget documentation, answer the question using only that information, outputted in markdown format. If you are unsure and the answer is not explicitly written in the documentation, say 'Sorry, I don't know how to help with that'.
    
     
            Context sections:
            {context}
        
            Question: 
            {question}""")
     ])
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")
    docs =  list(vector_store.max_marginal_relevance_search(query=message.content, k=20, fetch_k=20, lambda_mult=0.1))

    input = ''
    for doc in docs:
        input = input + doc.page_content + '\n\n'

    for chunk in await cl.make_async(runnable.stream)(
        {"question": message.content, "context": input},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()