# llm_service.py - CÂN BẰNG TỐC ĐỘ & CHẤT LƯỢNG

import requests
import csv
import os
import time
import hashlib

# ==============================
# CẤU HÌNH - CÂN BẰNG
# ==============================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2:0.5b"  # Vẫn giữ model nhẹ
OLLAMA_TIMEOUT = 45

SYSTEM_PROMPT = """Bạn là AI Thủ thư của Đại học Hải Phòng, chuyên gia về sách và tài liệu học thuật.
NHIỆM VỤ:
- Tư vấn, giới thiệu sách phù hợp với nhu cầu người dùng
- Giải thích nội dung sách một cách dễ hiểu
- Gợi ý các sách liên quan cùng chủ đề
- Trả lời lịch sự, thân thiện, có chiều sâu

QUY TẮC:
- CHỈ giới thiệu sách CÓ TRONG danh sách thư viện
- Nếu không có sách phù hợp, hãy đề xuất các sách cùng thể loại
- Nếu hỏi về chủ đề, hãy phân tích và gợi ý nhiều góc nhìn
- Trả lời bằng tiếng Việt tự nhiên, có thể dùng emoji
"""

# ==============================
# CACHE THÔNG MINH
# ==============================
class ChatCache:
    def __init__(self, expire_hours=48, max_size=200):
        self.cache = {}
        self.expire_hours = expire_hours
        self.max_size = max_size
        self.stats = {"hits": 0, "misses": 0}
    
    def _get_key(self, question):
        return hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    def get(self, question):
        key = self._get_key(question)
        if key in self.cache:
            answer, timestamp = self.cache[key]
            if time.time() - timestamp < self.expire_hours * 3600:
                self.stats["hits"] += 1
                print(f"⚡ Cache HIT")
                return answer
            else:
                del self.cache[key]
        self.stats["misses"] += 1
        return None
    
    def set(self, question, answer):
        key = self._get_key(question)
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = (answer, time.time())
        print(f"💾 Cache SAVED")

chat_cache = ChatCache()

