import os
import time
import uuid
from werkzeug.utils import secure_filename
from config import PDF_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from datetime import datetime

# CHECK ALLOWED FILE
def allowed_file(filename):
    """
    Check if file has allowed extension
    Args:
        filename: Name of the file
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# GENERATE UNIQUE FILENAME
def generate_unique_filename(original_filename):
    """
    Generate a unique filename to prevent overwrites
    Args:
        original_filename: Original filename
    Returns:
        Unique filename string
    """
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_name = f"{uuid.uuid4().hex}_{int(time.time())}"
    
    if ext:
        unique_name = f"{unique_name}.{ext}"
    
    return unique_name

# SAVE UPLOADED FILE
def save_uploaded_file(file, keep_original_name=False):
    """
    Save an uploaded file to PDF directory
    Args:
        file: File object from request
        keep_original_name: Whether to keep original filename
    Returns:
        Dictionary with result info
    """
    if not file:
        return {
            "success": False,
            "error": "No file provided"
        }
    
    # Check filename
    if file.filename == '':
        return {
            "success": False,
            "error": "No file selected"
        }
    
    # Check file type
    if not allowed_file(file.filename):
        return {
            "success": False,
            "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        return {
            "success": False,
            "error": f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024*1024)}MB"
        }
    
    # Create PDF directory if not exists
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # Generate filename
    if keep_original_name:
        filename = secure_filename(file.filename)
    else:
        filename = generate_unique_filename(file.filename)
    
    # Ensure unique filename
    filepath = os.path.join(PDF_DIR, filename)
    counter = 1
    while os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{counter}{ext}"
        filepath = os.path.join(PDF_DIR, filename)
        counter += 1
    
    # Save file
    file.save(filepath)
    
    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "size": file_size,
        "size_mb": round(file_size / (1024 * 1024), 2),
        "original_name": file.filename,
        "upload_time": time.time(),
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# SAVE MULTIPLE FILES
def save_multiple_files(files, keep_original_names=False):
    """
    Save multiple uploaded files
    Args:
        files: List of file objects
        keep_original_names: Whether to keep original filenames
    Returns:
        Dictionary with results
    """
    results = {
        "success": [],
        "failed": [],
        "total": len(files),
        "success_count": 0,
        "failed_count": 0
    }
    
    for file in files:
        result = save_uploaded_file(file, keep_original_names)
        if result["success"]:
            results["success"].append(result)
            results["success_count"] += 1
        else:
            results["failed"].append({
                "filename": file.filename if file else "Unknown",
                "error": result["error"]
            })
            results["failed_count"] += 1
    
    # Add summary
    results["total_size_mb"] = sum([f["size_mb"] for f in results["success"]])
    results["average_size_mb"] = results["total_size_mb"] / results["success_count"] if results["success_count"] > 0 else 0
    
    return results

# GET ALL UPLOADED FILES
def get_uploaded_files():
    """
    Get list of all uploaded PDF files with metadata
    Returns:
        List of file info dictionaries
    """
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR, exist_ok=True)
        return []
    
    files = []
    total_size = 0
    
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(PDF_DIR, filename)
            stat = os.stat(filepath)
            size_mb = stat.st_size / (1024 * 1024)
            total_size += size_mb
            
            files.append({
                "filename": filename,
                "path": filepath,
                "size": stat.st_size,
                "size_mb": round(size_mb, 2),
                "modified": stat.st_mtime,
                "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "created": stat.st_ctime,
                "created_date": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sort by modified time (newest first)
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    # Add summary
    summary = {
        "total_files": len(files),
        "total_size_mb": round(total_size, 2),
        "files": files
    }
    
    return summary

# DELETE UPLOADED FILE
def delete_uploaded_file(filename):
    """
    Delete an uploaded PDF file
    Args:
        filename: Name of file to delete
    Returns:
        Boolean indicating success
    """
    if not filename:
        return False
    
    # Secure the filename to prevent path traversal
    filename = secure_filename(filename)
    filepath = os.path.join(PDF_DIR, filename)
    
    if not os.path.exists(filepath):
        return False
    
    try:
        # Get file info before deleting
        file_info = get_file_info(filename)
        
        # Delete the file
        os.remove(filepath)
        
        print(f"✅ Deleted file: {filename} ({file_info['size_mb']}MB)")
        return True
    except Exception as e:
        print(f"❌ Error deleting file {filename}: {e}")
        return False

# DELETE MULTIPLE FILES
def delete_multiple_files(filenames):
    """
    Delete multiple uploaded files
    Args:
        filenames: List of filenames to delete
    Returns:
        Dictionary with results
    """
    results = {
        "success": [],
        "failed": [],
        "total": len(filenames)
    }
    
    for filename in filenames:
        if delete_uploaded_file(filename):
            results["success"].append(filename)
        else:
            results["failed"].append(filename)
    
    results["success_count"] = len(results["success"])
    results["failed_count"] = len(results["failed"])
    
    return results

# GET FILE INFO
def get_file_info(filename):
    """
    Get information about a specific file
    Args:
        filename: Name of the file
    Returns:
        Dictionary with file info or None if not found
    """
    filename = secure_filename(filename)
    filepath = os.path.join(PDF_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    size_mb = stat.st_size / (1024 * 1024)
    
    return {
        "filename": filename,
        "path": filepath,
        "size": stat.st_size,
        "size_mb": round(size_mb, 2),
        "modified": stat.st_mtime,
        "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "created": stat.st_ctime,
        "created_date": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "exists": True
    }

# RENAME FILE
def rename_file(old_filename, new_filename):
    """
    Rename an uploaded file
    Args:
        old_filename: Current filename
        new_filename: New filename
    Returns:
        Boolean indicating success
    """
    old_filename = secure_filename(old_filename)
    new_filename = secure_filename(new_filename)
    
    # Ensure new filename has .pdf extension
    if not new_filename.lower().endswith('.pdf'):
        new_filename += '.pdf'
    
    old_path = os.path.join(PDF_DIR, old_filename)
    new_path = os.path.join(PDF_DIR, new_filename)
    
    if not os.path.exists(old_path):
        return False
    
    if os.path.exists(new_path):
        return False  # New filename already exists
    
    try:
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        print(f"❌ Error renaming file {old_filename}: {e}")
        return False

# CLEANUP OLD FILES
def cleanup_old_files(days=30):
    """
    Delete files older than specified days
    Args:
        days: Maximum age in days
    Returns:
        Number of files deleted
    """
    if not os.path.exists(PDF_DIR):
        return 0
    
    current_time = time.time()
    max_age = days * 24 * 60 * 60  # Convert days to seconds
    
    deleted = 0
    deleted_files = []
    total_size_freed = 0
    
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(PDF_DIR, filename)
            file_age = current_time - os.path.getmtime(filepath)
            file_size = os.path.getsize(filepath)
            
            if file_age > max_age:
                try:
                    # Get file info before deleting
                    file_info = get_file_info(filename)
                    
                    # Delete the file
                    os.remove(filepath)
                    deleted += 1
                    total_size_freed += file_size
                    deleted_files.append({
                        "filename": filename,
                        "age_days": round(file_age / (24 * 60 * 60), 1),
                        "size_mb": round(file_size / (1024 * 1024), 2)
                    })
                    print(f"🧹 Deleted old file: {filename} ({(file_age / (24*60*60)):.1f} days old)")
                except Exception as e:
                    print(f"❌ Error deleting {filename}: {e}")
    
    return {
        "deleted_count": deleted,
        "deleted_files": deleted_files,
        "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
        "days_threshold": days
    }

# GET STORAGE STATISTICS
def get_storage_stats():
    """
    Get storage statistics for PDF directory
    Returns:
        Dictionary with storage statistics
    """
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR, exist_ok=True)
        return {
            "total_files": 0,
            "total_size_mb": 0,
            "average_size_mb": 0,
            "largest_file": None,
            "smallest_file": None,
            "oldest_file": None,
            "newest_file": None,
            "by_year": {},
            "by_month": {}
        }
    
    files = []
    total_size = 0
    
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith('.pdf'):
            filepath = os.path.join(PDF_DIR, filename)
            stat = os.stat(filepath)
            size_mb = stat.st_size / (1024 * 1024)
            total_size += size_mb
            
            files.append({
                "filename": filename,
                "size_mb": size_mb,
                "modified": stat.st_mtime,
                "modified_date": datetime.fromtimestamp(stat.st_mtime)
            })
    
    if not files:
        return {
            "total_files": 0,
            "total_size_mb": 0,
            "average_size_mb": 0,
            "largest_file": None,
            "smallest_file": None,
            "oldest_file": None,
            "newest_file": None,
            "by_year": {},
            "by_month": {}
        }
    
    # Calculate statistics
    files.sort(key=lambda x: x["size_mb"])
    smallest = files[0]
    largest = files[-1]
    
    files.sort(key=lambda x: x["modified"])
    oldest = files[0]
    newest = files[-1]
    
    # Group by year and month
    by_year = {}
    by_month = {}
    
    for f in files:
        year = f["modified_date"].year
        month = f["modified_date"].strftime("%Y-%m")
        
        by_year[year] = by_year.get(year, 0) + 1
        by_month[month] = by_month.get(month, 0) + 1
    
    return {
        "total_files": len(files),
        "total_size_mb": round(total_size, 2),
        "average_size_mb": round(total_size / len(files), 2),
        "largest_file": {
            "filename": largest["filename"],
            "size_mb": round(largest["size_mb"], 2)
        },
        "smallest_file": {
            "filename": smallest["filename"],
            "size_mb": round(smallest["size_mb"], 2)
        },
        "oldest_file": {
            "filename": oldest["filename"],
            "date": oldest["modified_date"].strftime("%Y-%m-%d")
        },
        "newest_file": {
            "filename": newest["filename"],
            "date": newest["modified_date"].strftime("%Y-%m-%d")
        },
        "by_year": {str(k): v for k, v in sorted(by_year.items())},
        "by_month": dict(sorted(by_month.items())),
        "directory": PDF_DIR,
        "free_space_mb": get_free_space_mb()
    }

# GET FREE SPACE
def get_free_space_mb():
    """
    Get free disk space in MB
    Returns:
        Free space in MB or None if not available
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(PDF_DIR), None, None, ctypes.pointer(free_bytes)
            )
            return round(free_bytes.value / (1024 * 1024), 2)
        else:  # Unix/Linux/Mac
            stat = os.statvfs(PDF_DIR)
            free_bytes = stat.f_frsize * stat.f_bavail
            return round(free_bytes / (1024 * 1024), 2)
    except Exception as e:
        print(f"⚠️ Could not get free space: {e}")
        return None

