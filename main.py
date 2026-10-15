import os
import asyncio
import edge_tts
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=GROQ_API_KEY)

async def generate_voiceover(text, output_file="voiceover.mp3"):
    # বাংলায় বা ইংরেজিতে চমৎকার কণ্ঠস্বর (এখানে ইংরেজি বা বাংলা ভয়েস সিলেক্ট করা যায়)
    # প্রাকৃতিকভাবে মুভি এক্সপ্লানেশনের জন্য একটি প্রফেশনাল ভয়েস ব্যবহার করা হচ্ছে
    voice = "en-US-ChristopherNeural" # অথবা বাংলা ভয়েস চাইলে 'bn-BD-PradeepNeural' দিতে পারেন
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"Voiceover saved successfully as {output_file}")

def generate_movie_script():
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Do not include extra markdown intro, just give the direct voiceover text."
    
    try:
        models_response = client.models.list()
        available_models = [m.id for m in models_response.data if "llama" in m.id]
        print(f"Available models found: {available_models}")
    except Exception as e:
        print(f"Could not list models: {e}")
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
            print(script_content)
            success = True
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    if not success:
        raise RuntimeError("All available models failed. Please check your Groq API key permissions.")

    # অডিও ভয়েসওভার জেনারেট করার ফাংশন কল করা
    asyncio.run(generate_voiceover(script_content))

if __name__ == "__main__":
    generate_movie_script()
