import pymupdf  # Upgraded to remove the fitz warning
import re

def check_pdf_health(pdf_path):
    """
    Evaluates a PDF to determine if it is readable.
    Catches P06 (scanned image) and P07 (corrupted mojibake text mapping).
    """
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        return False, f"Decline: Corrupted PDF file structure. Error: {str(e)}"

    total_text = ""
    for page in doc:
        total_text += page.get_text()
    doc.close()

    # 1. Catch Missing Text Layer (Catches P06)
    if not total_text.strip():
        return False, "Decline: Scanned image-only PDF detected. No structural text layer found."

    # 2. Catch Garbled Font Maps / Gibberish (Catches P07 Trap)
    # A list of common structural academic terms that MUST appear in a valid research paper
    academic_dictionary = ["abstract", "introduction", "results", "discussion", "references", "figure", "table", "the", "and", "with"]
    
    # Convert text to lowercase and find all valid lowercase alphabet words
    clean_words = re.findall(r'\b[a-z]{3,15}\b', total_text.lower())
    
    if not clean_words:
        return False, "Decline: Corrupted text extraction. No readable alphabetic words found."

    # Count how many common structural dictionary words are present in the text
    dictionary_matches = sum(1 for word in clean_words if word in academic_dictionary)
    
    # Calculate a matching score. Valid papers will match hundreds of times.
    # Corrupted Mojibake papers will score 0 or near 0 because their letters are scrambled.
    if dictionary_matches < 5:
        return False, f"Decline: Corrupted font map / Mojibake detected. Text is unreadable gibberish (matched {dictionary_matches} structural words)."

    return True, "Valid: PDF contains a healthy, readable text layer. Ready for layout parsing."

if __name__ == "__main__":
    test_files = [
        "datasets/psf2_synth_papers/P01_ionq.pdf",
        "datasets/psf2_synth_papers/P06_scanned_unreadable.pdf",
        "datasets/psf2_synth_papers/P07_mojibake_unreadable.pdf"
    ]
    
    print("--- Running Trust Gate Validation ---")
    for file_path in test_files:
        readable, reason = check_pdf_health(file_path)
        print(f"\n📄 File: {file_path}")
        print(f"✅ Status: {'PASSED' if readable else 'REJECTED'}")
        print(f"💬 Reason: {reason}")
