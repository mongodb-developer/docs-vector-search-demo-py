# MongoDB Atlas vector search chatbot



## Introduction

This is Python flavor to this [workshop](https://mongodb-developer.github.io/).

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

3. Run the gradio application
```
python app.py
```

Visit http://localhost:7860 to see the chatbot.

The results when asking "How do I install FancyWidget?" should result in a very generic result, not related to the docs hosted on `fake_docs` directory.


## Add vector store

First lets create the vector embeddings and insert them into `embeddings` collection:
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

New LLM prompt:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "AI Chatbot"),
    #("user", "Answer user query {currentMessageContent}")
    ("user", """You are a very enthusiastic FancyWidget representative who loves to help people! Given the following sections from the FancyWidget documentation, answer the question using only that information, outputted in markdown format. If you are unsure and the answer is not explicitly written in the documentation, say 'Sorry, I don't know how to help with that'.
    history:
    {history}
     
    Context sections:
    {vectorSearch}
  
    Question: 
    {currentMessageContent}""")
     ])
```

New `get_chat_response`:
```python
def get_chat_response(message, history):

    try:
        docs =  list(vector_store.max_marginal_relevance_search(query=message, k=20, fetch_k=20, lambda_mult=0.1))

        input = ''
        for doc in docs:
            input = input + doc.page_content + '\n\n'

      
        
        print_llm_text = chain.invoke({"vectorSearch": input, "currentMessageContent": message, "history": str(history) })
    
        for i in range(len(print_llm_text)):
            time.sleep(0.05)
            yield  print_llm_text[: i+1]
    except Exception as e:
        error_message = traceback.format_exc()
        print("An error occurred: \n" + error_message)
        yield "Please clone the repo and add your open ai key as well as your MongoDB Atlas URI in the Secret Section of you Space\n OPENAI_API_KEY (your Open AI key) and MONGODB_ATLAS_URI (0.0.0.0/0 whitelisted instance with Vector index created) \n\n For more information : https://mongodb.com/products/platform/atlas-vector-search"
```

Now when we run the application:
```
python app.py
```

We will see specific results for queries like "How do I install FancyWidget?", try to give some followups queries.




