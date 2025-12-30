import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
import asyncio

# API tokens
HUGGINGFACE_API_TOKEN = "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"

if not HUGGINGFACE_API_TOKEN:
    st.error("HUGGINGFACE_API_TOKEN is not set.")
    st.stop()

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDF documents."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text.strip()

def get_text_chunks(text):
    """Split the text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Create and cache a FAISS vector store."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    """Create a conversational chain with custom prompts."""
    prompt_template = """
    Use the provided context to answer the user's question. If no relevant context is found, respond:
    "Sorry, I couldn't find sufficient information in the document."

    Context: {context}
    Question: {question}

    Answer:
    """
    model = HuggingFaceHub(
        repo_id="google/flan-t5-base", 
        model_kwargs={"temperature": 0.5, "max_length": 768},  
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN
    )
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    return load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)

async def process_user_input(user_question):
    """Process user questions asynchronously."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question, k=3)

        if not docs:
            return "Sorry, I couldn't find relevant information in the uploaded documents."

        chain = get_conversational_chain()
        response = chain.run(input_documents=docs, question=user_question)
        
        st.session_state.messages.append({"role": "user", "content": user_question})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        return response
    except Exception as e:
        return f"Error processing your query: {str(e)}"

def display_chat():
    """Display the chat history."""
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assistant").markdown(message["content"])

def extract_text(uploaded_files):
    """
    Extract text content from uploaded files (PDFs and .txt).
    Supports PDF files and plain text files.
    """
    text = ""
    for file in uploaded_files:
        file_type = file.name.split(".")[-1].lower()
        
        if file_type == "pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        elif file_type == "txt":
            text += file.read().decode("utf-8")  # Assuming UTF-8 encoding for text files
        else:
            st.warning(f"Unsupported file type: {file.name}. Only PDFs and .txt files are supported.")
    
    if not text.strip():
        st.error("No text could be extracted from the uploaded files.")
    return text.strip()

# Update the main function to use the new extraction method
def main():
    """Main application function."""
    st.set_page_config("Multi File Chatbot", page_icon=":robot:", layout="wide")
    st.title("PDF Reader Chatbot 🤖")
    
    with st.sidebar:
        st.header("📁 File Upload")
        uploaded_files = st.file_uploader(
            "Upload your PDF or Text files",
            accept_multiple_files=True
        )
        
        if st.button("Process Files"):
            if not uploaded_files:
                st.warning("Please upload files first!")
                return
            
            with st.spinner("Processing..."):
                raw_text = extract_text(uploaded_files)
                if not raw_text:
                    st.error("No text could be extracted from the uploaded files.")
                    return
                
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Processing complete! Vector store created.")
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.experimental_rerun()
    
    # Display the chat history
    display_chat()
    
    # Chat Input
    if prompt := st.chat_input("Ask a question about your uploaded files..."):
        if not os.path.exists("faiss_index"):
            st.warning("Please process files first!")
            return
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(process_user_input(prompt))
                st.markdown(response)

# Run the main application
if __name__ == "__main__":
    main()
