__import__('pysqlite3')
import sys
import os
import streamlit as st
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv(encoding="utf-8")

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.memory import ConversationTokenBufferMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader 
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores.milvus import Milvus
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores import Pinecone as LangchainPinecone  # Note this import
from langchain_core.prompts import MessagesPlaceholder
from langchain.vectorstores.faiss import FAISS
from typing import List, Dict, Any
from milvus import default_server as milvus_server

class RAG:
    def __init__(self, 
                 model_name: str = "gpt-4",
                 creative: float = 1.5) -> None:
            self.__model = self.__set_llm_model(model_name, creative)

    def __set_llm_model(self, model_name = "gpt-4", temperature: float = 0.7):
        openai_api_key = st.secrets["OPENAI_API_KEY"].strip()
        os.environ["OPENAI_API_KEY"] = openai_api_key
        return ChatOpenAI(model_name=model_name, temperature=temperature)
    
    def get_uploaded_doc(self, doc_path: str) -> List[Document]:
        print("Fetching Uploaded Doc")
        global pages
        loader = PyPDFLoader(doc_path)
        pages = loader.load()
        # Improved text splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(pages)
        return chunks
    
    def set_retriever(self, chunks: List[Document], k: int = 1):
        sharing_mode = st.secrets["STREAMLIT_SHARING_MODE"]
        store_vector = None  # or appropriate default value
                 
        try:
            # Initialize Pinecone
            # Access secrets
            PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"].strip()
            PINECONE_ENVIRONMENT = st.secrets["ENVIRONMENT"]
            pc = Pinecone(api_key=PINECONE_API_KEY)
            index_name = 'streamlit-index'
            
            # Check and create index if needed
            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric='cosine'
                )
                st.write(f"Created new Pinecone index: {index_name}")
            # Using Chroma Vector Store
            embeddings = OpenAIEmbeddings()
            # st.write(f"embeddings initialized properly: {embeddings}")
            store_vector = LangchainPinecone.from_existing_index(
                index_name=index_name,
                embedding=embeddings,
                namespace="default"   # Replace with your Pinecone index name
            )
            store_vector.add_documents(chunks)
            # st.write("chunks stored to vector store")

            # Self-Querying Retriever
            metadata_field_info = [
                AttributeInfo(
                    name="source",
                    description="The path of directories where the document is found",
                    type="string",
                ),
            ]
    
            document_content_description = "Uploaded_Interaction_Document"
    
            # return retriever
            _retriever = SelfQueryRetriever.from_llm(
                self.__model,
                store_vector,
                document_content_description,
                metadata_field_info,
                search_kwargs={"k": k}
            )
            # st.write("_retriever set properly")
            return _retriever
        except Exception as e:
            st.error(f"Connection error occurred: {str(e)}")
            # Add logging if needed
            print(f"Error details: {e}")
            store_vector = None  # or appropriate default value
    
    def get_relevant_excerpt(self, retriever, query):
        docs = retriever.get_relevant_documents(query)
        return " ".join([doc.page_content for doc in docs])
    
    def set_chat_history(self, max_token_limit: int = 3097):
        return ConversationTokenBufferMemory(llm=self.__model, max_token_limit=max_token_limit, return_messages=True)
    
    #PUBLIC RESPONSE METHOD
    def get_response(self, question: str, retriever: any, chat_history: any) -> str:

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant responsible for answering questions about documents. Respond to the user's question with a reasonable level of detail based on the following context document(s):\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        output_parser = StrOutputParser()
        chain = prompt | self.__model | output_parser

        answer = chain.invoke({
            "input": question,
            "chat_history": chat_history.load_memory_variables({})['history'],
            "context": retriever.invoke(question)
        })

        chat_history.save_context({"input": question}, {"output": answer})
        return answer

