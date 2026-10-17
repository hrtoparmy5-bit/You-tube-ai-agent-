import os
import asyncio
import edge_tts
from groq import Groq
import google.generativeai as genai
from moviepy import AudioFileClip, ColorClip

# এপিআই কি রিড করা
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

async def generate_bangla_voiceover(text, output_file="voiceover.mp3"):
    """একদম মানুষের মতো স্পষ্ট বাংলায় ভয়েসওভার জেনারেট করা"""
    print("Generating natural Bangla humanlike voiceover...")
    # বাংলার জন্য প্রাকৃতিকভাবে কথা বলার ভয়েস (PradeepNeural / TanishaNeural)
    voice = "bn-BD-PradeepNeural" 
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"Bangla voiceover saved successfully as {output_file}")

def create_video():
    """ভিডিও রেন্ডারিং (কালো স্ক্রিন দূর করতে ব্যাকগ্রাউন্ড কালার ও মোশন যুক্ত করা)"""
    audio_path = "voiceover.mp3"
    output_video_path = "output.mp4"
    
    print("Rendering video with Bangla audio...")
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # আকর্ষণীয় ব্যাকগ্রাউন্ড ভিজ্যুয়াল
    bg_clip = ColorClip(size=(1280, 720), color=(15, 23, 42), duration=duration)
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
    # সম্পূর্ণ বাংলায় মুভি এক্সপ্লেনেশন স্ক্রিপ্ট লেখার প্রম্পট
    prompt = (
        "বর্তমানে ট্রেন্ডিং বা জনপ্রিয় যেকোনো একটি দারুণ মুভি বেছে নিন। "
        "এরপর ওই মুভিটির একটি আকর্ষণীয়, সাসপেন্সফুল এবং গল্পের স্টাইলে ৩ মিনিটের একটি মুভি এক্সপ্লেনেশন ভয়েসওভার স্ক্রিপ্ট সম্পূর্ণ বাংলায় লিখুন। "
        "কোণো অতিরিক্ত ইংরেজি বা মার্কডাউন ভূমিকা ছাড়াই সরাসরি কেবল বাংলা ভয়েসওভারের মূল টেক্সটটুকু প্রদান করুন।"
    )
    
    script_content = None

    # --- ১. Groq দিয়ে বাংলা স্ক্রিপ্ট তৈরি ---
    if not script_content and GROQ_API_KEY:
        try:
            print("Trying AI Provider 1 (Groq) for Bangla script...")
            client = Groq(api_key=GROQ_API_KEY)
            models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            for m in models:
                try:
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=m)
                    script_content = res.choices[0].message.content
                    if script_content:
                        print(f"Success! Bangla script generated via Groq ({m})")
                        break
                except Exception as e:
                    print(f"Groq {m} error: {e}")
        except Exception as e:
            print(f"Groq init error: {e}")

    # --- ২. Google Gemini দিয়ে ব্যাকআপ বাংলা স্ক্রিপ্ট তৈরি ---
    if not script_content and GEMINI_API_KEY:
        try:
            print("Auto-switching to AI Provider 2 (Google Gemini) for Bangla script...")
            genai.configure(api_key=GEMINI_API_KEY)
            models = ["gemini-1.5-flash", "gemini-1.5-pro"]
            for m in models:
                try:
                    model = genai.GenerativeModel(m)
                    res = model.generate_content(prompt)
                    if res and res.text:
                        script_content = res.text
                        print(f"Success! Bangla script generated via Gemini ({m})")
                        break
                except Exception as e:
                    print(f"Gemini {m} error: {e}")
        except Exception as e:
            print(f"Gemini init error: {e}")

    if not script_content:
        raise RuntimeError("All AI providers failed to generate the Bangla script.")

    # ১. বাংলা ভয়েসওভার জেনারেট করা
    asyncio.run(generate_bangla_voiceover(script_content))
    
    # ২. ভিডিও রেন্ডার করা
    create_video()

if __name__ == "__main__":
    generate_movie_script()
