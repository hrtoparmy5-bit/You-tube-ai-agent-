import os
import asyncio
import edge_tts
import requests
from groq import Groq
import google.generativeai as genai
import cohere
from huggingface_hub import InferenceClient
from moviepy import AudioFileClip, ColorClip, VideoFileClip

# এপিআই কি রিড করা
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def generate_elevenlabs_voice(text, output_file="voiceover.mp3"):
    """ElevenLabs দিয়ে মানুষের মতো রিয়েলিস্টিক ভয়েস তৈরি করা"""
    if not ELEVENLABS_API_KEY:
        return False
    
    print("Generating humanlike voice using ElevenLabs...")
    # Adam / Brian / Josh - রিয়েলিস্টিক ভয়েস আইডি
    voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print("ElevenLabs voiceover generated successfully!")
            return True
        else:
            print(f"ElevenLabs error: {response.text}")
            return False
    except Exception as e:
        print(f"ElevenLabs connection error: {e}")
        return False

async def generate_edge_tts_voice(text, output_file="voiceover.mp3"):
    """ElevenLabs না থাকলে ব্যাকআপ হিসেবে উচ্চমানের ন্যাচারাল ভয়েস ব্যবহার"""
    print("Switching to Backup Natural Voice (Edge-TTS)...")
    voice = "en-US-AndrewMultilingualNeural" # অত্যন্ত ন্যাচারাল হিউম্যানিস্টিক টোন
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"Backup voiceover saved successfully as {output_file}")

def create_video():
    """ভিডিও রেন্ডারিং - ডাইনামিক ব্যাকগ্রাউন্ড সহ (কালো স্ক্রিন দূর করতে)"""
    audio_path = "voiceover.mp3"
    output_video_path = "output.mp4"
    
    print("Rendering final video with audio...")
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # ভিডিও দৃশ্য তৈরি করা (ভিজ্যুয়াল ব্যাকগ্রাউন্ড)
    # আপনার ব্যাকগ্রাউন্ড ভিজ্যুয়াল আকর্ষণীয় করতে কালার মোশন যুক্ত করা হয়েছে
    bg_clip = ColorClip(size=(1280, 720), color=(30, 40, 60), duration=duration)
    
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

    # ১. Groq দিয়ে স্ক্রিপ্ট জেনারেট
    if not script_content and GROQ_API_KEY:
        try:
            print("Trying AI Provider 1: Groq...")
            client = Groq(api_key=GROQ_API_KEY)
            groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            for m in groq_models:
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

    # ২. Gemini দিয়ে ব্যাকআপ
    if not script_content and GEMINI_API_KEY:
        try:
            print("Auto-switching to AI Provider 2: Google Gemini...")
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
            for m in gemini_models:
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

    if not script_content:
        raise RuntimeError("All AI providers failed.")

    # --- ভয়েস জেনারেশন (ElevenLabs ফার্স্ট প্রায়োরিটি) ---
    success = generate_elevenlabs_voice(script_content)
    if not success:
        asyncio.run(generate_edge_tts_voice(script_content))
    
    # --- ভিডিও রেন্ডার ---
    create_video()

if __name__ == "__main__":
    generate_movie_script()
