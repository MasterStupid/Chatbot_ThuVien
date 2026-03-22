from services.metadata_service import load_books, count_by_category
from collections import Counter
import json
from datetime import datetime

# LIBRARY STATISTICS
def library_stats(books=None):
    """
    Get comprehensive library statistics
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with all statistics
    """
    if books is None:
        books = load_books()
    
    if not books:
        return {
            "total_books": 0,
            "categories": {},
            "authors": {},
            "years": {},
            "total_authors": 0,
            "total_categories": 0,
            "oldest_book": None,
            "newest_book": None,
            "most_prolific_author": None,
            "largest_category": None
        }
    
    # Basic counts
    total_books = len(books)
    
    # Category counts
    categories = count_by_category(books)
    total_categories = len(categories)
    
    # Author counts
    authors = {}
    for b in books:
        author = b.get("author", "Unknown")
        authors[author] = authors.get(author, 0) + 1
    total_authors = len(authors)
    
    # Year counts
    years = {}
    valid_years = []
    for b in books:
        year = b.get("year", "Unknown")
        years[year] = years.get(year, 0) + 1
        if year != "Unknown" and year.isdigit():
            valid_years.append(int(year))
    
    # Find oldest and newest books
    oldest_book = None
    newest_book = None
    if valid_years:
        oldest_year = min(valid_years)
        newest_year = max(valid_years)
        
        for b in books:
            if b.get("year") == str(oldest_year):
                oldest_book = b
            if b.get("year") == str(newest_year):
                newest_book = b
    
    # Most prolific author
    most_prolific_author = max(authors.items(), key=lambda x: x[1]) if authors else None
    
    # Largest category
    largest_category = max(categories.items(), key=lambda x: x[1]) if categories else None
    
    # Publication decades
    decades = {}
    for year in valid_years:
        decade = (year // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1
    
    return {
        "total_books": total_books,
        "total_categories": total_categories,
        "total_authors": total_authors,
        "categories": categories,
        "authors": authors,
        "years": years,
        "decades": decades,
        "oldest_book": oldest_book,
        "newest_book": newest_book,
        "most_prolific_author": most_prolific_author,
        "largest_category": largest_category,
        "average_books_per_author": total_books / total_authors if total_authors > 0 else 0,
        "average_books_per_category": total_books / total_categories if total_categories > 0 else 0
    }

# CATEGORY STATISTICS
def category_stats(books=None):
    """
    Get detailed category statistics
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with category statistics
    """
    if books is None:
        books = load_books()
    
    stats = {}
    
    for book in books:
        cat = book["category"]
        
        if cat not in stats:
            stats[cat] = {
                "count": 0,
                "books": [],
                "authors": set(),
                "years": []
            }
        
        stats[cat]["count"] += 1
        stats[cat]["books"].append(book["title"])
        stats[cat]["authors"].add(book["author"])
        
        if book["year"].isdigit():
            stats[cat]["years"].append(int(book["year"]))
    
    # Process each category
    for cat, data in stats.items():
        data["authors"] = list(data["authors"])
        data["unique_authors"] = len(data["authors"])
        data["year_range"] = {
            "min": min(data["years"]) if data["years"] else None,
            "max": max(data["years"]) if data["years"] else None,
            "average": sum(data["years"]) / len(data["years"]) if data["years"] else None
        }
        del data["years"]  # Remove raw years list
    
    return stats

# AUTHOR STATISTICS
def author_stats(books=None):
    """
    Get detailed author statistics
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with author statistics
    """
    if books is None:
        books = load_books()
    
    stats = {}
    
    for book in books:
        author = book["author"]
        
        if author not in stats:
            stats[author] = {
                "count": 0,
                "books": [],
                "categories": set(),
                "years": []
            }
        
        stats[author]["count"] += 1
        stats[author]["books"].append(book["title"])
        stats[author]["categories"].add(book["category"])
        
        if book["year"].isdigit():
            stats[author]["years"].append(int(book["year"]))
    
    # Process each author
    for author, data in stats.items():
        data["categories"] = list(data["categories"])
        data["unique_categories"] = len(data["categories"])
        if data["years"]:
            data["first_book"] = min(data["years"])
            data["last_book"] = max(data["years"])
            data["career_span"] = data["last_book"] - data["first_book"]
        del data["years"]  # Remove raw years list
    
    return stats

# YEARLY STATISTICS
def yearly_stats(books=None):
    """
    Get yearly publication statistics
    Args:
        books: List of books (if None, load from file)
    Returns:
        Dictionary with yearly statistics
    """
    if books is None:
        books = load_books()
    
    years = {}
    
    for book in books:
        year = book["year"]
        if not year.isdigit():
            continue
        
        if year not in years:
            years[year] = {
                "count": 0,
                "categories": set(),
                "authors": set(),
                "books": []
            }
        
        years[year]["count"] += 1
        years[year]["categories"].add(book["category"])
        years[year]["authors"].add(book["author"])
        years[year]["books"].append(book["title"])
    
    # Convert sets to lists
    for year, data in years.items():
        data["categories"] = list(data["categories"])
        data["authors"] = list(data["authors"])
    
    # Sort by year
    return dict(sorted(years.items(), key=lambda x: int(x[0])))

# EXPORT STATS TO JSON
def export_stats_to_json(filepath=None):
    """
    Export all statistics to JSON file
    Args:
        filepath: Path to save JSON file (if None, use timestamp)
    Returns:
        Path to saved file
    """
    books = load_books()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_books": len(books),
        "library_stats": library_stats(books),
        "category_stats": category_stats(books),
        "author_stats": author_stats(books),
        "yearly_stats": yearly_stats(books)
    }
    
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"library_stats_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    return filepath

# PRINT STATS REPORT
def print_stats_report(books=None):
    """
    Print a formatted statistics report
    Args:
        books: List of books (if None, load from file)
    """
    if books is None:
        books = load_books()
    
    stats = library_stats(books)
    
    print("=" * 60)
    print("📊 THƯ VIỆN TRƯỜNG ĐẠI HỌC HẢI PHÒNG - BÁO CÁO THỐNG KÊ")
    print("=" * 60)
    
    print(f"\n📚 Tổng số sách: {stats['total_books']}")
    print(f"👥 Tổng số tác giả: {stats['total_authors']}")
    print(f"🏷️ Tổng số danh mục: {stats['total_categories']}")
    
    print(f"\n📈 Thống kê trung bình: ")
    print(f"   • Số sách/tác giả: {stats['average_books_per_author']:.2f}")
    print(f"   • Số sách/danh mục: {stats['average_books_per_category']:.2f}")
    
    print(f"\n📅 Phân bố theo năm: ")
    for year, count in sorted(stats['years'].items()):
        if year != "Unknown":
            print(f"   • {year}: {count} sách")
    
    print(f"\n📊 Top 5 danh mục lớn nhất: ")
    top_cats = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:5]
    for cat, count in top_cats:
        print(f"   • {cat}: {count} sách")
    
    print(f"\n✍️ Top 5 tác giả có nhiều sách nhất: ")
    top_authors = sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True)[:5]
    for author, count in top_authors:
        print(f"   • {author}: {count} sách")
    
    if stats['oldest_book']:
        print(f"\n📖 Sách cũ nhất: {stats['oldest_book']['title']} ({stats['oldest_book']['year']})")
    
    if stats['newest_book']:
        print(f"📖 Sách mới nhất: {stats['newest_book']['title']} ({stats['newest_book']['year']})")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test statistics
    print_stats_report()