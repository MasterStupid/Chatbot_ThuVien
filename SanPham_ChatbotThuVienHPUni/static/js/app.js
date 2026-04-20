const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const typing = document.getElementById("typing");

const inputWrapper = document.querySelector('.input-wrapper');

let sessionId = localStorage.getItem('chatSessionId') || generateSessionId();
let conversationContext = [];
localStorage.setItem('chatSessionId', sessionId);

// Cấu hình marked
marked.setOptions({
    breaks: true,
    gfm: true,
    sanitize: false
});

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function scrollToBottom() {
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

function showInput() {
    inputWrapper.style.display = 'flex'; // Hiện thanh chat
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.focus();
}

function hideInput() {
    inputWrapper.style.display = 'none'; // Ẩn thanh chat 
    chatInput.disabled = true;
    sendBtn.disabled = true;
}

function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "user-message";
    div.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
        <div class="message-time">${formatTime()}</div>
    `;
    chatBox.appendChild(div);
    scrollToBottom();
    conversationContext.push({ role: 'user', content: text });
}

function addBotMessage(text) {
    const div = document.createElement("div");
    div.className = "bot-message";
    const htmlContent = marked.parse(text);
    div.innerHTML = `
        <div class="bot-avatar-small">🐧</div>
        <div class="message-wrapper">
            <div class="message-content">${htmlContent}</div>
            <div class="message-time">${formatTime()}</div>
        </div>
    `;
    chatBox.appendChild(div);
    scrollToBottom();
    conversationContext.push({ role: 'assistant', content: text });
}

function addBookCard(book) {
    const card = document.createElement("div");
    card.className = "book-card";

    const title = book.title || 'Không có tiêu đề';
    const classCode = book.class_code || 'N/A';
    const author = book.author || 'Không rõ';
    const year = book.year || 'N/A';
    const category = book.category || 'Khác';
    const description = book.description || 'Không có mô tả';

    card.innerHTML = `
        <div class="book-card-header">
            <span class="book-emoji">📚</span>
            <span class="book-title">${escapeHtml(title)}</span>
        </div>
        <div class="book-meta">
            <div class="meta-item"><span class="meta-label">📌 Mã: </span> <span class="meta-value">${escapeHtml(classCode)}</span></div>
            <div class="meta-item"><span class="meta-label">✍️ Tác giả: </span> <span class="meta-value">${escapeHtml(author)}</span></div>
            <div class="meta-item"><span class="meta-label">📅 Năm: </span> <span class="meta-value">${escapeHtml(year)}</span></div>
            <div class="meta-item"><span class="meta-label">🏷️ Danh mục: ‌󠁢󠁢󠁢󠁦󠁮󠁢󠁢󠁭󠁳󠁷󠁢󠁢󠁢󠁣󠁨󠁢󠁢󠁭󠁳󠁭󠁢󠁢󠁢󠁦󠁧󠁢󠁢󠁢󠁣󠁨󠁢󠁢󠁢󠁦󠁧󠁢󠁢󠁭󠁱󠁵󠁢󠁢󠁢󠁦󠁮󠁢󠁢󠁢󠁣󠁨󠁢󠁢󠁢󠁦󠁬󠁢󠁢󠁢󠁫󠁬󠁢󠁢󠁢󠁦󠁣󠁡 </span> <span class="meta-value">${escapeHtml(category)}</span></div>
            <div class="meta-item description"><span class="meta-label">📝 Mô tả: </span> <span class="meta-value">${escapeHtml(description)}</span></div>
        </div>
    `;
    chatBox.appendChild(card);
    scrollToBottom();
}

function renderBooks(books, prependMessage = null) {
    if (!books || books.length === 0) {
        addBotMessage("❌ Không tìm thấy sách phù hợp.");
        return;
    }
    if (prependMessage) {
        addBotMessage(prependMessage);
    }
    books.forEach(book => addBookCard(book));
}

function showTyping() {
    hideInput();
    
    typing.style.display = "flex";
    typing.style.alignItems = "center";
    typing.style.gap = "10px";
    typing.style.padding = "10px 15px";
    
    typing.innerHTML = `
        <div class="ai-thinking-logo">✨</div> 
        <span style="color: #9aa8b9; font-size: 14px; display: flex; align-items: center; font-style: italic;">
            Thủ thư AI đang suy nghĩ <span class="ai-cursor"></span>
        </span>
    `;
    scrollToBottom();
}

function hideTyping() {
    typing.style.display = "none";
    typing.innerHTML = '';
}

function showWelcomeMessage() {
    const welcomeDiv = document.createElement("div");
    welcomeDiv.className = "welcome-message";

    const hours = new Date().getHours();
    let greeting = "Chào bạn";
    if (hours < 11) greeting = "Chào buổi sáng";
    else if (hours < 13) greeting = "Chào buổi trưa";
    else if (hours < 18) greeting = "Chào buổi chiều";
    else greeting = "Chào buổi tối";

    welcomeDiv.innerHTML = `
        <div class="welcome-avatar">
            <img src="/static/images/logo.png" 
                 alt="Đại học Hải Phòng" 
                 style="width:80px; height:80px; border-radius:50%; object-fit:cover;">
        </div>
        <h2>${greeting}! Tôi là Thủ thư AI Agent</h2>
        <p>Thư viện Trường Đại học Hải Phòng - Tư vấn, hỏi đáp sách 24/7</p>
        <div class="welcome-stats" id="welcomeStats"><span>📚 Đang tải dữ liệu...</span></div>
        <div class="quick-actions">
            <button class="quick-action-btn" onclick="quickSearch('sách CNTT')">💻 Công Nghệ Thông Tin</button>
            <button class="quick-action-btn" onclick="quickSearch('sách Kinh tế')">📊 Kinh tế</button>
            <button class="quick-action-btn" onclick="quickSearch('python')">🐍 Python</button>
            <button class="quick-action-btn" onclick="quickSearch('machine learning')">🤖 Machine Learning</button>
        </div>
        <div class="suggestion-text">💡 Thử hỏi: "Du lịch", "Công nghệ thông tin", "Kinh tế" <br>Để xem hướng dẫn sử dụng hãy <b>/huongdan</b> </div>
    `;
    chatBox.appendChild(welcomeDiv);
    loadWelcomeStats();
}

async function loadWelcomeStats() {
    try {
        const res = await fetch('/stats');
        const data = await res.json();
        const statsDiv = document.getElementById('welcomeStats');
        if (statsDiv) {
            statsDiv.innerHTML = `
                <span>📚 Tổng số: ${data.total || 0} sách</span> |
                <span>🏷️ ${Object.keys(data.categories || {}).length} danh mục</span> |
                <span>✍️ ${Object.keys(data.authors || {}).length} tác giả</span>
            `;
        }
    } catch (e) {
        console.log('Không tải được stats');
    }
}

window.quickSearch = function(query) {
    chatInput.value = query;
    sendMessage();
};

async function sendMessage() {
    const message = chatInput.value.trim();
    if (message === "") {
        chatInput.style.borderColor = "#ff4444";
        setTimeout(() => chatInput.style.borderColor = "#3b82f6", 1000);
        return;
    }

    if (message.startsWith("/huongdan") || message.startsWith("/help")) {
        hideInput();
        addUserMessage(message);
        chatInput.value = "";
        showTyping();

        try {
            const res = await fetch("/help", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command: message })
            });
            const data = await res.json();
            hideTyping();
            if (data.reply) addBotMessage(data.reply);
        } catch (error) {
            hideTyping();
            addBotMessage("❌ Lỗi khi tải hướng dẫn.");
        } finally {
            showInput();
        }
        return;
    }

    hideInput();
    addUserMessage(message);
    chatInput.value = "";
    showTyping();

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); 

        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                message, 
                session_id: sessionId, 
                history: conversationContext.slice(-10) 
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const data = await res.json();
        hideTyping();

        if (data.use_llm) {
            await getLLMResponse(data.query || message);
        } else {
            if (data.books && data.books.length > 0) {
                renderBooks(data.books, data.message || null);
            } else if (data.reply) {
                addBotMessage(data.reply);
            } else {
                addBotMessage("Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về sách, tác giả hoặc danh mục cụ thể không?");
            }
            showInput();
        }

    } catch (error) {
        hideTyping();
        console.error("Error:", error);
        addBotMessage("❌ Lỗi kết nối. Vui lòng thử lại.");
        showInput();
    }
}

async function getLLMResponse(query) {
    showTyping();
    try {
        const res = await fetch("/llm_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: query, session_id: sessionId })
        });
        const data = await res.json();
        hideTyping();
        if (data.reply) {
            addBotMessageTypewriter(data.reply);
        } else {
            addBotMessage("Xin lỗi, tôi không thể tìm thấy thông tin phù hợp.");
            showInput();
        }
    } catch (error) {
        hideTyping();
        addBotMessage("❌ Lỗi kết nối đến AI Agent. Vui lòng thử lại sau!");
        showInput();
    }
}

function clearChat() {
    if (confirm('Bạn có muốn xóa lịch sử trò chuyện?')) {
        chatBox.innerHTML = '';
        conversationContext = [];
        
        sessionId = generateSessionId();
        localStorage.setItem('chatSessionId', sessionId);

        showWelcomeMessage();
        addBotMessage("👋 Đã xóa lịch sử. Hệ thống đã thoát chế độ LLM và chúng ta có thể bắt đầu lại!");
        showInput();
    }
}

function showHelp() {
    const help = `
🤖 **HƯỚNG DẪN SỬ DỤNG**

📚 **Tìm sách:**
• Gõ tên sách: "Python", "Machine Learning"
• Gõ tác giả: "sách của Nguyễn Văn Ba"
• Gõ mã sách: "CNTT-001" (Ưu tiên nhất)

💬 **Trò chuyện:**
• Hỏi thông tin: "Thư viện có bao nhiêu sách?"
• Bắt đầu chat với LLM: Gọi từ khóa "ollama" trong câu lệnh

⌨️ **Phím tắt:**
• Enter: Gửi tin nhắn
• Ctrl+L: Xóa lịch sử chat (đồng thời thoát chế độ LLM)
• Ctrl+H: Hiện hướng dẫn này
    `;
    addBotMessage(help);
}

chatInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
    if (e.ctrlKey && e.key === 'h') {
        e.preventDefault();
        showHelp();
    }
});

window.onload = function() {
    loadWelcomeStats();
    showWelcomeMessage();
    chatInput.focus();

    fetch('/health')
        .then(res => res.json())
        .then(data => {
            console.log('✅ Connected to server');
            if (data.books === 0) {
                addBotMessage("📚 Thư viện đang cập nhật dữ liệu. Bạn có thể thêm sách trong trang Admin!");
            }
        })
        .catch(err => {
            console.error('❌ Cannot connect to server:', err);
            addBotMessage('⚠️ Không thể kết nối đến server. Vui lòng kiểm tra lại!');
        });
};

function addBotMessageTypewriter(text) {
    hideInput();

    const div = document.createElement("div");
    div.className = "bot-message";
    div.innerHTML = `
        <div class="bot-avatar-small">🐥</div>
        <div class="message-wrapper">
            <div class="message-content"></div>
            <div class="message-time">${formatTime()}</div>
        </div>
    `;
    chatBox.appendChild(div);
    scrollToBottom();

    const contentDiv = div.querySelector('.message-content');
    let index = 0;
    let currentText = "";
    const typingSpeed = 15;

    const typeInterval = setInterval(() => {
        if (index < text.length) {
            currentText += text.charAt(index);
            contentDiv.innerHTML = marked.parse(currentText); 
            scrollToBottom();
            index++;
        } else {
            clearInterval(typeInterval);
            conversationContext.push({ role: 'assistant', content: text });
            showInput(); 
        }
    }, typingSpeed);
}

// THEME TOGGLE
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('theme-toggle');
    
    body.classList.toggle('light-mode');
    
    if (body.classList.contains('light-mode')) {
        themeBtn.innerHTML = '🌙 Chế độ tối';
        localStorage.setItem('theme', 'light');
    } else {
        themeBtn.innerHTML = '🌞 Chế độ sáng';
        localStorage.setItem('theme', 'dark');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const themeBtn = document.getElementById('theme-toggle');
    
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        if(themeBtn) themeBtn.innerHTML = '🌙 Chế độ tối';
    } else {
        if(themeBtn) themeBtn.innerHTML = '🌞 Chế độ sáng';
    }
});