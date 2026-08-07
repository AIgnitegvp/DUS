import pymupdf  # Using clean, modern API calls

def parse_reading_order(pdf_path):
    """
    Parses a two-column academic PDF page layout and reorganizes 
    text blocks from top-to-bottom, column-by-column.
    """
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    ordered_document_data = []

    for page_num, page in enumerate(doc):
        # Extract text blocks with geometric coordinates
        # Block tuple format: (x0, y0, x1, y1, "text string", block_no, block_type)
        raw_blocks = page.get_text("blocks")
        
        page_width = page.rect.width
        mid_point = page_width / 2

        left_column = []
        right_column = []
        full_width_blocks = []

        for block in raw_blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            clean_text = text.strip()
            
            if not clean_text:
                continue

            # Classify positioning based on the center vertical gutter
            # Allows a tiny 10-pixel buffer margin for indented text blocks
            if x1 <= mid_point + 10:
                left_column.append(block)
            elif x0 >= mid_point - 10:
                right_column.append(block)
            else:
                # Spans across the entire layout width (Titles, Abstracts, full-width charts)
                full_width_blocks.append(block)

        # Sort each column individually from top to bottom based on y0
        left_column.sort(key=lambda b: b[1])
        right_column.sort(key=lambda b: b[1])
        full_width_blocks.sort(key=lambda b: b[1])

        # Interleave elements structurally to mirror correct human reading order
        page_ordered_text = []
        
        # 1. Process header elements (like Titles) resting at the top 25% of the page
        for block in full_width_blocks:
            if block[1] < (page.rect.height * 0.25):
                page_ordered_text.append(block)

        # 2. Append all sorted text from the left column
        for block in left_column:
            page_ordered_text.append(block)
            
        # 3. Append all sorted text from the right column
        for block in right_column:
            page_ordered_text.append(block)

        # 4. Process layout elements resting at the absolute bottom (Footnotes, References)
        for block in full_width_blocks:
            if block[1] >= (page.rect.height * 0.25):
                page_ordered_text.append(block)

        ordered_document_data.append({
            "page": page_num + 1,
            "blocks": page_ordered_text
        })

    doc.close()
    return ordered_document_data

if __name__ == "__main__":
    # Test layout segmentation directly against the verified paper
    target_paper = "datasets/psf2_synth_papers/P01_ionq.pdf"
    
    print(f"📖 Restructuring reading order layout for: {target_paper}...")
    structured_layout = parse_reading_order(target_paper)
    
    if structured_layout:
        print("\n--- EXTRACTED LAYOUT TRACKING (PAGE 1) ---")
        # Grab first page block list safely
        first_page_blocks = structured_layout[0]["blocks"]
        
        # Print out the text content of the first three sorted blocks
        for i, block in enumerate(first_page_blocks[:3]):
            x0, y0, x1, y1, text, b_no, b_type = block
            print(f"\n[Structural Block #{i+1}] (Coords: x0={x0:.1f}, y0={y0:.1f}):")
            print(text.strip())
            print("-" * 50)
