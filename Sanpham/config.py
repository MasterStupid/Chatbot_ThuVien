import os

# BASE PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DATA PATH
DATA_DIR = os.path.join(BASE_DIR, "data")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.csv")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
VECTOR_DIR = os.path.join(DATA_DIR, "vectors")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

# VECTOR STORAGE
CHUNKS_FILE = os.path.join(VECTOR_DIR, "chunks.pkl")
FAISS_INDEX = os.path.join(VECTOR_DIR, "faiss.index")

# OLLAMA CONFIG
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2:0.5b"
OLLAMA_TIMEOUT = 30

# SERVER CONFIG
HOST = "0.0.0.0"
PORT = 411
DEBUG = True

# CHATBOT SYSTEM PROMPT
SYSTEM_PROMPT = """
Bạn là THỦ THƯ AI của Thư viện Trường Đại học Hải Phòng.

Nhiệm vụ:
- Giới thiệu sách trong thư viện
- Hướng dẫn sinh viên tìm tài liệu
- Trả lời câu hỏi học thuật

Quy tắc:
- Nếu thư viện có sách → giới thiệu sách đó
- Không tự bịa sách ngoài thư viện
- Nếu không có sách → nói rõ thư viện chưa có
"""

# MEMORY CONFIG
MAX_MEMORY_MESSAGES = 10
SESSION_TIMEOUT = 3600  # 1 hour

# SEARCH CONFIG
MAX_SEARCH_RESULTS = 10
MIN_SEARCH_TERM_LENGTH = 2

# UPLOAD CONFIG
ALLOWED_EXTENSIONS = {'pdf'}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

print(f"✅ Configuration loaded")
print(f"📁 Data directory: {DATA_DIR}")
print(f"📁 PDF directory: {PDF_DIR}")
print(f"📁 Vector directory: {VECTOR_DIR}")