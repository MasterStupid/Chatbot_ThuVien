from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import csv
import os
import uuid
import re
import time

from llm_service import get_cache_stats, clear_cache

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "metadata.csv")

# MAP TỪ KHÓA DANH MỤC -> TIỀN TỐ MÃ
CATEGORY_KEYWORDS = {
    "công nghệ thông tin": "CNTT",
    "cntt": "CNTT",
    "it": "CNTT",
    "tin học": "CNTT",
    "lập trình": "CNTT",

    "kinh tế": "KT",
    "kt": "KT",
    "quản trị kinh doanh": "KT",
    "marketing": "KT",

    "kế toán": "KTTC",
    "tài chính": "KTTC",
    "kttc": "KTTC",
    "kế toán tài chính": "KTTC",

    "du lịch": "DL",
    "dl": "DL",
    "khách sạn": "DL",
    "lữ hành": "DL",

    "ngoại ngữ": "NN",
    "nn": "NN",
    "tiếng anh": "NN",
    "english": "NN",

    "toán": "TN",
    "tn": "TN",
    "khoa học tự nhiên": "TN",
    "khtn": "TN",
    "toán và khoa học tự nhiên": "TN",
}

PREFIX_DISPLAY = {
    "CNTT": "Khoa Công nghệ thông tin",
    "KT": "Khoa Kinh tế và Quản trị kinh doanh",
    "KTTC": "Khoa Kế toán - Tài chính",
    "DL": "Khoa Du lịch",
    "NN": "Khoa Ngoại ngữ",
    "TN": "Khoa Toán và Khoa học tự nhiên",
}

def ensure_data_dir():
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'author', 'year', 'category', 'class_code', 'description'])

def load_books():
    books = []
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return books
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
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
    except Exception as e:
        print(f"Lỗi đọc sách: {e}")
    return books

def add_book(book):
    required = ["title", "author", "year", "category", "class_code", "description"]
    for field in required:
        if not book.get(field, "").strip():
            return False, f"Thiếu {field}"
    try:
        ensure_data_dir()
        file_exists = os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(required)
            writer.writerow([book[f].strip() for f in required])
        return True, "Thêm sách thành công!"
    except Exception as e:
        return False, f"Lỗi: {e}"

def get_books_by_prefix(prefix, books):
    prefix_upper = prefix.upper()
    return [b for b in books if b["class_code"].upper().startswith(prefix_upper)]

# ROUTES
@app.route("/")
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template("chat.html")

@app.route("/admin")
def admin():
    books = load_books()
    success = request.args.get('success', '')
    error = request.args.get('error', '')
    return render_template("admin.html", books=books, total_books=len(books), success=success, error=error)

@app.route("/add_book", methods=["POST"])
def add_book_route():
    book = {k: request.form.get(k, "").strip() for k in ["class_code", "title", "author", "year", "category", "description"]}
    success, msg = add_book(book)
    return redirect(url_for('admin', success=msg if success else None, error=msg if not success else None))

