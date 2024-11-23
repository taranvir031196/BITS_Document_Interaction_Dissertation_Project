# BITS_Document_Interaction_Dissertation_Project
## Introduction
Interactive Chatbots are fastly becoming new research areas in current era of
Information Science. The integration of Artificial Intelligence (AI) in document data
interaction marks a paradigm shift in how organizations process, analyze, and derive
insights from vast textual repositories.

The broad range of our project include developing a chatbot that interacts with
documents such as books, legal documents, and other important files. The chatbot will leverage 
LangChain’s loader, OpenAI Embeddings, and GPT to provide responses based on the document content.
Also, it includes current Artificial intelligence, Information retrieval and extraction
techniques.

LangChain’s loader is our first point of discussion, it is an all-purpose tool used to
load various document types, hence aiding in streamlining data preparation. Next,
the analysis explores how OpenAI Embeddings leverage vector representations of
high dimensionality to convert text into numbers so as to be able to carry out
similarity comparisons and observe semantic relationships.

## Setup
To set up a document interaction application locally from GitHub, follow these steps:

### Clone the GitHub Repository

Open your terminal or command prompt and Run the following command to clone the repository:
```
git clone <repository_url>
```

### Navigate to the Project Directory
```
cd <repository_name>
```

### Install Dependencies
```
npm install
```
### Create a new virtual environment
```
python -m venv venv
```
### Installing the project dependencies required to run streamlit project
```
pip install -r requirements.txt
```
###  Run the Streamlit Application
```
streamlit run --server.runOnSave=True main.py
```


