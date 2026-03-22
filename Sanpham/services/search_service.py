# SMART SEARCH ENGINE
def search_books(query, books):
    """
    Search books with smart matching
    Args:
        query: Search query string
        books: List of book dictionaries
    Returns:
        List of matching books (sorted by relevance)
    """
    if not books:
        return []
    
    query = query.lower().strip()
    if not query:
        return []
    
    results = []
    search_terms = query.split()
    
    for book in books:
        score = 0
        title = book["title"].lower()
        category = book["category"].lower()
        code = book["class_code"].lower()
        author = book["author"].lower()
        description = book["description"].lower()
        
        # Exact match in title (highest score)
        if query == title:
            score += 100
        elif query in title:
            score += 50
        
        # Exact match in class code
        if query == code:
            score += 80
        elif query in code:
            score += 40
        
        # Match in author
        if query == author:
            score += 60
        elif query in author:
            score += 30
        
        # Match in category
        if query == category:
            score += 40
        elif query in category:
            score += 20
        
        # Match in description
        if query in description:
            score += 10
        
        # Partial matches for multi-word queries
        for term in search_terms:
            if len(term) > 2:
                if term in title:
                    score += 15
                if term in category:
                    score += 10
                if term in code:
                    score += 8
                if term in author:
                    score += 12
                if term in description:
                    score += 5
        
        if score > 0:
            results.append((score, book))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return only books (without scores)
    return [r[1] for r in results]

# SEARCH BY CATEGORY
def search_by_category(category_name, books):
    """
    Search books by category
    Args:
        category_name: Category name to search for
        books: List of book dictionaries
    Returns:
        List of books in matching categories
    """
    if not books:
        return []
    
    category_name = category_name.lower().strip()
    if not category_name:
        return []
    
    results = []
    
    for book in books:
        book_cat = book["category"].lower()
        if category_name in book_cat or book_cat in category_name:
            results.append(book)
    
    return results

# SEARCH BY TITLE
def search_by_title(keyword, books):
    """
    Search books by title
    Args:
        keyword: Title keyword to search for
        books: List of book dictionaries
    Returns:
        List of books with matching titles
    """
    if not books:
        return []
    
    keyword = keyword.lower().strip()
    if not keyword:
        return []
    
    results = []
    keywords = keyword.split()
    
    for book in books:
        title = book["title"].lower()
        
        # Check for exact match
        if keyword == title:
            results.insert(0, book)  # Put exact matches first
            continue
        
        # Check for partial match
        if keyword in title:
            results.append(book)
            continue
        
        # Check for word matches
        for word in keywords:
            if len(word) > 2 and word in title:
                results.append(book)
                break
    
    return results

# SEARCH BY AUTHOR
def search_by_author(author_name, books):
    """
    Search books by author
    Args:
        author_name: Author name to search for
        books: List of book dictionaries
    Returns:
        List of books by matching authors
    """
    if not books:
        return []
    
    author_name = author_name.lower().strip()
    if not author_name:
        return []
    
    results = []
    
    for book in books:
        author = book["author"].lower()
        if author_name in author or author in author_name:
            results.append(book)
    
    return results

# SEARCH BY YEAR
def search_by_year(year, books):
    """
    Search books by publication year
    Args:
        year: Year to search for
        books: List of book dictionaries
    Returns:
        List of books published in that year
    """
    if not books:
        return []
    
    year = str(year).strip()
    
    results = []
    for book in books:
        if book["year"] == year:
            results.append(book)
    
    return results

# ADVANCED SEARCH
def advanced_search(filters, books):
    """
    Advanced search with multiple filters
    Args:
        filters: Dictionary with search filters
            e.g., {"title": "python", "author": "nguyen", "year": "2020"}
        books: List of book dictionaries
    Returns:
        List of books matching all filters
    """
    if not books:
        return []
    
    results = books.copy()
    
    # Apply title filter
    if "title" in filters and filters["title"]:
        title_keyword = filters["title"].lower()
        results = [b for b in results if title_keyword in b["title"].lower()]
    
    # Apply author filter
    if "author" in filters and filters["author"]:
        author_keyword = filters["author"].lower()
        results = [b for b in results if author_keyword in b["author"].lower()]
    
    # Apply category filter
    if "category" in filters and filters["category"]:
        cat_keyword = filters["category"].lower()
        results = [b for b in results if cat_keyword in b["category"].lower()]
    
    # Apply year filter
    if "year" in filters and filters["year"]:
        year = str(filters["year"])
        results = [b for b in results if b["year"] == year]
    
    # Apply code filter
    if "class_code" in filters and filters["class_code"]:
        code = filters["class_code"].lower()
        results = [b for b in results if code in b["class_code"].lower()]
    
    return results

# GET SUGGESTIONS
def get_suggestions(query, books, max_suggestions=5):
    """
    Get search suggestions based on partial query
    Args:
        query: Partial search query
        books: List of book dictionaries
        max_suggestions: Maximum number of suggestions
    Returns:
        List of suggestion strings
    """
    if not books or not query:
        return []
    
    query = query.lower()
    suggestions = set()
    
    for book in books:
        # Suggest titles
        if query in book["title"].lower():
            suggestions.add(book["title"])
        
        # Suggest authors
        if query in book["author"].lower():
            suggestions.add(book["author"])
        
        # Suggest categories
        if query in book["category"].lower():
            suggestions.add(book["category"])
        
        if len(suggestions) >= max_suggestions:
            break
    
    return list(suggestions)[:max_suggestions]