# CHAT API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "Yêu cầu không hợp lệ"}), 400

        message = data.get("message", "").lower().strip()
        if not message:
            return jsonify({"reply": "Vui lòng nhập câu hỏi!"})

        books = load_books()
        if not books:
            return jsonify({"reply": "📚 Thư viện chưa có sách."})

        # 1. Tìm theo mã chính xác
        match = re.search(r"([A-Za-z]+-\d+)", message)
        if match:
            code = match.group(1).upper()
            for b in books:
                if b["class_code"].upper() == code:
                    return jsonify({"books": [b], "message": f"📌 Sách mã {code}:"})
            return jsonify({"reply": f"❌ Không có mã {code}"})

        # 2. Tìm theo danh mục
        category_query = None
        if message.startswith("sách "):
            category_query = message[5:].strip()
        elif "tìm sách" in message:
            category_query = message.replace("tìm sách", "").strip()
        elif "danh mục" in message:
            parts = message.split("danh mục")
            if len(parts) > 1:
                category_query = parts[-1].strip()

        if category_query:
            matched_prefix = None
            for key, prefix in CATEGORY_KEYWORDS.items():
                if key in category_query or category_query in key:
                    matched_prefix = prefix
                    break
            if matched_prefix:
                results = get_books_by_prefix(matched_prefix, books)
                if results:
                    display_name = PREFIX_DISPLAY.get(matched_prefix, matched_prefix)
                    return jsonify({
                        "books": results,
                        "message": f"📚 {len(results)} sách {display_name}:"
                    })
                else:
                    return jsonify({"reply": f"❌ Danh mục này chưa có sách."})

        # 3. Tìm kiếm văn bản
        stop_words = ["cho", "tớ", "vài", "quyển", "về", "gợi", "ý", "có", "không", "bạn", "hãy", "giới", "thiệu", "tìm", "sách"]
        words = [w for w in message.split() if w not in stop_words and len(w) > 2]
        keywords = words if words else [message]

        results = []
        for b in books:
            title = b["title"].lower()
            author = b["author"].lower()
            desc = b["description"].lower()
            category = b["category"].lower()
            code = b["class_code"].lower()
            for kw in keywords:
                if kw in title or kw in author or kw in desc or kw in category or kw in code:
                    results.append(b)
                    break

        if results:
            seen = set()
            unique = []
            for b in results:
                if b["class_code"] not in seen:
                    seen.add(b["class_code"])
                    unique.append(b)
            return jsonify({"books": unique[:10]})

        # 4. Không tìm thấy, nhờ Ollama
        return jsonify({"use_llm": True, "query": message})

    except Exception as e:
        print(f"Lỗi chat: {e}")
        return jsonify({"reply": "❌ Đã xảy ra lỗi."}), 500

@app.route("/llm_chat", methods=["POST"])
def llm_chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"reply": "Vui lòng nhập câu hỏi!"})
        from llm_service import ask_llm
        reply = ask_llm(message)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Lỗi LLM: {e}")
        return jsonify({"reply": "❌ Lỗi kết nối AI."}), 500

# HƯỚNG DẪN (/HELP)
@app.route("/help", methods=["POST"])
def help():
    """Trả về hướng dẫn sử dụng dựa trên lệnh"""
    data = request.get_json() or {}
    command = data.get("command", "").strip().lower()

    # Hướng dẫn chung (mặc định)
    default_help = """
📚 **HƯỚNG DẪN SỬ DỤNG THỦ THƯ AI Agent**

Xin chào! Tôi là Thủ thư AI Agent của Trường Đại học Hải Phòng.

🔍 **Tìm kiếm sách:**
- Gõ tên sách: "Python", "Machine Learning"
- Gõ danh mục: "sách CNTT", "sách Kinh tế"
- Gõ mã sách: "CNTT-001", "KT-005"

💬 **Trò chuyện chung:**
- Hỏi về thư viện: "Thư viện có bao nhiêu sách?"
- Hỏi gợi ý: "Giới thiệu sách hay về Python"
- Yêu cầu giúp đỡ: "bạn giúp gì được?"

📌 **Mẹo nhỏ:**
- Nhấn vào danh mục bên trái để xem sách theo khoa.
- Gõ `/huongdan chat` để biết cách trò chuyện với AI.
- Gõ `/huongdan thuvien` để biết thông tin về thư viện thực tế (giờ mở cửa, quy định,...).

⚠️ **Lưu ý:** 
- Tôi trả lời dựa trên dữ liệu sách có sẵn. 
- Nếu không tìm thấy, tôi sẽ thông báo và gợi ý cách tìm khác. 
- Nếu xảy ra lỗi, vấn đề về thư viện mà tôi trả lời không chính xác, hãy trao đổi trực tiếp với các cô thủ thư khác để được hỗ trợ một cách đúng và đầy đủ nhất. 
 **Xin cám ơn sự ủng hộ của bạn!**
Nếu cần thêm trợ giúp, cứ hỏi tôi nhé! 😊
"""

    # Hướng dẫn riêng cho chat (cách dùng AI)
    chat_help = """
💬 **HƯỚNG DẪN TRÒ CHUYỆN VỚI AI**

Bạn có thể hỏi tôi bất cứ điều gì liên quan đến thư viện, sách vở.

**Các câu hỏi thường gặp:**
- "Thư viện có bao nhiêu sách?"
- "Giới thiệu sách hay về Python"
- "Có sách của tác giả Nguyễn Văn Ba không?"
- "Tìm sách danh mục Kinh tế"

⚠️ **Lưu ý:** 
- Tôi chỉ trả lời dựa trên dữ liệu sách có sẵn. Nếu không tìm thấy, tôi sẽ thông báo và gợi ý cách tìm khác.
- Nếu xảy ra lỗi, vấn đề về thư viện mà tôi trả lời không chính xác, hãy trao đổi trực tiếp với các cô trực quầy để được hỗ trợ một cách đúng và đầy đủ nhất. 
 **Xin cám ơn sự ủng hộ của bạn!**

💡 **Mẹo:** Hãy dùng từ khóa cụ thể để tìm chính xác hơn.
"""

    # Hướng dẫn riêng cho thư viện thực tế (ngoài đời)
    library_help = """
🏛️ **HƯỚNG DẪN SỬ DỤNG THƯ VIỆN THỰC TẾ**

**Địa chỉ:** Thư viện Trường Đại học Hải Phòng (Hiện ở tại tòa nhà A8 của Trường Đại học Hải Phòng).

🕒 **Giờ mở cửa:**
- Thứ 2 - Thứ 6: 7:30 - 17:00
- Thứ 7, Chủ nhật: Đóng cửa

📋 **Quy định mượn trả sách:**
- Xin vui lòng xem trực tiếp giấy nội quy tại thư viện tránh nhầm lẫn khi có sự thay đổi.

🌐 **Website:** https://lib.dhhp.edu.vn /  https://dlib.dhhp.edu.vn

Hãy đến thư viện để trải nghiệm không gian học tập và đọc sách nhé! 📖

⚠️ **Lưu ý:** 
- Tôi chỉ trả lời dựa trên dữ liệu sách có sẵn. Nếu không tìm thấy, tôi sẽ thông báo và gợi ý cách tìm khác.
- Nếu xảy ra lỗi, vấn đề về thư viện mà tôi trả lời không chính xác, hãy trao đổi trực tiếp với các cô trực quầy để được hỗ trợ một cách đúng và đầy đủ nhất. 
 **Xin cám ơn sự ủng hộ của bạn!**
"""

    # Chọn nội dung phù hợp
    if "chat" in command:
        reply = chat_help
    elif "thuvien" in command or "thư viện" in command:
        reply = library_help
    else:
        reply = default_help

    return jsonify({"reply": reply})

