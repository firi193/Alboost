import os
import time
import logging
import requests
from functools import wraps
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import tempfile
import os
# Load environment variables from .env if present
load_dotenv()

# ---------- Logging ----------
LOG_FILE = "logs/agent_events.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log_event(agent_name, message):
    """Logs a message with the agent's name."""
    logging.info(f"[{agent_name}] {message}")

# ---------- Retry with Backoff ----------
def retry_with_backoff(max_retries=3, delay=2, backoff=2):
    """Retry decorator with exponential backoff."""
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    log_event(func.__name__, f"Error: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            raise Exception(f"Function {func.__name__} failed after {max_retries} retries.")
        return wrapper
    return decorator_retry

# ---------- Text Cleaning ----------
def clean_text(text):
    """Basic cleaning of text from LLM or user input."""
    return text.strip().replace('\n', ' ').replace('\r', '')

# ---------- Env Var Loader ----------
def load_env_var(key, default=None):
    """Loads an environment variable safely."""
    value = os.getenv(key, default)
    if value is None:
        raise EnvironmentError(f"Environment variable '{key}' not set.")
    return value

# ---------- Telegram Integration ----------
def send_message_via_telegram(text, chat_id=None, bot_token=None):
    """Send a message to Telegram."""
    chat_id = chat_id or load_env_var("TELEGRAM_CHAT_ID")
    bot_token = bot_token or load_env_var("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_event("Telegram", f"Failed to send message: {e}")
        return None
    


# Load embedding model once (can be global)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def build_temp_vectorstore_from_data(df=None, pdf_text=None):
    """
    Converts a DataFrame or PDF text into text chunks, embeds them,
    and loads into an in-memory Chroma vectorstore.
    
    Returns:
        Chroma vectorstore instance (in-memory)
    """
    if df is None and pdf_text is None:
        raise ValueError("Must provide either a DataFrame or PDF text.")

    # Convert DataFrame to plain text
    raw_text = ""
    if df is not None:
        raw_text += df.to_csv(index=False)

    if pdf_text is not None:
        raw_text += "\n" + pdf_text

    # Chunk the text
    chunks = text_splitter.split_text(raw_text)

    # Wrap as LangChain Documents
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Create temp directory for Chroma
    persist_dir = tempfile.mkdtemp()

    # Build vectorstore
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_dir
    )

    return vectorstore

