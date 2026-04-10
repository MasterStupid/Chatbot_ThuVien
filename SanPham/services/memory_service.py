import time
import uuid
from collections import OrderedDict
from config import MAX_MEMORY_MESSAGES, SESSION_TIMEOUT

memory_store = {}

# SESSION MANAGEMENT
def create_session():
    """
    Create a new chat session
    Returns:
        session_id string
    """
    session_id = str(uuid.uuid4())
    current_time = time.time()
    
    memory_store[session_id] = {
        "created_at": current_time,
        "last_active": current_time,
        "messages": []
    }
    
    # Add welcome message
    add_message(session_id, "assistant", "👋 Xin chào! Tôi là Thủ thư AI Agent của Trường Đại học Hải Phòng. Tôi có thể giúp gì cho bạn?")
    return session_id

def get_session(session_id):
    """
    Get session data
    Args:
        session_id: Session identifier
    Returns:
        Session dict or None if not found/expired
    """
    if session_id not in memory_store:
        return None
    
    session = memory_store[session_id]
    
    # Check if session expired
    if time.time() - session["last_active"] > SESSION_TIMEOUT:
        delete_session(session_id)
        return None
    
    # Update last active time
    session["last_active"] = time.time()
    
    return session


def delete_session(session_id):
    """
    Delete a session
    Args:
        session_id: Session identifier
    """
    if session_id in memory_store:
        del memory_store[session_id]
        return True
    return False


def cleanup_expired_sessions():
    """
    Remove all expired sessions
    Returns:
        Number of sessions removed
    """
    current_time = time.time()
    expired = []
    
    for session_id, session in memory_store.items():
        if current_time - session["last_active"] > SESSION_TIMEOUT:
            expired.append(session_id)
    
    for session_id in expired:
        del memory_store[session_id]
    
    return len(expired)

# MESSAGE MANAGEMENT
def get_history(session_id):
    """
    Get message history for a session
    Args:
        session_id: Session identifier
    Returns:
        List of messages
    """
    session = get_session(session_id)
    if not session:
        return []
    return session["messages"]

def add_message(session_id, role, content):
    """
    Add a message to session history
    Args:
        session_id: Session identifier
        role: "user" or "assistant"
        content: Message content
    Returns:
        Boolean indicating success
    """
    session = get_session(session_id)
    if not session:
        # Create new session if doesn't exist
        session_id = create_session()
        session = memory_store[session_id]
    
    message = {
        "role": role,
        "content": content,
        "timestamp": time.time()
    }
    
    session["messages"].append(message)
    
    # Keep only last N messages
    if len(session["messages"]) > MAX_MEMORY_MESSAGES * 2:  # *2 because user+assistant pairs
        session["messages"] = session["messages"][-MAX_MEMORY_MESSAGES * 2:]
    return True

def get_conversation_context(session_id, max_messages=MAX_MEMORY_MESSAGES):
    """
    Get formatted conversation context for LLM
    Args:
        session_id: Session identifier
        max_messages: Maximum number of messages to include
    Returns:
        Formatted conversation string
    """
    messages = get_history(session_id)
    
    if not messages:
        return ""
    
    # Take last N messages
    recent_messages = messages[-max_messages:]
    
    context = "LỊCH SỬ TRÒ CHUYỆN GẦN ĐÂY:\n"
    for msg in recent_messages:
        role = "Người dùng" if msg["role"] == "user" else "Thủ thư AI Agent"
        context += f"{role}: {msg['content']}\n"
    
    return context

def clear_history(session_id):
    """
    Clear message history for a session
    Args:
        session_id: Session identifier
    """
    session = get_session(session_id)
    if session:
        session["messages"] = []
        return True
    return False

# UTILITY FUNCTIONS
def get_all_sessions():
    """
    Get all active sessions
    Returns:
        Dictionary of sessions
    """
    cleanup_expired_sessions()
    return memory_store

def get_session_count():
    """
    Get number of active sessions
    Returns:
        Integer count
    """
    cleanup_expired_sessions()
    return len(memory_store)

def get_total_messages():
    """
    Get total number of messages across all sessions
    Returns:
        Integer count
    """
    total = 0
    for session in memory_store.values():
        total += len(session["messages"])
    return total

def format_timestamp(timestamp):
    """
    Format timestamp for display
    Args:
        timestamp: Unix timestamp
    Returns:
        Formatted time string
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

# SESSION STATS
def get_session_stats(session_id):
    """
    Get statistics for a session
    Args:
        session_id: Session identifier
    Returns:
        Dictionary with session stats
    """
    session = get_session(session_id)
    if not session:
        return None
    
    messages = session["messages"]
    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    
    return {
        "session_id": session_id,
        "created_at": format_timestamp(session["created_at"]),
        "last_active": format_timestamp(session["last_active"]),
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "duration": int(session["last_active"] - session["created_at"])
    }

# Initialize with cleanup thread (optional)
def start_cleanup_thread(interval=300):  # 5 minutes
    """
    Start a background thread to clean up expired sessions
    Args:
        interval: Cleanup interval in seconds
    """
    import threading
    
    def cleanup_worker():
        while True:
            time.sleep(interval)
            removed = cleanup_expired_sessions()
            if removed > 0:
                print(f"🧹 Cleaned up {removed} expired sessions")
    
    thread = threading.Thread(target=cleanup_worker, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Test memory service
    session_id = create_session()
    print(f"Created session: {session_id}")
    
    add_message(session_id, "user", "Xin chào")
    add_message(session_id, "assistant", "Chào bạn!")
    
    print("\nSession history:")
    for msg in get_history(session_id):
        print(f"[{msg['role']}] {msg['content']}")
    
    print(f"\nActive sessions: {get_session_count()}")
    print(f"Total messages: {get_total_messages()}")