# ==============================
# ĐỌC SÁCH
# ==============================
def load_books():
    books = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.join(base_dir, "data", "metadata.csv")
    
    if not os.path.exists(metadata_path):
        return books
    
    try:
        with open(metadata_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book = {
                    "title": row.get("title", "").strip(),
                    "author": row.get("author", "").strip(),
                    "year": row.get("year", "").strip(),
                    "category": row.get("category", "").strip(),
                    "class_code": row.get("class_code", "").strip(),
                    "description": row.get("description", "").strip()
                }
                if book["title"]:
                    books.append(book)
        print(f"✅ Đã tải {len(books)} sách")
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
    
    return books

# ==============================
# XÂY DỰNG CONTEXT - ĐẦY ĐỦ THÔNG TIN
# ==============================
def build_library_context(books=None, max_books=10):
    """Tạo context chi tiết hơn cho từng sách"""
    if books is None:
        books = load_books()
    
    if not books:
        return "📚 Thư viện chưa có sách."
    
    books_to_show = books[:max_books]
    context = "📚 DANH SÁCH SÁCH THƯ VIỆN:\n\n"
    
    for i, book in enumerate(books_to_show, 1):
        context += f"{i}. {book['title']}\n"
        context += f"   ✍️ Tác giả: {book['author']}\n"
        context += f"   📅 Năm: {book['year']}\n"
        context += f"   🏷️ Thể loại: {book['category']}\n"
        context += f"   📝 Mô tả: {book['description'][:100]}...\n\n"
    
    if len(books) > max_books:
        context += f"... và {len(books) - max_books} sách khác.\n"
    
    return context

# ==============================
# KIỂM TRA OLLAMA
# ==============================
def check_ollama():
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False

# ==============================
# FALLBACK THÔNG MINH HƠN
# ==============================
def fallback_response(question, books):
    """Fallback có suy nghĩ"""
    if not books:
        return "📚 Thư viện chưa có sách nào. Bạn có thể góp ý để thư viện bổ sung nhé!"
    
    q = question.lower()
    
    # Phân tích câu hỏi
    categories = set()
    authors = set()
    results = []
    
    for book in books:
        title_match = q in book['title'].lower()
        author_match = q in book['author'].lower()
        cat_match = q in book['category'].lower()
        
        if title_match or author_match or cat_match:
            results.append(book)
            if cat_match:
                categories.add(book['category'])
            if author_match:
                authors.add(book['author'])
    
    if results:
        reply = f"📖 **Tìm thấy {len(results)} sách liên quan:**\n\n"
        for book in results[:5]:
            reply += f"• **{book['title']}** - {book['author']} ({book['year']})\n"
            reply += f"  *{book['description'][:80]}...*\n\n"
        
        if categories:
            reply += f"🏷️ **Thể loại liên quan:** {', '.join(list(categories)[:3])}\n"
        if authors:
            reply += f"✍️ **Tác giả:** {', '.join(list(authors)[:3])}\n"
        
        return reply
    
    # Gợi ý thông minh
    top_cats = {}
    for book in books[:20]:
        top_cats[book['category']] = top_cats.get(book['category'], 0) + 1
    
    popular_cats = sorted(top_cats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    reply = f"❌ Không tìm thấy sách phù hợp với '{question}'.\n\n"
    reply += "💡 **Bạn có thể thử:**\n"
    reply += "• Tìm theo thể loại: " + ", ".join([f"`{cat}`" for cat, _ in popular_cats]) + "\n"
    reply += "• Tìm theo tác giả: `Nguyễn Văn Ba`, `Trần Văn Bình`\n"
    reply += "• Tìm theo từ khóa: `Python`, `Machine Learning`, `Kinh tế`\n\n"
    reply += f"📚 Hiện thư viện có **{len(books)} sách** với **{len(set(b['category'] for b in books))} thể loại**."
    
    return reply

# ==============================
# GỌI OLLAMA - CÂN BẰNG TỐC ĐỘ & CHẤT LƯỢNG
# ==============================
def ask_llm(user_question):
    """Gọi Ollama với chất lượng tốt hơn"""
    
    # Kiểm tra cache
    cached = chat_cache.get(user_question)
    if cached:
        return cached
    
    # Kiểm tra Ollama
    if not check_ollama():
        return fallback_response(user_question, load_books())
    
    # Đọc sách
    books = load_books()
    context = build_library_context(books)
    
    # Prompt chi tiết hơn
    prompt = f"""{SYSTEM_PROMPT}

{context}

NGƯỜI DÙNG: {user_question}

HÃY SUY NGHĨ VÀ TRẢ LỜI:
1. Xác định chính xác nhu cầu của người dùng
2. Tìm sách phù hợp trong danh sách trên
3. Giới thiệu chi tiết: nội dung, tác giả, năm xuất bản
4. Giải thích tại sao sách đó phù hợp
5. Gợi ý thêm sách cùng chủ đề (nếu có)
6. Nếu không có sách, đề xuất thể loại tương tự
7. Trả lời bằng tiếng Việt tự nhiên, thân thiện

AI THỦ THƯ:"""

    # Payload CÂN BẰNG (không quá nhanh, không quá chậm)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,        # Tăng lên để sáng tạo hơn
            "num_predict": 400,         # Cho phép trả lời dài hơn
            "top_k": 40,                 # Mở rộng tìm kiếm
            "top_p": 0.9,
            "num_ctx": 2048,             # Context window vừa phải
            "repeat_penalty": 1.1,
            "num_thread": 6
        }
    }

    try:
        start = time.time()
        print(f"🔄 Đang suy nghĩ...")
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("response", "").strip()
            
            elapsed = time.time() - start
            print(f"✅ Hoàn thành trong {elapsed:.2f} giây")
            
            if reply:
                chat_cache.set(user_question, reply)
                return reply
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    return fallback_response(user_question, books)

# ==============================
# TEST
# ==============================
def test():
    questions = [
        "Tôi muốn học lập trình Python, có sách nào không?",
        "Giới thiệu sách về Machine Learning cho người mới bắt đầu",
        "Sách của tác giả Nguyễn Văn Ba viết về gì?",
        "Có sách kinh tế nào hay không?",
        "Thư viện có những sách gì về trí tuệ nhân tạo?"
    ]
    
    print("\n" + "=" * 60)
    print("🧪 TEST CHẤT LƯỢNG & TỐC ĐỘ")
    print("=" * 60)
    
    for q in questions:
        print(f"\n📝 Câu hỏi: {q}")
        print("-" * 40)
        start = time.time()
        answer = ask_llm(q)
        elapsed = time.time() - start
        print(f"⏱️ {elapsed:.2f} giây")
        print(f"💬 {answer[:200]}...")

if __name__ == "__main__":
    test()

def get_cache_stats():
    return {}

def clear_cache():
    return True