import os
import asyncio
import edge_tts
from groq import Groq
import google.generativeai as genai
import cohere
from huggingface_hub import InferenceClient
from moviepy import AudioFileClip, ColorClip

# বিভিন্ন এআই প্রোভাইডারের এপিআই কি গিটহাব সিক্রেট থেকে রিড করা হচ্ছে
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

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

    # --- AI PROVIDER 3: Cohere API ---
    if not script_content and COHERE_API_KEY:
        try:
            print("Switching to AI Provider 3: Cohere...")
            co = cohere.Client(COHERE_API_KEY)
            response = co.chat(
                model='command-r-plus',
                message=prompt,
            )
            if response and response.text:
                script_content = response.text
                print("Success via Cohere (command-r-plus)")
        except Exception as e:
            print(f"Cohere error: {e}")

    # --- AI PROVIDER 4: Hugging Face Inference API ---
    if not script_content and HUGGINGFACE_API_KEY:
        try:
            print("Switching to AI Provider 4: Hugging Face...")
            client = InferenceClient(api_key=HUGGINGFACE_API_KEY)
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            script_content = response.choices[0].message.content
            if script_content:
                print("Success via Hugging Face Mistral")
        except Exception as e:
            print(f"Hugging Face error: {e}")

    # চূড়ান্ত চেক: যদি একটি এআইও সচল না থাকে
    if not script_content:
        raise RuntimeError("All configured AI providers failed. Please check your API keys.")

    # ১. ভয়েসওভার জেনারেট করা
    asyncio.run(generate_voiceover(script_content))
    
    # ২. ভিডিও রেন্ডার করা
    create_video()

if __name__ == "__main__":
    generate_movie_script()
