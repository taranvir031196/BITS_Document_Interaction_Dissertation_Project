from models.basic_model import RAG
import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import time
import os

class Streamlit_Upload_App:

    def __init__(self) -> None:
        if not firebase_admin._apps:
            cred = credentials.Certificate("documate-ai-88b721abe941.json")
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
            blob.upload_from_file(uploaded_file)
            st.success("File uploaded successfully!")
            blob.make_public()  # Make the file publicly accessible (optional)
            # self._initalize_page_navigation('DocuMate Chatbot')

    def _initalize_page_navigation(self, page_navigation=None):
        if page_navigation is None:
            st.sidebar.title("DocuMate Navigation")
        # Define pages
        pages = ["DocuMate AI", "DocuMate Upload", "DocuMate Chatbot"]
        # Select a page
        if page_navigation is not None:
            page_selection = page_navigation
        else:
            page_selection = st.sidebar.selectbox("Go to", pages)
        # Display the selected page
        if page_selection == "DocuMate AI":
            st.session_state.page = 'DocuMate AI'
            self.__set_home_screen_title_subheader()
            
        elif page_selection == "DocuMate Upload":
            st.session_state.page = 'DocuMate Upload'
            st.title("DocuMate Upload")
            self.create_fileUploader_Section()
            
        elif page_selection == "DocuMate Chatbot":
            st.session_state.page = 'DocuMate Chatbot'
            st.title("DocuMate Chatbot")
            self.createAndOpenChatbot(blob.public_url)
    
    # def navigate_screens_basedOn_sessionState(self):

    #     if st.session_state.page == "DocuMate Chatbot":
    #         self.createAndOpenChatbot(blob.public_url)
            
    #     elif st.session_state.page == "page2":
    #         pass

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
                        padding: 10% 10% 10% 10%;
                        width: 86%;
                        border: 4px dashed black;
                        margin: 3% 0 0 9%;            
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
        self.typewriter("1. **Document Upload**: Upload your PDF files to start chatting with DocuMate AI.")
        self.typewriter("2. **Chatbot Interface**: Ask questions and receive responses from DocuMate AI.")
        self.typewriter("3. **Smart Summarization**: Get concise summaries of lengthy documents, saving you valuable time and effort.")
        self.typewriter("4. **Citation Assistant**: Easily generate citations from your uploaded documents.")
        # How It Works
        st.subheader("How It Works")
        self.typewriter("1. **Upload a Document**: Simply drag and drop your document into the upload area or click to select files from your device.")
        self.typewriter("2. **Analyze**: DocuMate AI will process your document, extracting key information and preparing for your questions.")
        self.typewriter("3. **Interact with DocuMate AI**: Ask questions, seek clarifications, or request summaries from DocuMate AI.")
        self.typewriter("4. **Discover Answers**: DocuMate AI will provide you with accurate, relevant responses based on your queries.")
        # Get Started
        st.subheader("Get Started")
        self.typewriter("1. **Time-Saving**: Reduce hours of reading and analysis to minutes of intelligent interaction.")
        self.typewriter("2. **Accuracy**: Powered by advanced AI, ensuring precise and reliable information extraction.")
        self.typewriter("3. **User-Friendly**: Intuitive interface designed for users of all technical levels.")
        self.typewriter("4. **Secure**: Your documents are processed with the highest level of security and privacy.")
        self.typewriter("5. **Versatile**: Suitable for a wide range of industries and document types.")
        # Ending message
        st.markdown(f'<p style="text-align: center;padding: 7%;font-size: x-large;"><em><strong>Ready to experience the future of document interaction? Start your journey with DocuMate AI today!</strong></em></p>', unsafe_allow_html=True)
        # self.typewriter("#**Ready to experience the future of document interaction? Start your journey with DocuMate AI today!**")

    def create_fileUploader_Section(self):
        # File uploader widget
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a file", type=["pdf"])
        if uploaded_file is not None:
            self.upload_to_firebase(uploaded_file)
            # st.session_state.page='DocuMate Chatbot'
            # self.navigate_screens_basedOn_sessionState()
        st.markdown('</div>', unsafe_allow_html=True)

    # # Initialize session state to control the visibility of the file upload section
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False

    # Function to open the popup
    def open_popup(self):
        st.session_state.show_popup = True
        st.session_state.file_uploaded = False

    # Function to close the popup
    def close_popup(self):
        st.session_state.show_popup = False
    
    def display_pdf_preview(self, pdf_file):
        # Path to the PDF (can be a URL or local file path)
        pdf_url = pdf_file
        # Use an iframe to embed the PDF in Streamlit
        pdf_display = f'<iframe src="https://docs.google.com/viewer?url={pdf_url}&embedded=true" width="100%" height="1000" type="application/pdf"></iframe>'
        # Display the PDF in Streamlit
        st.components.v1.html(pdf_display, height=1000)

    def chatbot_response(self, message):
        # Placeholder for actual chatbot logic
        try:
            response = rag.get_response(message)  
        except Exception as e:
            response = "I'm sorry, I couldn't process requests currently. Please try again later."
        return f"Chatbot: '{response}'"    

    def createAndOpenChatbot(self, uploaded_file):
        global rag
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Document Preview")
            preview = self.display_pdf_preview(uploaded_file)
            rag = RAG(
                doc_path = uploaded_file,
                number_of_retrievals = 1,
                max_chat_tokens = 3097,
                creative = 1.5
            )

        with col2:
            st.subheader("Chat Interface")
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display chat messages from history on app rerun
            if "messages" in st.session_state:
                with st.expander("View Chat History"):
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

            # React to user input
            if prompt := st.chat_input("What is your question?"):
                # Display user message in chat message container
                st.chat_message("user").markdown(prompt)
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.spinner("Processing..."):
                    time.sleep(1)

                response = self.chatbot_response(prompt)
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

                        
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