import os
from groq import Groq

# গিটহাব সিক্রেট থেকে Groq এপিআই কি রিড করবে
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set!")

client = Groq(api_key=GROQ_API_KEY)

def generate_movie_script():
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Also provide a catchy YouTube title and SEO description."
    
    # বর্তমানের সচল ও লেটেস্ট মডেল নাম ব্যবহার করা হলো
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
    )
    
    print("--- Generated AI Movie Script (via Groq) ---")
    print(chat_completion.choices[0].message.content)

if __name__ == "__main__":
    generate_movie_script()
