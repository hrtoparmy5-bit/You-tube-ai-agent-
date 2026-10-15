import os
from groq import Groq

# গিটহাব সিক্রেট থেকে Groq এপিআই কি রিড করবে
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=GROQ_API_KEY)

def generate_movie_script():
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Also provide a catchy YouTube title and SEO description."
    
    # গ্রোকের বর্তমান সবচেয়ে স্টবল ও রিলায়েবল মডেল ব্যবহার করা হলো
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192"]
    
    success = False
    for model_name in models_to_try:
        try:
            print( tratando model: {model_name})
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
            print(f"Model {model_name} failed with error: {e}")
            continue
            
    if not success:
        raise RuntimeError("All models failed. Please check your Groq API key and account limits.")

if __name__ == "__main__":
    generate_movie_script()
