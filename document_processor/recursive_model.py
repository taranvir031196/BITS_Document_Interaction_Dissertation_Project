import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
load_dotenv(encoding="utf-8")
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import openai
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from pypdf import PdfReader

class RAG_Recursive:

    def __init__(self, model_name) -> None:
        self.__set_llm_model(model_name)

    def __set_llm_model(self, model_name):
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(model_name="gpt-3.5-turbo-instruct")
        self.vector_Store = None
        return self.llm
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_text(text)
    
    def create_vector_store(self, chunks: List[str]):
        self.vector_Store = FAISS.from_texts(chunks, self.embeddings)
    
    def process_pdf(self, pdf_path: str) :
        text = self.extract_pdf_text(pdf_path)
        chunks = self.chunk_text(text)
        self.create_vector_store(chunks)
    
    def query(self, question: str)-> str:
        if not self.vector_Store:
            raise ValueError("Vector store is not initialized yet. Process the pdf first")
        
        qa_chain = RetrievalQA.from_chain_type(
            llm = self.llm,
            chain_type = "stuff",
            retriever = self.vector_Store.as_retriever()
        )
        return qa_chain.invoke(question)