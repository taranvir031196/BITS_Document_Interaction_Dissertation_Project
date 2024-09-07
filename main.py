from models.basic_model import RAG
from models.recursive_model import RAG_Recursive

rag = RAG(
    doc_path = 'docs/CAN_CIOSC_104_2021.pdf',
    number_of_retrievals = 1,
    max_chat_tokens = 3097,
    creative = 1.5
)
# rag_recursive = RAG_Recursive(model_name="gpt-3.5-turbo")
 
print("\nType 'exit' to exit the program.")
while True:
    question = str(input("Question: "))
    print('')
    if question == "exit":
        break
    response = rag.get_response(question)
    print('Response:', response)

    #Recursive Model
    # rag_recursive.process_pdf(pdf_path = 'docs/CAN_CIOSC_104_2021.pdf')
    # response = rag_recursive.query(question)
    # print('Response:', response['result'])
    print('==================================================')