# VALIDATE FILE INTEGRITY
def validate_pdf_integrity(filename):
    """
    Validate that a file is a valid PDF
    Args:
        filename: Name of the file to validate
    Returns:
        Boolean indicating if file is valid PDF
    """
    filename = secure_filename(filename)
    filepath = os.path.join(PDF_DIR, filename)
    
    if not os.path.exists(filepath):
        return False
    
    try:
        # Check PDF header
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False
        
        # Try to open with PyPDF2 (optional, requires PyPDF2)
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                PyPDF2.PdfReader(f)
            return True
        except ImportError:
            # If PyPDF2 not available, just check header
            return True
        except Exception:
            return False
            
    except Exception as e:
        print(f"❌ Error validating {filename}: {e}")
        return False

# GET FILE PREVIEW
def get_file_preview(filename, max_length=500):
    """
    Get a preview of file content (first few characters)
    Args:
        filename: Name of the file
        max_length: Maximum preview length
    Returns:
        Preview string or None if not available
    """
    filename = secure_filename(filename)
    filepath = os.path.join(PDF_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        # Try to extract text from PDF
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                if len(pdf.pages) > 0:
                    text = pdf.pages[0].extract_text()
                    if text:
                        return text[:max_length] + ('...' if len(text) > max_length else '')
        except ImportError:
            pass
        
        # Fallback: just return filename and size
        size = os.path.getsize(filepath)
        return f"PDF File: {filename} ({size} bytes)"
        
    except Exception as e:
        return f"Could not preview file: {e}"

# TEST FUNCTION
def test_upload_service():
    """
    Test the upload service functionality
    """
    print("=" * 60)
    print("📁 UPLOAD SERVICE TEST")
    print("=" * 60)
    
    # Test allowed file check
    print("\n🔍 Testing allowed_file():")
    test_files = ['test.pdf', 'test.txt', 'test.PDF', 'test.exe', 'no_extension']
    for f in test_files:
        result = allowed_file(f)
        print(f"  • {f}: {'✅' if result else '❌'}")
    
    # Test unique filename generation
    print("\n🔍 Testing generate_unique_filename():")
    test_names = ['document.pdf', 'file.PDF', 'no_extension']
    for name in test_names:
        unique = generate_unique_filename(name)
        print(f"  • {name} → {unique}")
    
    # Test storage stats
    print("\n🔍 Testing get_storage_stats():")
    stats = get_storage_stats()
    print(f"  • Total files: {stats['total_files']}")
    print(f"  • Total size: {stats['total_size_mb']} MB")
    if stats['largest_file']:
        print(f"  • Largest: {stats['largest_file']['filename']} ({stats['largest_file']['size_mb']} MB)")
    if stats['free_space_mb']:
        print(f"  • Free space: {stats['free_space_mb']} MB")
    
    print("\n" + "=" * 60)
    print("✅ Test complete")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_service()