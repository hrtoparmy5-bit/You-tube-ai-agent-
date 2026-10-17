import os
import asyncio
import edge_tts
from groq import Groq
from moviepy import AudioFileClip, ColorClip

# ইউনিভার্সাল বা ফ্রি এগ্রিগেটর এপিআই কি
UNIVERSAL_API_KEY = os.environ.get("UNIVERSAL_API_KEY")

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
    
    if not UNIVERSAL_API_KEY:
        raise ValueError("UNIVERSAL_API_KEY environment variable is not set!")

    # যেহেতু এই প্ল্যাটফর্মগুলো OpenAI কম্প্যাটিবল বেস ইউআরএল ব্যবহার করে, তাই বেস ইউআরএল সেট করতে হবে
    # (যদি সাইটটির নিজস্ব কাস্টম বেস ইউআরএল থাকে তা এখানে বসাতে হবে)
    client = Groq(
        api_key=UNIVERSAL_API_KEY,
        base_url="https://api.freellmapi.co/v1" # উদাহরণস্বরূপ ফ্রি এলএলএম এপিআই বেস ইউআরএল
    )

    models_to_try = ["gpt-4o", "claude-3-5-sonnet", "llama-3.3-70b-versatile"]
    script_content = None

    for model_name in models_to_try:
        try:
            print(f"Trying model via Universal API: {model_name}")
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
            )
            script_content = chat_completion.choices[0].message.content
            if script_content:
                print(f"Successfully generated script using {model_name}")
                break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    if not script_content:
        raise RuntimeError("All models failed on the universal API provider.")

    # ১. ভয়েসওভার জেনারেট করা
    asyncio.run(generate_voiceover(script_content))
    
    # ২. ভিডিও রেন্ডার করা
    create_video()

if __name__ == "__main__":
    generate_movie_script()
