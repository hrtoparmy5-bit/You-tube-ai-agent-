import os
import asyncio
import edge_tts
from groq import Groq
from moviepy import AudioFileClip, ColorClip

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=GROQ_API_KEY)

async def generate_voiceover(text, output_file="voiceover.mp3"):
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"Voiceover saved successfully as {output_file}")

def create_video():
    audio_path = "voiceover.mp3"
    output_video_path = "output.mp4"
    
    print("Rendering video using MoviePy...")
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # 1280x720 রেজোলিউশনের ডার্ক ব্যাকগ্রাউন্ড ক্লিপ
    bg_clip = ColorClip(size=(1280, 720), color=(20, 24, 33), duration=duration)
    
    video_clip = bg_clip.set_audio(audio_clip)
    
    video_clip.write_videofile(
        output_video_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='ultrafast',
        logger=None
    )
    print(f"Video rendered successfully as {output_video_path}")

def generate_movie_script():
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Do not include extra markdown intro, just give the direct voiceover text."
    
    try:
        models_response = client.models.list()
        available_models = [m.id for m in models_response.data if "llama" in m.id]
    except Exception:
        available_models = ["llama3-8b-8192"]

    success = False
    script_content = ""
    for model_name in available_models:
        try:
            print(f"Trying model: {model_name}")
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_name,
            )
            script_content = chat_completion.choices[0].message.content
            print(f"--- Generated AI Movie Script (via {model_name}) ---")
            print(script_content[:200] + "...")
            success = True
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    if not success:
        raise RuntimeError("All available models failed.")

    # ১. ভয়েসওভার জেনারেট করা
    asyncio.run(generate_voiceover(script_content))
    
    # ২. ভিডিও রেন্ডার করা
    create_video()

if __name__ == "__main__":
    generate_movie_script()
