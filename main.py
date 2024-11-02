from UI.upload_app import Streamlit_Upload_App

st_uploader_app = Streamlit_Upload_App()

# rag = RAG(
#     doc_path = 'docs/CAN_CIOSC_104_2021.pdf',
#     number_of_retrievals = 1,
#     max_chat_tokens = 3097,
#     creative = 1.5
# )

# print("\nType 'exit' to exit the program.")
# while True:
#     question = str(input("Question: "))
#     print('')
#     if question == "exit":
#         break
#     response = rag.get_response(question)
#     print('Response:', response)
#     print('==================================================')