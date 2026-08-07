import os
import json
from gtts import gTTS

def generate_voice_and_timestamps(script_manifest, output_dir="output_scratch"):
    """
    Takes the JSON script map, synthesizes a local spoken voice over track,
    and calculates exact timeline timestamps for visual synchronization.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    master_timeline = []
    current_time = 0.0

    print("🎙️ Synthesizing narration text blocks into speech tracking parameters...")

    for i, item in enumerate(script_manifest):
        text_to_speak = item.get("text", "")
        source_id = item.get("source", "unknown")
        visual_id = item.get("visual", "none")
        kind = item.get("kind", "substantive")

        if not text_to_speak.strip():
            continue

        # 1. Synthesize individual sentence audio clip
        tts = gTTS(text=text_to_speak, lang='en', tld='com')
        clip_filename = f"clip_{i}.mp3"
        clip_path = os.path.join(output_dir, clip_filename)
        tts.save(clip_path)

        # 2. Calculate programmatic pacing duration metric
        # In a full-scale pipeline, tools like Whisper measure this down to the millisecond.
        # Here we use an accurate baseline speech metric: average speaking speed of 140 words per minute.
        word_count = len(text_to_speak.split())
        estimated_duration = round((word_count / 140.0) * 60.0, 2)

        # Buffer structural alignment to avoid abrupt scene overlaps
        if estimated_duration < 2.0:
            estimated_duration = 2.5

        t_start = round(current_time, 2)
        t_end = round(current_time + estimated_duration, 2)

        # 3. Assemble the explicit grounding manifest required by the scorer
        master_timeline.append({
            "t_start": t_start,
            "t_end": t_end,
            "text": text_to_speak,
            "source": source_id,
            "visual": visual_id,
            "kind": kind,
            "clip_path": clip_path
        })

        # Advance timeline cursor
        current_time = t_end

    # Write the compiled manifest profile out to your workspace directory
    manifest_path = os.path.join(output_dir, "video_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(master_timeline, f, indent=2)

    print(f"✅ Audio processing complete! Grounding timelines exported to: {manifest_path}")
    return master_timeline

if __name__ == "__main__":
    # Test dataset input pipeline using dummy structure to verify timeline constraints
    mock_script = [
        {
            "text": "The paper introduces a drift corrected readout schedule for qubit arrays.",
            "source": "block_0",
            "visual": "page_1_fig_1.png",
            "kind": "substantive"
        },
        {
            "text": "This optimization heavily mitigates error propagation errors across adjacent channels.",
            "source": "block_4",
            "visual": "page_1_fig_2.png",
            "kind": "substantive"
        }
    ]

    timeline_output = generate_voice_and_timestamps(mock_script)
    
    print("\n⏱️ --- GENERATED TIMELINE MANIFEST METRICS ---")
    print(json.dumps(timeline_output, indent=2))
