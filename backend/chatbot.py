import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter  

# Initialize FastAPI app
app = FastAPI()

# ✅ Fix CORS for React (Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change "*" to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Define supported CDP platforms
CDP_KEYWORDS = ["segment", "mparticle", "lytics", "zeotap"]

def load_docs():
    """Loads `docs.txt` and returns its content"""
    if not os.path.exists("docs.txt"):
        raise FileNotFoundError("🚨 ERROR: docs.txt not found!")

    with open("docs.txt", "r", encoding="utf-8") as f:
        return f.read()

def extract_keyword(query: str):
    """Extracts relevant CDP keyword from the query"""
    for keyword in CDP_KEYWORDS:
        if keyword in query.lower():
            return keyword
    return None  # No keyword found

def extract_answer_for_cdp(docs_text, cdp_keyword):
    """
    Finds the relevant section for the CDP keyword in `docs.txt`
    and extracts the answer until the next "---".
    """
    docs_lower = docs_text.lower()
    keyword_index = docs_lower.find(cdp_keyword)

    if keyword_index == -1:
        return None  # No section found for this keyword

    # ✅ Extract from the keyword position onward
    extracted_text = docs_text[keyword_index:]
    
    # ✅ Stop extraction at next "---"
    stop_index = extracted_text.find("---")
    if stop_index != -1:
        extracted_text = extracted_text[:stop_index]

    return extracted_text.strip()  # Remove extra spaces

@app.get("/")
def read_root():
    return {"message": "Chatbot API is running! This chatbot only answers 'how-to' questions."}

# Define request model for queries
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_chatbot(request: QueryRequest):
    """Handles user queries by directly searching `docs.txt` for relevant answers"""
    query = request.query.strip()

    # ✅ Ensure query follows "How to" format
    if not query.lower().startswith("how to") and not query.lower().startswith("how do i"):
        return {"answer": "❌ Sorry, I only answer 'how-to' questions."}

    # ✅ Extract CDP keyword from the query
    query_cdp = extract_keyword(query)
    if not query_cdp:
        return {"answer": "❌ No valid CDP found in query!"}

    print(f"🔍 Searching docs.txt for: {query_cdp}")

    # ✅ Load `docs.txt` and extract relevant content
    docs_text = load_docs()
    extracted_answer = extract_answer_for_cdp(docs_text, query_cdp)

    if not extracted_answer:
        return {"answer": "❌ No relevant answer found in docs.txt!"}

    # ✅ Format answer with line breaks
    formatted_answer = extracted_answer.replace(". ", ".\n")  

    print(f"✅ Answer found:\n{formatted_answer}\n")
    return {"answer": formatted_answer}
