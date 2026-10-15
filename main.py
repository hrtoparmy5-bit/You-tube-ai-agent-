import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=GROQ_API_KEY)

def generate_movie_script():
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Also provide a catchy YouTube title and SEO description."
    
    # বর্তমানের যেকোনো সচল মডেল অটো-ডিটেক্ট করার জন্য
    try:
        models_response = client.models.list()
        available_models = [m.id for m in models_response.data if "llama" in m.id or "mixtral" in m.id or "gemma" in m.id]
        print(f"Available models found: {available_models}")
    except Exception as e:
        print(f"Could not list models: {e}")
        available_models = ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]

    success = False
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
            print(f"--- Generated AI Movie Script (via {model_name}) ---")
            print(chat_completion.choices[0].message.content)
            success = True
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    if not success:
        raise RuntimeError("All available models failed. Please check your Groq API key permissions.")

if __name__ == "__main__":
    generate_movie_script()
