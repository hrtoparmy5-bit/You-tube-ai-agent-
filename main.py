import os
import asyncio
import edge_tts
from groq import Groq
import google.generativeai as genai
from moviepy import AudioFileClip, ColorClip

# এপিআই কি গিটহাব সিক্রেট থেকে রিড করা হচ্ছে
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
    
    bg_clip = ColorClip(size=(1280, 720), color=(20, 24, 33), duration=duration)
    video_clip = bg_clip.with_audio(audio_clip)
    
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
    
    script_content = None

    # --- AI PROVIDER 1: Groq API ---
    if not script_content and GROQ_API_KEY:
        try:
            print("Trying AI Provider 1: Groq...")
            client = Groq(api_key=GROQ_API_KEY)
            models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            for m in models:
                try:
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=m)
                    script_content = res.choices[0].message.content
                    if script_content:
                        print(f"Success via Groq ({m})")
                        break
                except Exception as e:
                    print(f"Groq {m} error: {e}")
        except Exception as e:
            print(f"Groq init error: {e}")

    # --- AI PROVIDER 2: Google Gemini API ---
    if not script_content and GEMINI_API_KEY:
        try:
            print("Switching to AI Provider 2: Google Gemini...")
            genai.configure(api_key=GEMINI_API_KEY)
            models = ["gemini-1.5-flash", "gemini-1.5-pro"]
            for m in models:
                try:
                    model = genai.GenerativeModel(m)
                    res = model.generate_content(prompt)
                    if res and res.text:
                        script_content = res.text
                        print(f"Success via Gemini ({m})")
                        break
                except Exception as e:
                    print(f"Gemini {m} error: {e}")
        except Exception as e:
            print(f"Gemini init error: {e}")

    # চূড়ান্ত চেক
    if not script_content:
        raise RuntimeError("Both Groq and Gemini failed. Please check your API keys.")

    # ১. ভয়েসওভার জেনারেট করা
    asyncio.run(generate_voiceover(script_content))
    
    # ২. ভিডিও রেন্ডার করা
    create_video()

if __name__ == "__main__":
    generate_movie_script()
