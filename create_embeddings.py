from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import  OpenAIEmbeddings
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os


client = MongoClient(os.getenv('MONGODB_ATLAS_URI'))
db_name = 'docs'
collection_name = 'embeddings'
collection = client[db_name][collection_name]

def read_fake_docs():
    print('Reading fake docs')
    ## Traverse ./fake_docs directory and read all files
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.MARKDOWN, chunk_size=500,chunk_overlap=50)
    fake_docs = []
    for root, dirs, files in os.walk("./fake_docs"):
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                # file to text
                text = f.read()
                md_docs = splitter.create_documents([text])
                fake_docs.extend(md_docs)
                print('Vectorizing ' + file + '...')
                MongoDBAtlasVectorSearch.from_documents(
                    documents=md_docs,
                    embedding=OpenAIEmbeddings(),
                    collection=collection,
                    index_name='vector_index',
                    text_key='text',
                    embedding_key='embedding'
                )

read_fake_docs()
print('Done')
    