from services.metadata_service import load_books, get_statistics
from services.stats_service import library_stats, category_stats, author_stats
from datetime import datetime
import os

# BUILD BASIC REPORT
def build_basic_report(books=None):
    """
    Build a basic text report of all books
    Args:
        books: List of books (if None, load from file)
    Returns:
        Report string
    """
    if books is None:
        books = load_books()
    
    report = []
    report.append("=" * 80)
    report.append("📚 THƯ VIỆN ĐẠI HỌC HẢI PHÒNG - DANH MỤC SÁCH")
    report.append(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    if not books:
        report.append("❌ Không có dữ liệu sách trong thư viện.")
        return "\n".join(report)
    
    # Group by category
    categories = {}
    for book in books:
        cat = book["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(book)
    
    # Print each category
    for category, cat_books in sorted(categories.items()):
        report.append(f"\n📖 DANH MỤC: {category.upper()} ({len(cat_books)} sách)")
        report.append("-" * 60)
        
        for book in sorted(cat_books, key=lambda x: x["title"]):
            report.append(f"  • {book['title']}")
            report.append(f"    Mã: {book['class_code']} | Tác giả: {book['author']} | Năm: {book['year']}")
            if book.get('description'):
                report.append(f"    Mô tả: {book['description'][:100]}{'...' if len(book['description']) > 100 else ''}")
            report.append("")
    
    report.append("=" * 80)
    report.append(f"Tổng số sách: {len(books)}")
    report.append("=" * 80)
    
    return "\n".join(report)

# BUILD STATISTICS REPORT
def build_stats_report(books=None):
    """
    Build a detailed statistics report
    Args:
        books: List of books (if None, load from file)
    Returns:
        Report string
    """
    if books is None:
        books = load_books()
    
    stats = library_stats(books)
    
    report = []
    report.append("=" * 80)
    report.append("📊 THƯ VIỆN ĐẠI HỌC HẢI PHÒNG - BÁO CÁO THỐNG KÊ")
    report.append(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    # Tổng quan
    report.append("📈 TỔNG QUAN:")
    report.append(f"  • Tổng số sách: {stats['total_books']}")
    report.append(f"  • Tổng số tác giả: {stats['total_authors']}")
    report.append(f"  • Tổng số danh mục: {stats['total_categories']}")
    report.append(f"  • Trung bình sách/tác giả: {stats['average_books_per_author']:.2f}")
    report.append(f"  • Trung bình sách/danh mục: {stats['average_books_per_category']:.2f}")
    report.append("")
    
    # Theo danh mục
    report.append("🏷️ THỐNG KÊ THEO DANH MỤC: ")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
        report.append(f"  • {cat}: {count} sách")
    report.append("")
    
    # Theo tác giả
    report.append("✍️ THỐNG KÊ THEO TÁC GIẢ: ")
    top_authors = sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True)[:10]
    for author, count in top_authors:
        report.append(f"  • {author}: {count} sách")
    report.append("")
    
    # Theo năm
    report.append("📅 THỐNG KÊ THEO NĂM: ")
    for year, count in sorted(stats['years'].items()):
        if year != "Unknown":
            report.append(f"  • {year}: {count} sách")
    report.append("")
    
    # Sách cũ nhất và mới nhất
    if stats['oldest_book']:
        report.append(f"📖 Sách cũ nhất: {stats['oldest_book']['title']} ({stats['oldest_book']['year']})")
    if stats['newest_book']:
        report.append(f"📖 Sách mới nhất: {stats['newest_book']['title']} ({stats['newest_book']['year']})")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

# BUILD CATEGORY REPORT
def build_category_report(category_name, books=None):
    """
    Build a report for a specific category
    Args:
        category_name: Name of the category
        books: List of books (if None, load from file)
    Returns:
        Report string
    """
    if books is None:
        books = load_books()
    
    category_books = [b for b in books if b["category"].lower() == category_name.lower()]
    
    report = []
    report.append("=" * 80)
    report.append(f"📖 DANH MỤC: {category_name.upper()}")
    report.append(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    if not category_books:
        report.append(f"❌ Không có sách trong danh mục '{category_name}'")
        return "\n".join(report)
    
    report.append(f"📚 Tổng số sách: {len(category_books)}")
    report.append("")
    
    # Group by author
    by_author = {}
    for book in category_books:
        author = book["author"]
        if author not in by_author:
            by_author[author] = []
        by_author[author].append(book)
    
    for author, author_books in sorted(by_author.items()):
        report.append(f"✍️ Tác giả: {author} ({len(author_books)} sách)")
        for book in sorted(author_books, key=lambda x: x["title"]):
            report.append(f"  • {book['title']} - {book['year']} (Mã: {book['class_code']})")
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

# BUILD AUTHOR REPORT
def build_author_report(author_name, books=None):
    """
    Build a report for a specific author
    Args:
        author_name: Name of the author
        books: List of books (if None, load from file)
    Returns:
        Report string
    """
    if books is None:
        books = load_books()
    
    author_books = [b for b in books if author_name.lower() in b["author"].lower()]
    
    report = []
    report.append("=" * 80)
    report.append(f"✍️ TÁC GIẢ: {author_name}")
    report.append(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    if not author_books:
        report.append(f"❌ Không tìm thấy sách của tác giả '{author_name}'")
        return "\n".join(report)
    
    report.append(f"📚 Tổng số sách: {len(author_books)}")
    report.append("")
    
    # Group by category
    by_category = {}
    for book in author_books:
        cat = book["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(book)
    
    for category, cat_books in sorted(by_category.items()):
        report.append(f"🏷️ Danh mục: {category} ({len(cat_books)} sách)")
        for book in sorted(cat_books, key=lambda x: x["year"]):
            report.append(f"  • {book['title']} - {book['year']} (Mã: {book['class_code']})")
        report.append("")
    
    # Publication years
    years = [int(b["year"]) for b in author_books if b["year"].isdigit()]
    if years:
        report.append(f"📅 Năm xuất bản: {min(years)} - {max(years)}")
    
    report.append("=" * 80)
    
    return "\n".join(report)

# EXPORT REPORT TO FILE
def export_report_to_file(report_content, filename=None):
    """
    Export report to a text file
    Args:
        report_content: Report string
        filename: Output filename (if None, generate from timestamp)
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"library_report_{timestamp}.txt"
    
    # Create reports directory if not exists
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    filepath = os.path.join(reports_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"✅ Report saved to: {filepath}")
    return filepath

# GENERATE COMPLETE REPORT
def generate_complete_report(export=True):
    """
    Generate a complete library report
    Args:
        export: Whether to export to file
    Returns:
        Report string and file path (if exported)
    """
    books = load_books()
    
    report = []
    report.append(build_basic_report(books))
    report.append("\n\n")
    report.append(build_stats_report(books))
    
    complete_report = "\n".join(report)
    
    if export:
        filepath = export_report_to_file(complete_report)
        return complete_report, filepath
    
    return complete_report, None

if __name__ == "__main__":
    # Test report service
    print("📄 Report Service Test")
    print("=" * 50)
    
    report, filepath = generate_complete_report(export=True)
    print(f"\nReport generated: {filepath}")
    print("\nFirst 500 characters:")
    print("-" * 50)
    print(report[:500])