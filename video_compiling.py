import os
import json
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

def compile_final_video(manifest_path="output_scratch/video_manifest.json", output_video_path="output_scratch/final_explainer.mp4"):
    """
    Reads the timeline manifest, loads the audio clips and matching cropped figures,
    and stitches them together into a final playable MP4 video.
    """
    # 1. Load your stopwatch timeline blueprint
    if not os.path.exists(manifest_path):
        print(f"❌ Error: Cannot find manifest blueprint at {manifest_path}. Run audio_engine.py first!")
        return

    with open(manifest_path, "r") as f:
        master_timeline = json.load(f)

    video_clips = []
    print("🎬 Starting video assembly line. Rendering scenes...")

    # 2. Build each scene one by one based on timestamps
    for item in master_timeline:
        text_line = item["text"]
        clip_path = item["clip_path"]
        visual_name = item["visual"]
        duration = item["t_end"] - item["t_start"]

        # Define the path to the cropped figure image we generated earlier
        image_path = os.path.join("output_scratch", visual_name)
        
        # Fallback placeholder if a specific figure isn't present
        if not os.path.exists(image_path) or not visual_name:
            # Look for any extracted image in the scratch folder as a fallback
            fallback_images = [f for f in os.listdir("output_scratch") if f.endswith('.png')]
            image_path = os.path.join("output_scratch", fallback_images[0]) if fallback_images else None

        if not image_path:
            print("⚠️ Warning: No visual images found to display on screen!")
            continue

        try:
            # Modern MoviePy 2.x updates:
            # - Use .with_duration() instead of .set_duration()
            # - Use .with_audio() instead of .set_audio()
            slide_clip = ImageClip(image_path).with_duration(duration)
            audio_clip = AudioFileClip(clip_path)
            slide_clip = slide_clip.with_audio(audio_clip)
            
            video_clips.append(slide_clip)
            print(f"   🎥 Generated Scene: Displaying {visual_name} for {duration} seconds.")
        except Exception as e:
            print(f"   ❌ Skipped scene due to rendering issue: {e}")

    # 3. Glue all individual scenes together into one continuous movie sequence
    if video_clips:
        print("整合 Stitching all compiled scenes into a single movie track...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Render the raw layers out into a high-quality playable .mp4 asset file
        final_video.write_videofile(
            output_video_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac"
        )
        print(f"🏁 SUCCESS! Your final explainer video is ready: {output_video_path}")
    else:
        print("❌ Video production aborted: No valid scenes were processed.")

if __name__ == "__main__":
    compile_final_video()