@app.route("/stats")
def stats():
    books = load_books()
    stats_data = {
        "total": len(books),
        "categories": {},
        "authors": {},
        "years": {},
        "prefixes": {}
    }
    for b in books:
        stats_data["categories"][b["category"]] = stats_data["categories"].get(b["category"], 0) + 1
        stats_data["authors"][b["author"]] = stats_data["authors"].get(b["author"], 0) + 1
        stats_data["years"][b["year"]] = stats_data["years"].get(b["year"], 0) + 1
        if "-" in b["class_code"]:
            p = b["class_code"].split("-")[0]
            stats_data["prefixes"][p] = stats_data["prefixes"].get(p, 0) + 1
    return jsonify(stats_data)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "books": len(load_books()),
        "session": session.get('session_id', 'none'),
        "time": time.time()
    })

@app.route("/debug/info")
def debug_info():
    books = load_books()
    categories = set(b["category"] for b in books)
    prefixes = set()
    for b in books:
        if "-" in b["class_code"]:
            prefixes.add(b["class_code"].split("-")[0])
    return jsonify({
        "categories": list(categories),
        "prefixes": list(prefixes),
        "total_books": len(books)
    })

@app.route("/cache/stats")
def cache_stats():
    """Xem thống kê cache"""
    return jsonify(get_cache_stats())

@app.route("/cache/clear")
def cache_clear():
    """Xóa cache"""
    return jsonify({"message": clear_cache()})

if __name__ == "__main__":
    print("=" * 60)
    print("📚 HPUni Library AI")
    print("Thủ thư AI Agent - Trường Đại học Hải Phòng")
    print("=" * 60)
    books = load_books()
    print(f"\n📊 Đã tải {len(books)} sách")
    print("\n✅ Các tiền tố mã có trong dữ liệu:")
    prefixes = set()
    for b in books:
        if "-" in b["class_code"]:
            prefixes.add(b["class_code"].split("-")[0])
    for p in sorted(prefixes):
        count = len([b for b in books if b["class_code"].startswith(p)])
        print(f"   • {p}: {count} sách")
    print("\n" + "=" * 60)
    app.run(host="0.0.0.0", port=411, debug=True)