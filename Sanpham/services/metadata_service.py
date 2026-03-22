import csv
import os
from config import METADATA_PATH

# LOAD BOOK DATABASE
def load_books():
    """
    Load all books from metadata.csv
    Returns:
        List of book dictionaries
    """
    books = []
    
    if not os.path.exists(METADATA_PATH):
        print(f"⚠️ Metadata file không tìm thấy: {METADATA_PATH}")
        return books
    
    try:
        with open(METADATA_PATH, encoding="utf-8") as f:
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
                # Only add if title exists
                if book["title"]:
                    books.append(book)
        
        print(f"✅ Loaded {len(books)} books from metadata")
        
    except Exception as e:
        print(f"❌ Lỗi khi tải metadata: {e}")
    
    return books

# GET BOOK BY CLASS CODE
def get_book_by_code(class_code):
    """
    Find a book by its class code
    Args:
        class_code: Book class code (e.g., CNTT-001)
    Returns:
        Book dictionary or None if not found
    """
    books = load_books()
    for book in books:
        if book["class_code"].lower() == class_code.lower():
            return book
    return None

# GET BOOKS BY CATEGORY
def get_books_by_category(category):
    """
    Get all books in a specific category
    Args:
        category: Category name
    Returns:
        List of books in that category
    """
    books = load_books()
    category = category.lower()
    return [b for b in books if b["category"].lower() == category]

# GET BOOKS BY AUTHOR
def get_books_by_author(author):
    """
    Get all books by a specific author
    Args:
        author: Author name
    Returns:
        List of books by that author
    """
    books = load_books()
    author = author.lower()
    return [b for b in books if author in b["author"].lower()]

# ADD NEW BOOK
def add_book(book_data):
    """
    Add a new book to metadata.csv
    Args:
        book_data: Dictionary with book info
    Returns:
        (success, message)
    """
    required_fields = ["title", "author", "year", "category", "class_code", "description"]
    
    # Validate required fields
    for field in required_fields:
        if field not in book_data or not str(book_data.get(field, "")).strip():
            return False, f"Missing required field: {field}"
    
    try:
        # Create data directory if not exists
        os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
        
        # Check if file exists to write header
        file_exists = os.path.exists(METADATA_PATH) and os.path.getsize(METADATA_PATH) > 0
        
        with open(METADATA_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow(["title", "author", "year", "category", "class_code", "description"])
            
            writer.writerow([
                book_data["title"].strip(),
                book_data["author"].strip(),
                book_data["year"].strip(),
                book_data["category"].strip(),
                book_data["class_code"].strip(),
                book_data["description"].strip()
            ])
        
        return True, f"Added book: {book_data['title']}"
        
    except Exception as e:
        return False, f"Error adding book: {e}"

# UPDATE BOOK
def update_book(class_code, updated_data):
    """
    Update an existing book
    Args:
        class_code: Class code of book to update
        updated_data: Dictionary with updated fields
    Returns:
        (success, message)
    """
    books = load_books()
    updated = False
    
    for i, book in enumerate(books):
        if book["class_code"].lower() == class_code.lower():
            # Update fields
            for key, value in updated_data.items():
                if key in book and value:
                    books[i][key] = value.strip()
            updated = True
            break
    
    if not updated:
        return False, f"Book with code {class_code} not found"
    
    # Save all books back to file
    try:
        with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "author", "year", "category", "class_code", "description"])
            
            for book in books:
                writer.writerow([
                    book["title"],
                    book["author"],
                    book["year"],
                    book["category"],
                    book["class_code"],
                    book["description"]
                ])
        
        return True, f"Updated book: {class_code}"
        
    except Exception as e:
        return False, f"Error updating book: {e}"


# DELETE BOOK

def delete_book(class_code):
    """
    Delete a book by class code
    Args:
        class_code: Class code of book to delete
    Returns:
        (success, message)
    """
    books = load_books()
    filtered_books = [b for b in books if b["class_code"].lower() != class_code.lower()]
    
    if len(filtered_books) == len(books):
        return False, f"Book with code {class_code} not found"
    
    try:
        with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "author", "year", "category", "class_code", "description"])
            
            for book in filtered_books:
                writer.writerow([
                    book["title"],
                    book["author"],
                    book["year"],
                    book["category"],
                    book["class_code"],
                    book["description"]
                ])
        
        return True, f"Deleted book: {class_code}"
        
    except Exception as e:
        return False, f"Error deleting book: {e}"

# COUNT BY CATEGORY
def count_by_category(books=None):
    """
    Count books by category
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with category counts
    """
    if books is None:
        books = load_books()
    
    result = {}
    for b in books:
        cat = b["category"]
        result[cat] = result.get(cat, 0) + 1
    
    return result

# SEARCH BOOKS
def search_books(keyword, books=None):
    """
    Search books by keyword in title, author, category, description
    Args:
        keyword: Search keyword
        books: List of books (if None, load from file)
    Returns:
        List of matching books
    """
    if books is None:
        books = load_books()
    
    keyword = keyword.lower()
    results = []
    
    for book in books:
        if (keyword in book["title"].lower() or
            keyword in book["author"].lower() or
            keyword in book["category"].lower() or
            keyword in book["description"].lower() or
            keyword in book["class_code"].lower()):
            results.append(book)
    
    return results

# GET STATISTICS
def get_statistics(books=None):
    """
    Get library statistics
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with statistics
    """
    if books is None:
        books = load_books()
    
    stats = {
        "total_books": len(books),
        "categories": {},
        "authors": {},
        "years": {}
    }
    
    for b in books:
        # Count categories
        cat = b["category"]
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        
        # Count authors
        author = b["author"]
        stats["authors"][author] = stats["authors"].get(author, 0) + 1
        
        # Count years
        year = b["year"]
        stats["years"][year] = stats["years"].get(year, 0) + 1
    
    return stats