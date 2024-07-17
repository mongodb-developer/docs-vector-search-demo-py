# MongoDB Atlas vector search chatbot



## Introduction

This is Python flavor to this [workshop](https://mongodb-developer.github.io/vector-search-workshop/).

The `main` brunch holds an intial application phase with just a chatbot to OpenAI LLM.

The `complete` brunch contains the full RAG application code with MongoDB as the Vector Store.


## Database and OpenAI Setup

Please refer to the following sections:
1. [Atlas Setup](https://mongodb-developer.github.io/vector-search-workshop/docs/category/mongodb-atlas)
2. [OpenAI](https://mongodb-developer.github.io/vector-search-workshop/docs/category/openai)



## First application setup

To run the application in a python environment of 3.11+:

1. Setup ENV variables
```
export OPENAI_API_KEY=<API_KEY>
export MONGODB_ATLAS_URI=<your-atlas-srv-uri>
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the chainlit application
```
chainlit run app.py
```

Visit http://localhost:8000 to see the chatbot.

The results when asking "How do I install FancyWidget?" should be in a very generic response form, not related to the docs hosted in directory `fake_docs` directory.


## Add vector store

1. Follow [create vector index](https://mongodb-developer.github.io/vector-search-workshop/docs/vector-search/create-index) section.

2. Now lets create the vector embeddings and insert them into `embeddings` collection from `fake_docs` md files:
```
python create_embeddings.py
```

This should result in:
```
Reading fake docs
Vectorizing LICENSE...
Vectorizing API_Reference.md...
Vectorizing Changelog.md...
Vectorizing Usage.md...
Vectorizing README.md...
Vectorizing Contributing.md...
Vectorizing Installation.md...
Vectorizing Quick_Start.md...
Done
```

Now the collection should be full with FancyWidget.js docs data.

### Now lets update the following functions in `app.py`:

Uncomment the import for 

```python
from langchain_mongodb import MongoDBAtlasVectorSearch
```

Add a vector store configuration using LangChain library before the `llm` intialisation statement:
```python
vector_store = MongoDBAtlasVectorSearch(collection=collection,embedding=OpenAIEmbeddings(), index_name='vector_index', text_key='text', embedding_key='embedding')
llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)
```

New LLM prompt:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "AI Chatbot"),
    #("user", "Answer user query {currentMessageContent}")
    ("user", """You are a very enthusiastic FancyWidget representative who loves to help people! Given the following sections from the FancyWidget documentation, answer the question using only that information, outputted in markdown format. If you are unsure and the answer is not explicitly written in the documentation, say 'Sorry, I don't know how to help with that'.

    Context sections:
    {context}
  
    Question: 
    {question}""")
     ])
```

New `on_message`:
```python
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
```

Now when we run the application:
```
chainlit run app.py
```

We will see specific results for queries like "How do I install FancyWidget?", try to give some followups queries.



