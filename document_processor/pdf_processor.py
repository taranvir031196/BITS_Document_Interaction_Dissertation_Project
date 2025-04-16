__import__('pysqlite3')
import sys
import os
import streamlit as st
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
from langchain.vectorstores import Pinecone
from langchain_core.prompts import MessagesPlaceholder
from typing import List, Dict, Any
import pinecone

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
    store_vector = None
             
    try:
        # Access secrets
        PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"].strip()
        PINECONE_ENVIRONMENT = st.secrets["ENVIRONMENT"]
        index_name = 'streamlit-index'
        
        # Initialize Pinecone
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, if not create it
        index_list = pc.list_indexes().names()
        if index_name not in index_list:
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embeddings dimension
                metric='cosine'
            )
            st.write(f"Created new Pinecone index: {index_name}")
        
        # Get index instance - this is the key part that needs to change
        index = pc.Index(index_name)
        
        # Initialize OpenAI embeddings
        embeddings = OpenAIEmbeddings()
        
        # Create LangChain Pinecone vectorstore - UPDATED THIS PART
        # langchain-pinecone expects a different Index format
        from pinecone import Index as PineconeIndex
        
        # Import needed for handling different Pinecone client versions
        import pkg_resources
        pinecone_version = pkg_resources.get_distribution("pinecone-client").version
        major_version = int(pinecone_version.split('.')[0])

        if major_version >= 2:
            # For Pinecone v2.x client
            # Convert to the legacy format expected by LangChain
            index_for_langchain = {
                "api_key": PINECONE_API_KEY,
                "environment": PINECONE_ENVIRONMENT,
                "index_name": index_name
            }
        else:
            # For Pinecone v1.x client
            index_for_langchain = index
            
        # Create the vector store with the appropriate index format
        store_vector = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            text_key="text"
        )
        
        # Add documents to the vector store
        store_vector.add_documents(chunks)

        # Set up SelfQueryRetriever
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="The path of directories where the document is found",
                type="string",
            ),
        ]

        document_content_description = "Uploaded_Interaction_Document"

        # Create and return retriever
        retriever = SelfQueryRetriever.from_llm(
            self.__model,
            store_vector,
            document_content_description,
            metadata_field_info,
            search_kwargs={"k": k}
        )
        
        return retriever
        
    except Exception as e:
        st.error(f"Pinecone connection error: {str(e)}")
        print(f"Error details: {e}")
        return None
    
    def get_relevant_excerpt(self, retriever, query):
        if retriever is None:
            return "No retriever available. Please check your vector store connection."
        docs = retriever.get_relevant_documents(query)
        return " ".join([doc.page_content for doc in docs])
    
    def set_chat_history(self, max_token_limit: int = 3097):
        return ConversationTokenBufferMemory(llm=self.__model, max_token_limit=max_token_limit, return_messages=True)
    
    #PUBLIC RESPONSE METHOD
    def get_response(self, question: str, retriever: any, chat_history: any) -> str:
        if retriever is None:
            return "I'm sorry, but I couldn't connect to the knowledge base. Please check your Pinecone configuration and try again."

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant responsible for answering questions about documents. Respond to the user's question with a reasonable level of detail based on the following context document(s):\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        output_parser = StrOutputParser()
        chain = prompt | self.__model | output_parser

        try:
            context = retriever.invoke(question)
            answer = chain.invoke({
                "input": question,
                "chat_history": chat_history.load_memory_variables({})['history'],
                "context": context
            })
            
            chat_history.save_context({"input": question}, {"output": answer})
            return answer
        except Exception as e:
            error_msg = f"Error getting response: {str(e)}"
            print(error_msg)
            return f"I encountered an error while processing your question. Please try again or check your configuration. Error: {str(e)}"
