from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class GPT_Evaluator:

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0)
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are an AI assistant tasked with evaluating the accuracy and relevance of an answer to a given question based on a provided excerpt from a document.

            Question: {question}
            Answer: {answer}
            Relevant Excerpt: {document_excerpt}

            Please evaluate the answer based on the following criteria:
            1. Accuracy: Is the answer factually correct according to the excerpt?
            2. Relevance: Does the answer directly address the question asked?
            3. Completeness: Does the answer provide all necessary information from the excerpt?
            4. Clarity: Is the answer clear and easy to understand?

            Provide a score out of 10 for each criterion and an overall score out of 10.
            Also, provide a brief explanation for each score and any suggestions for improvement.

            Format your response as follows:
            **Accuracy**: **[[Score]/10**
            [Explanation]

            **Relevance**: **[Score]/10**
            [Explanation]

            **Completeness**: **[Score]/10**
            [Explanation]

            **Clarity**: **[Score]/10**
            [Explanation]

            **Overall Score**: **[Score]/10**
            [Summary and suggestions for improvement]
            """
        )

    def evaluate_RAG_Response(self, document_excerpt, question, answer):
        evaluation = self.llm(self.prompt.format(
            question=question,
            answer=answer,
            document_excerpt=document_excerpt
        ))
        print(document_excerpt)
        return evaluation.content
