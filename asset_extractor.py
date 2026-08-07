import pymupdf
import os

def extract_visual_assets(pdf_path, output_dir="output_scratch"):
    """
    Finds embedded images/figures inside the PDF, crops them out precisely,
    and saves them as individual PNG image files for the video editor.
    """
    # Create an output folder for our pictures if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = pymupdf.open(pdf_path)
    extracted_count = 0

    print(f"✂️ Cutting out images from {pdf_path}...")

    for page_num, page in enumerate(doc):
        # 1. Get a list of all images embedded on this page
        image_list = page.get_images(full=True)
        
        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            
            # 2. Reconstruct the image parameters from the PDF structure
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # e.g., 'png' or 'jpeg'
            
            # 3. Generate a distinct file name matching the challenge format
            image_name = f"page_{page_num+1}_fig_{img_idx+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)
            
            # 4. Save the raw image bytes to disk
            with open(image_path, "wb") as f:
                f.write(image_bytes)
                
            print(f"   💾 Saved Asset: {image_path}")
            extracted_count += 1

    doc.close()
    print(f"🏁 Finished! Successfully cropped {extracted_count} visual assets.")
    return extracted_count

if __name__ == "__main__":
    target_paper = "datasets/psf2_synth_papers/P01_ionq.pdf"
    extract_visual_assets(target_paper)
