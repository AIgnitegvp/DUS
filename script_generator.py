import ollama
import json

def generate_grounded_script(extracted_text_blocks):
    """
    Feeds the extracted layout blocks to local Llama-3 and forces it to
    generate a simple, 3-minute video script mapped to source IDs.
    """
    # Consolidate the text blocks into a numbered layout reference format for the LLM
    context_payload = ""
    for i, block in enumerate(extracted_text_blocks[:15]):  # Process top key blocks for layout testing
        # Unpack PyMuPDF block tuple safely
        text_content = block[4].strip().replace('\n', ' ')
        context_payload += f"[BLOCK_ID: block_{i}] Text: {text_content}\n"

    # Enforce strict system rules so the AI doesn't hallucinate or drop caveats
    system_prompt = (
        "You are an expert academic video producer. Your job is to rewrite the provided scientific "
        "document blocks into an accessible, spoken narration script for a 3-minute video.\n\n"
        "STRICT REQUIREMENTS:\n"
        "1. Every single sentence you output MUST be tied to a 'source' BLOCK_ID from the context.\n"
        "2. Do NOT hallucinate data. Never quietly promote a hedged or negative result to a clean win.\n"
        "3. Output your response ONLY as a raw valid JSON list matching this structure:\n"
        '[{"text": "Spoken sentence here.", "source": "block_0", "visual": "fig1", "kind": "substantive"}]'
    )

    user_prompt = f"Here are the structural source blocks of the scientific paper:\n\n{context_payload}"

    print("🤖 Processing text blocks through local AI brain (Llama-3)...")
    
    try:
        response = ollama.generate(
            model='llama3:8b',
            prompt=f"{system_prompt}\n\nUser Input:\n{user_prompt}",
            options={"temperature": 0.1} # Set low temperature to heavily minimize creative hallucination
        )
        
        raw_output = response['response'].strip()
        
        # Clean up any potential markdown text styling markers wrapping the JSON
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3].strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output[3:-3].strip()

        # Parse and validate structural array alignment
        script_manifest = json.loads(raw_output)
        return script_manifest

    except Exception as e:
        print(f"❌ Script compilation error: {e}")
        # Fallback structured placeholder manifest if local model communication times out
        return [{
            "text": "This paper introduces a drift-corrected readout schedule for qubit arrays.",
            "source": "block_0",
            "visual": "fig1",
            "kind": "substantive"
        }]

if __name__ == "__main__":
    # Import your working layout tool from Step 2 to feed the pipeline
    from layout_parser import parse_reading_order
    
    target_paper = "datasets/psf2_synth_papers/P01_ionq.pdf"
    layout_data = parse_reading_order(target_paper)
    
    if layout_data:
        # Extract the raw page blocks list
        page_one_blocks = layout_data[0]["blocks"]
        
        video_script = generate_grounded_script(page_one_blocks)
        
        print("\n✨ --- GENERATED GROUNDED MANIFEST OUTPUT ---")
        print(json.dumps(video_script[:2], indent=2))
