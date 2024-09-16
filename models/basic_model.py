import os
from dotenv import load_dotenv
load_dotenv(encoding="utf-8")

from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader 
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores.milvus import Milvus
from langchain.vectorstores.chroma import Chroma
from langchain_core.prompts import MessagesPlaceholder
from milvus import default_server as milvus_server

class RAG:
    def __init__(self, 
                 doc_path: str,
                 number_of_retrievals: int = 1,
                 max_chat_tokens: int = 3097,
                 model_name: str = "gpt-4",
                 creative: float = 0.7) -> None:
        self.pages = []
        self.__model = self.__set_llm_model(model_name, creative)
        self.__doc_path = self.__get_uploaded_doc(doc_path)
        self.__retriever = self.__set_retriever(k=number_of_retrievals)
        self.__chat_history = self.__set_chat_history(max_token_limit=max_chat_tokens)

    def __set_llm_model(self, model_name = "gpt-4", temperature: float = 0.7):
        return ChatOpenAI(model_name=model_name, temperature=temperature)
    
    def __get_uploaded_doc(self, doc_path: str) -> list:
        print("Fetching Uploaded Doc")
        # global pages
        loader = PyPDFLoader(doc_path)
        self.pages = loader.load_and_split()
        return self.pages[0].page_content

    def __set_retriever(self, k: int = 1):
        #Using Milvus Vector Data Store
        embeddings = OpenAIEmbeddings()
        store_vector = Chroma.from_documents(self.pages, 
                                             embedding=embeddings,
                                             persist_directory=".",
                                            )
        store_vector.persist()

        # Self-Querying Retriever
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="The path of directories where the document is found",
                type="string",
            ),
        ]

        document_content_description = "Uploaded_Interaction_Document"

        _retriever = SelfQueryRetriever.from_llm(
            self.__model,
            store_vector,
            document_content_description,
            metadata_field_info,
            search_kwargs={"k": k}
        )

        return _retriever
    
    def __set_chat_history(self, max_token_limit: int = 3097):
        return ConversationTokenBufferMemory(llm=self.__model, max_token_limit=max_token_limit, return_messages=True)
    
    #PUBLIC RESPONSE METHOD
    def get_response(self, question: str) -> str:

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant responsible for answering questions about documents. Respond to the user's question with a reasonable level of detail based on the following context document(s):\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        output_parser = StrOutputParser()
        chain = prompt | self.__model | output_parser

        answer = chain.invoke({
            "input": question,
            "chat_history": self.__chat_history.load_memory_variables({})['history'],
            "context": self.__retriever.invoke(question)
        })

        self.__chat_history.save_context({"input": question}, {"output": answer})
        return answer

