import os
import PyPDF2
from config import PDF_DIR
import re

# READ PDF TEXT
def read_pdf_text(pdf_path):
    """
    Extract text from a PDF file
    Args:
        pdf_path: Path to PDF file
    Returns:
        Extracted text string
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return ""
    
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get number of pages
            num_pages = len(pdf_reader.pages)
            print(f"📄 Reading PDF: {os.path.basename(pdf_path)} ({num_pages} pages)")
            
            # Extract text from each page
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
        
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
        return ""

def get_all_pdfs():
    """
    Get list of all PDF files in PDF directory
    Returns:
        List of PDF filenames
    """
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR, exist_ok=True)
        return []
    
    pdfs = []
    for file in os.listdir(PDF_DIR):
        if file.lower().endswith('.pdf'):
            pdfs.append(file)
    
    return sorted(pdfs)

def extract_pdf_metadata(pdf_path):
    """
    Extract metadata from PDF file
    Args:
        pdf_path: Path to PDF file
    Returns:
        Dictionary with metadata
    """
    if not os.path.exists(pdf_path):
        return {}
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            metadata = {
                "filename": os.path.basename(pdf_path),
                "num_pages": len(pdf_reader.pages),
                "pdf_version": pdf_reader.pdf_header if hasattr(pdf_reader, 'pdf_header') else "Unknown"
            }
            
            # Extract document info
            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    # Clean up key name
                    clean_key = key.replace('/', '').lower()
                    metadata[clean_key] = str(value)
            
            return metadata
            
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất metadata từ {pdf_path}: {e}")
        return {"filename": os.path.basename(pdf_path), "error": str(e)}

# SPLIT TEXT INTO CHUNKS
def split_into_chunks(text, chunk_size=1000, overlap=200):
    """
    Split long text into overlapping chunks
    Args:
        text: Input text
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Find end of chunk
        end = min(start + chunk_size, text_length)
        
        # Try to end at a sentence or paragraph
        if end < text_length:
            # Look for paragraph break
            paragraph_end = text.rfind('\n\n', start, end)
            if paragraph_end != -1 and paragraph_end > start + chunk_size // 2:
                end = paragraph_end + 2
            else:
                # Look for sentence end
                sentence_end = text.rfind('. ', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 2
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
    
    return chunks

# PROCESS PDF FOR VECTOR STORAGE
def process_pdf_for_vectors(pdf_path, chunk_size=1000, overlap=200):
    """
    Process a PDF file for vector storage
    Args:
        pdf_path: Path to PDF file
        chunk_size: Size of text chunks
        overlap: Overlap between chunks
    Returns:
        Dictionary with processing results
    """
    print(f"🔄 Processing PDF: {pdf_path}")
    
    # Extract text
    text = read_pdf_text(pdf_path)
    if not text:
        return {
            "success": False,
            "error": "No text extracted",
            "filename": os.path.basename(pdf_path)
        }
    
    # Split into chunks
    chunks = split_into_chunks(text, chunk_size, overlap)
    
    # Extract metadata
    metadata = extract_pdf_metadata(pdf_path)
    
    result = {
        "success": True,
        "filename": os.path.basename(pdf_path),
        "num_chunks": len(chunks),
        "total_chars": len(text),
        "metadata": metadata,
        "chunks": chunks
    }
    
    print(f"✅ Processed {result['filename']}: {result['num_chunks']} chunks, {result['total_chars']} chars")
    
    return result

def batch_process_pdfs():
    """
    Process all PDFs in the PDF directory
    Returns:
        List of processing results
    """
    pdfs = get_all_pdfs()
    results = []
    
    for pdf in pdfs:
        pdf_path = os.path.join(PDF_DIR, pdf)
        result = process_pdf_for_vectors(pdf_path)
        results.append(result)
    
    return results

# SEARCH IN PDFS
def search_in_pdfs(keyword, case_sensitive=False):
    """
    Search for keyword in all PDFs
    Args:
        keyword: Search keyword
        case_sensitive: Whether search is case sensitive
    Returns:
        List of results with filename and context
    """
    pdfs = get_all_pdfs()
    results = []
    
    keyword = keyword if case_sensitive else keyword.lower()
    
    for pdf in pdfs:
        pdf_path = os.path.join(PDF_DIR, pdf)
        text = read_pdf_text(pdf_path)
        
        if not text:
            continue
        
        search_text = text if case_sensitive else text.lower()
        
        if keyword in search_text:
            # Find context around keyword
            index = search_text.find(keyword)
            start = max(0, index - 100)
            end = min(len(text), index + len(keyword) + 100)
            context = text[start:end]
            
            results.append({
                "filename": pdf,
                "context": context,
                "position": index
            })
    
    return results

if __name__ == "__main__":
    # Test PDF service
    print("📚 PDF Service Test")
    print("=" * 50)
    
    pdfs = get_all_pdfs()
    print(f"Found {len(pdfs)} PDFs")
    
    if pdfs:
        test_pdf = pdfs[0]
        print(f"\nTesting with: {test_pdf}")
        
        result = process_pdf_for_vectors(os.path.join(PDF_DIR, test_pdf))
        print(f"Result: {result['num_chunks']} chunks")