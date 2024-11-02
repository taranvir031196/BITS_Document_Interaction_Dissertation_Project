from evaluate_answer_GPT.gpt_evaluator import GPT_Evaluator
from document_processor.pdf_processor import RAG
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import time
import os

class Streamlit_Upload_App:

    def __init__(self) -> None:
        # if 'rag' not in st.session_state and 'prompt' not in st.session_state:
        self.rag = None
        self.gpt_Evaluator = None
        self.prompt = None
        self.rag_initialized = False  # New flag to track RAG initialization
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None  # Initialize uploaded_file to None
            st.session_state.prompt = None
        # else:
        #     self.rag = st.session_state.rag
        #     self.prompt = st.session_state.prompt
        if not firebase_admin._apps:
            key_dict = json.loads(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'documate-ai.appspot.com'  # Replace with your storage bucket
        })
        self.set_page_config()
        self._initalize_page_navigation()

    # Function to upload file to Firebase
    def upload_to_firebase(self, uploaded_file):
        global blob
        bucket = storage.bucket()
        if uploaded_file is not None:
            blob = bucket.blob(uploaded_file.name)  # Name the blob with the uploaded file's name
            blob.upload_from_file(uploaded_file, timeout=120)
            self.custom_success_message("File uploaded successfully!", color="#1E1E1E")
            blob.make_public()  # Make the file publicly accessible (optional)
            st.session_state.blob_URL = blob.public_url
            # self._initalize_page_navigation('DocuMate Chatbot')

    def custom_success_message(self, message, color="#000000"):
        st.markdown(f'<p style="background-color:#d1f6cb;color:{color};font-size:16px;border-radius:15px;padding: 1%;font-weight: bold;">{message}</p>', unsafe_allow_html=True)
    
    def _initalize_page_navigation(self, page_navigation=None):
        if page_navigation is None:
            st.sidebar.title("DocuMate Navigation")
        # Define pages
        pages = ["DocuMate AI", "DocuMate Chatbot"]
        # Select a page
        if page_navigation is not None:
            page_selection = page_navigation
        else:
            st.sidebar.markdown('<p id="go-to-text" style="color: white;">Go to</p>', unsafe_allow_html=True)
            page_selection = st.sidebar.selectbox('Navigation', pages, label_visibility="collapsed")
        # Display the selected page
        if page_selection == "DocuMate AI":
            st.session_state.page = 'DocuMate AI'
            print(st.session_state.uploaded_file)
            if st.session_state.uploaded_file is not None:
                st.session_state.uploaded_file = None
            self.__set_home_screen_title_subheader()
            
        elif page_selection == "DocuMate Chatbot":
            st.session_state.page = 'DocuMate Chatbot'
            st.title("DocuMate Upload")
            self.create_fileUploader_Section()

        # Create the Refresh button
        refresh_clicked = st.sidebar.markdown(
            '<button class="custom-button" onclick="window.location.reload();">Refresh</button>',
            unsafe_allow_html=True
        )
            
        # Create the Logout button
        logout_clicked = st.sidebar.markdown(
            '<button class="custom-button-logout">Logout</button>',
            unsafe_allow_html=True
        )
        
            # Custom styled buttons with HTML and CSS
        st.sidebar.markdown(
            """
            <style>
            .custom-button {
                background-color: #004466;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                display: inline-block;
                font-size: 16px;
                margin: 5px 2px;
                cursor: pointer;
                width: 100%;
                border-radius: 5px;
            }
            .custom-button:hover {
                background-color: #006699;
            }
            .custom-button-logout {
                background-color: ##FF0000;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                display: inline-block;
                font-size: 16px;
                margin: 5px 2px;
                cursor: pointer;
                width: 100%;
                border-radius: 5px;
            }
            .custom-button-logout:hover {
                background-color: #006699;
            }
            </style>
            """, unsafe_allow_html=True
        )

    # Custom function to set page config and apply custom CSS
    def set_page_config(self):
        st.set_page_config(
            page_title="DocuMate AI",
            page_icon="📄",
            layout="wide"
        )
    
        # Custom CSS to set background color
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #f0f8ff;
            }
            #welcome-to-documate-ai {
                color: #000000;
                text-align: center;
            }
            #revolutionize-your-document-interaction {
                color: #000000;
            }
            #key-features {
                color: #000000;
            }
            #how-it-works {
                color: #000000;
            }
            #get-started {
                color: #000000;
            }
            .st-emotion-cache-15hul6a {
                background-color: #FFFFFF;
                color: #000000;
            }
            #your-intelligent-document-companion {
                color: #000000;
                text-align: center;
                font-size: larger;
                margin: -11px 0 28px 0px;
            }
            .stButton {
                display: grid;
            }
            .stMarkdown {
                color: #000000;
            }
            .popup {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: white;
                padding: 20px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                width: 50%;
                height: 65%;
                z-index: 100;
                border: 5px dashed black;
                overflow: hidden;
            }
            .popup-header {
                    font-size: 20px;
                    margin-bottom: 20px;
                    color: #333;
                    text-align: center;
                    z-index: 9999;
                    position: relative;
                    top: -10em;
                    font-weight: bold;
            }
            .popup-button {
                display: block;
                margin: 0 auto;
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }
            .popup-button:hover {
                background-color: #45a049;
            }
            .overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 99;
            }
            .stFileUploader {
                        z-index: 100 !important;
                        position: relative;
                        float: inline-start;
                        padding: 4% 10% 5% 10%;
                        width: 86%;
                        border: 4px dashed black;
                        margin: 3% 0 0 9%;            
            }
            small {
                color: #000000;
                font-style: italic;
                font-size: 0.8em;
            }
            #document-preview {
                font-weight: 900;
                color: black;
            }
            #chat-interface {
                font-weight: 900;
                color: black;
            }
            .stExpander {
                background-color: #FFFFFF;
                color: #000000;
            }
            .stFileUploaderFileData {
                color: #000000;
                font-weight: bold;
            }
           [data-testid="stFileUploaderDeleteBtn"] {
                color: red;
                font-weight: bold;
            }
            [data-testid="stMarkdownContainer"] {
                color: black;
                font-weight: bold;
            }
            #documate-upload {
                color: black;
                text-align: -webkit-center;
            }
            #documate-chatbot {
                color: black;
                text-align: -webkit-center;
            }
            .custom-spinner {
                font-size: 18px;
                color: black;
                background-color: #4CAF50;
                padding: 10px;
                border-radius: 8px;
                text-align: center; 
            }
            # go-to-text {
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
    def __set_home_screen_title_subheader(self):
        st.title("Welcome to DocuMate AI")
        # Example usage of typewriter effect
        st.subheader('Your Intelligent Document Companion')
        st.subheader("Revolutionize Your Document Interaction")
        self.typewriter("DocuMate AI is a cutting-edge document interaction chatbot that transforms the way you engage with your files. Whether you're a student, researcher, professional, or just someone looking to streamline your document workflow, DocuMate AI is here to assist.")
        # Key Features of DocuMate AI
        st.subheader("Key Features")
        self.typewriter("1. 📄 **Document Upload**: Upload your PDF files to start chatting with DocuMate AI.")
        self.typewriter("2. 💬 **Chatbot Interface**: Ask questions and receive responses from DocuMate AI.")
        self.typewriter("3. 📝 **Smart Summarization**: Get concise summaries of lengthy documents, saving you valuable time and effort.")
        self.typewriter("4. 📚 **Citation Assistant**: Easily generate citations from your uploaded documents.")
        self.typewriter("5. 🧠 **AI-Powered Answer Evaluation**: Receive detailed assessments of your responses, including accuracy, relevance, and completeness scores, helping you identify areas for improvement.")

        # How It Works
        st.subheader("How It Works")
        self.typewriter("1. **Upload a Document**: Simply drag and drop your document into the upload area or click to select files from your device.")
        self.typewriter("2. **Analyze**: DocuMate AI will process your document, extracting key information and preparing for your questions.")
        self.typewriter("3. **Interact with DocuMate AI**: Ask questions, seek clarifications, or request summaries from DocuMate AI.")
        self.typewriter("4. **Discover Answers**: DocuMate AI will provide you with accurate, relevant responses based on your queries.")
        self.typewriter("5. **Evaluate Answers**: Get evaluations of your answers to improve your understanding and knowledge.")
        # Get Started
        st.subheader("Get Started")
        self.typewriter("1. **Time-Saving**: Reduce hours of reading and analysis to minutes of intelligent interaction.")
        self.typewriter("2. **Accuracy**: Powered by advanced AI, ensuring precise and reliable information extraction.")
        self.typewriter("3. **User-Friendly**: Intuitive interface designed for users of all technical levels.")
        self.typewriter("4. **Secure**: Your documents are processed with the highest level of security and privacy.")
        self.typewriter("5. **Versatile**: Suitable for a wide range of industries and document types.")
        self.typewriter("6. **AI-Powered Answer Evaluation**: Receive detailed assessments of your responses, including accuracy, relevance, and completeness scores. This feature helps you identify areas for improvement and deepens your understanding of the subject matter.")
        # Ending message
        st.markdown(f'<p style="text-align: center;padding: 7%;font-size: x-large;"><em><strong>Ready to experience the future of document interaction? Start your journey with DocuMate AI today!</strong></em></p>', unsafe_allow_html=True)
        # self.typewriter("#**Ready to experience the future of document interaction? Start your journey with DocuMate AI today!**")

    def create_fileUploader_Section(self):
        uploaded_file = st.file_uploader("Choose a file", type=["pdf"])
        print(uploaded_file)
        if st.session_state.uploaded_file is None and uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            self.upload_to_firebase(uploaded_file)
            if blob is not None:
                st.title("DocuMate Chatbot")
                self.process_document(blob.public_url)
        else:
            if 'blob_URL' in st.session_state:
                st.success("File already uploaded.")
                st.title("DocuMate Chatbot")
                st.session_state.chunks=None
                self.createAndOpenChatbot(st.session_state.blob_URL)            
            # Display the uploaded file
        # else:
        # File uploader widget
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # # Initialize session state to control the visibility of the file upload section
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False

    def process_document(self, uploaded_file_URL):
        try:
            if self.rag is None:
                with st.spinner("Processing document... Please wait."):
                    # Your processing logic here
                    self.createAndOpenChatbot(uploaded_file_URL)
            
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
        finally:
            pass

    def display_pdf_preview(self, pdf_file):
        # Path to the PDF (can be a URL or local file path)
        pdf_url = pdf_file
        # Use an iframe to embed the PDF in Streamlit
        pdf_display = f'<iframe src="https://docs.google.com/viewer?url={pdf_url}&embedded=true" width="100%" height="1000" type="application/pdf"></iframe>'
        # Display the PDF in Streamlit
        st.components.v1.html(pdf_display, height=1000)

    def chatbot_response(self, message, retriever, chat_history):
        # Placeholder for actual chatbot logic
        try:
            response = self.rag.get_response(message, retriever, chat_history)  
        except Exception as e:
            print(e)
            response = "I'm sorry, I couldn't process requests currently. Please try again later."
        return f"Chatbot: '{response}'"    

    def createAndOpenChatbot(self, uploaded_file):
        global col1, col2
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Document Preview")
            self.display_pdf_preview(uploaded_file)

        with col2:
            self.rag = RAG()
            if 'uploaded_file' in st.session_state and 'chunks' not in st.session_state:
                st.session_state.chunks = self.rag.get_uploaded_doc(uploaded_file)
                st.session_state.retriever = self.rag.set_retriever(st.session_state.chunks, k=1)
                st.session_state.chat_history = self.rag.set_chat_history(max_token_limit=3097)

                self.rag_initialized = True  # Set the flag to True
                print("RAG instance initialized.")
                st.write("RAG instance initialized.")
            else:
                print("RAG instance already exists.")
                st.write("RAG instance already exists.")
                # print(st.session_state.chunks)
            
            self.initialize_ChatHistoryAndChatInterface()
    
    def initialize_ChatHistoryAndChatInterface(self):
        st.subheader("Chat Interface")
        if 'uploaded_file' in st.session_state and 'chunks' not in st.session_state:
            self.rag.set_retriever(st.session_state.chunks, k=1)
            self.rag.set_chat_history(max_token_limit=3097)

        self.gpt_Evaluator = GPT_Evaluator()
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        if "messages" in st.session_state:
            with st.expander("View Chat History"):
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if message["role"] == "" in st.session_state.messages:
                            with st.expander("View Answer Evaluation"):
                                st.markdown(message["evaluation"])

        # React to user input
        # self.prompt = st.chat_input("What is your question?", key=f"chat_input_{len(st.session_state.messages)}")
        self.prompt = st.chat_input("What is your question?")
        st.session_state.prompt = self.prompt
        if self.prompt:
          
            # Display user message in chat message container
            st.chat_message("user").markdown(self.prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": self.prompt})

            with st.spinner("Processing..."):
                time.sleep(1)
                response = self.chatbot_response(self.prompt, st.session_state.retriever, st.session_state.chat_history)
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Fetch relevant excerpt
                excerpt = self.rag.get_relevant_excerpt(st.session_state.retriever, self.prompt)

                # Evaluate the answer
                evaluation = self.gpt_Evaluator.evaluate_RAG_Response(excerpt, self.prompt, response)

                with st.expander("View Answer Evaluation"):
                    st.markdown(evaluation)

                # Optionally, you can store the evaluation in the session state
                if "evaluations" not in st.session_state:
                    st.session_state.evaluations = []
                st.session_state.evaluations.append({"question": self.prompt, "answer": response, "evaluation": evaluation})
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "", "content": evaluation})

    def typewriter(self, content: str, speed: float = 5):
        """
        Display content with a typewriter effect in Streamlit.
        :param content: The content to be displayed (str, int, float, etc.)
        :param speed: The delay between each character (in seconds)
        """
        # Convert content to string to ensure it's iterable
        tokens = content.split()
        container = st.empty()
        for index in range(len(tokens) + 1):
            curr_full_text = " ".join(tokens[:index])
            container.markdown(curr_full_text)
            time.sleep(1 / speed)
