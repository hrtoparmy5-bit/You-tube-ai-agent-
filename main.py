import os
import asyncio
import edge_tts
import requests
from groq import Groq
import google.generativeai as genai
import cohere
from huggingface_hub import InferenceClient
from moviepy import AudioFileClip, ColorClip

# গিটহাব সিক্রেট থেকে ৪টি এআই-এর এপিআই কি রিড করা হচ্ছে
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

    # ==========================================
    # --- AI PROVIDER 1: Groq API ---
    # ==========================================
    if not script_content and GROQ_API_KEY:
        try:
            print("Trying AI Provider 1: Groq...")
            client = Groq(api_key=GROQ_API_KEY)
            groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]
            for m in groq_models:
                try:
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=m)
                    script_content = res.choices[0].message.content
                    if script_content:
                        print(f"Success! Script generated via Groq ({m})")
                        break
                except Exception as e:
                    print(f"Groq ({m}) error: {e}. Trying next Groq model...")
        except Exception as e:
            print(f"Groq init error: {e}. Auto-switching to Provider 2...")

    # ==========================================
    # --- AI PROVIDER 2: Google Gemini API ---
    # ==========================================
    if not script_content and GEMINI_API_KEY:
        try:
            print("Auto-switching to AI Provider 2: Google Gemini...")
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            for m in gemini_models:
                try:
                    model = genai.GenerativeModel(m)
                    res = model.generate_content(prompt)
                    if res and res.text:
                        script_content = res.text
                        print(f"Success! Script generated via Gemini ({m})")
                        break
                except Exception as e:
                    print(f"Gemini ({m}) error: {e}. Trying next Gemini model...")
        except Exception as e:
            print(f"Gemini init error: {e}. Auto-switching to Provider 3...")

    # ==========================================
    # --- AI PROVIDER 3: Cohere API ---
    # ==========================================
    if not script_content and COHERE_API_KEY:
        try:
            print("Auto-switching to AI Provider 3: Cohere...")
            co = cohere.Client(COHERE_API_KEY)
            cohere_models = ["command-r-08-2024", "command-light", "command-nightly"]
            for m in cohere_models:
                try:
                    response = co.chat(model=m, message=prompt)
                    if response and response.text:
                        script_content = response.text
                        print(f"Success! Script generated via Cohere ({m})")
                        break
                except Exception as e:
                    print(f"Cohere ({m}) error: {e}. Trying next Cohere model...")
        except Exception as e:
            print(f"Cohere init error: {e}. Auto-switching to Provider 4...")

    # ==========================================
    # --- AI PROVIDER 4: Hugging Face API ---
    # ==========================================
    if not script_content and HUGGINGFACE_API_KEY:
        try:
            print("Auto-switching to AI Provider 4: Hugging Face...")
            hf_models = ["meta-llama/Llama-3.2-1B-Instruct", "mistralai/Mistral-7B-Instruct-v0.2", "Qwen/Qwen2.5-72B-Instruct"]
            for m in hf_models:
                try:
                    client = InferenceClient(model=m, token=HUGGINGFACE_API_KEY)
                    response = client.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000,
                    )
                    script_content = response.choices[0].message.content
                    if script_content:
                        print(f"Success! Script generated via Hugging Face ({m})")
                        break
                except Exception as e:
                    print(f"Hugging Face ({m}) error: {e}. Trying next HF model...")
        except Exception as e:
            print(f"Hugging Face init error: {e}")

    # ==========================================
    # --- FINAL CHECK ---
    # ==========================================
    if not script_content:
        raise RuntimeError("Autonomous Fail-safe Error: All 4 AI providers (Groq, Gemini, Cohere, HuggingFace) failed. Please check your API keys.")

    # ভয়েসওভার ও ভিডিও তৈরি
    asyncio.run(generate_voiceover(script_content))
    create_video()

if __name__ == "__main__":
    generate_movie_script()
