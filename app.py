
import os
from pymongo import MongoClient
#from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
import json


## Connect to MongoDB Atlas local cluster
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_ATLAS_URI')
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI, appname="devrel.content.python")
db_name = 'docs'
collection_name = 'embeddings'
collection = client[db_name][collection_name]


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Ask a question",
            message="How do I use FancyWidget?"
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a chatbot.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    for chunk in await cl.make_async(runnable.stream)(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
