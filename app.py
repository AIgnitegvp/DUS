import streamlit as st
import os
import time
from trust_gate import check_pdf_health
from layout_parser import parse_reading_order
from asset_extractor import extract_visual_assets
from script_generator import generate_grounded_script
from audio_engine import generate_voice_and_timestamps
from video_compiler import compile_final_video

# UI Page Canvas Setup Configurations
st.set_page_config(page_title="PS-F2 Cinema Room", page_icon="🎬", layout="centered")

SCRATCH_DIR = "output_scratch"
if not os.path.exists(SCRATCH_DIR):
    os.makedirs(SCRATCH_DIR)

# Track configuration state in local session cache memory
if "current_page" not in st.session_state:
    st.session_state.current_page = "upload_page"

def switch_to_theater():
    st.session_state.current_page = "theater_page"

def switch_to_upload():
    st.session_state.current_page = "upload_page"

# ==============================================================================
# 🚪 PAGE 1: THE INPUT GATEWAY
# ==============================================================================
if st.session_state.current_page == "upload_page":
    st.title("🎬 PS-F2: Automatic Paper-to-Video Engine")
    st.markdown("Convert complex academic research papers into narrated explainer videos instantly.")
    st.write("---")
    
    uploaded_file = st.file_uploader("Upload your Research Paper PDF", type=["pdf"])
    
    if uploaded_file:
        saved_pdf_path = os.path.join(SCRATCH_DIR, uploaded_file.name)
        with open(saved_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.success(f"📄 Successfully staged: {uploaded_file.name}")
        st.write("")
        
        if st.button("🚀 GET VIDEO", use_container_width=True, key="get_video_btn"):
            
            # Open operational visual modal progress tracking area
            with st.status("⚙️ Processing multimedia layers...", expanded=True) as status:
                
                # Step 1: Health Inspection Filter
                status.update(label="🛡️ Running Gate Validation...")
                is_healthy, reason = check_pdf_health(saved_pdf_path)
                if not is_healthy:
                    st.error(f"❌ Document Blocked! {reason}")
                    status.update(label="Validation Failed", state="error")
                    st.stop()
                
                # Step 2 & 3: Structural Reading Re-ordering
                status.update(label="📐 Segmenting Columns & Extracting Graphics...")
                layout_profile = parse_reading_order(saved_pdf_path)
                extract_visual_assets(saved_pdf_path, SCRATCH_DIR)
                
                # Step 4: FIXED INDENTATION & ADAPTIVE DATA LINK LAYOUT BLOCK
                status.update(label="🤖 Generating Grounded Script via Local AI...")
                
                page_blocks = []
                if isinstance(layout_profile, list):
                    # Unpack elements dynamically if it is a list of dictionary segments
                    for item in layout_profile:
                        if isinstance(item, dict):
                            raw_blocks = item.get("blocks", [])
                            for b in raw_blocks:
                                if isinstance(b, tuple) and len(b) >= 5:
                                    page_blocks.append(str(b[4]))
                                else:
                                    page_blocks.append(str(b))
                        else:
                            page_blocks.append(str(item))
                elif isinstance(layout_profile, dict):
                    raw_blocks = layout_profile.get("blocks", [])
                    for b in raw_blocks:
                        if isinstance(b, tuple) and len(b) >= 5:
                            page_blocks.append(str(b[4]))
                        else:
                            page_blocks.append(str(b))
                else:
                    page_blocks = [str(layout_profile)]

                # Pass the completely clean text string list directly into your Ollama engine
                generated_script = generate_grounded_script(page_blocks)
                st.write("📊 Grounded manifest data array populated successfully.")
                
                # Step 5: Audio Recording Studio
                status.update(label="🎙️ Recording Voice Narration Tracks...")
                generate_voice_and_timestamps(generated_script, SCRATCH_DIR)
                
                # Step 6: Multi-Media Movie Assembly Suite
                status.update(label="🎬 Compiling Final MP4 Movie Master File...")
                output_movie_path = os.path.join(SCRATCH_DIR, "final_explainer.mp4")
                compile_final_video(
                    manifest_path=os.path.join(SCRATCH_DIR, "video_manifest.json"),
                    output_video_path=output_movie_path
                )
                
                status.update(label="🏁 Final Assembly Complete!", state="complete")
                time.sleep(1.0)
            
            # Route viewport to cinema viewer layout tab
            switch_to_theater()
            st.rerun()

# ==============================================================================
# 📺 PAGE 2: THE THEATER (CLEANED & MOVIE CONTEXT LOCK)
# ==============================================================================
elif st.session_state.current_page == "theater_page":
    st.title("📺 PS-F2 Screening Theater")
    st.markdown("Your narrated scientific explainer video is ready for playback below.")
    st.write("---")
    
    output_movie_path = os.path.join(SCRATCH_DIR, "final_explainer.mp4")
    
    # Read and map binary movie bytes directly into frame viewport container
    if os.path.exists(output_movie_path):
        with open(output_movie_path, "rb") as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)
    else:
        st.error("❌ Media Player Error: The final explainer MP4 file could not be fetched from storage.")
        
    st.write("---")
    
    if st.button("⬅️ Convert Another Document", type="primary", use_container_width=True, key="convert_another_btn"):
        switch_to_upload()
        st.rerun()
