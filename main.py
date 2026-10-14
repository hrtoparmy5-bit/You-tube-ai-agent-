import os
import google.generativeai as genai

# গিটহাব সিক্রেট থেকে এপিআই কি রিড করবে
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set!")

genai.configure(api_key=GOOGLE_API_KEY)

def generate_movie_script():
    # লেটেস্ট জেমিনি মডেল ব্যবহার করা
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "Find a currently trending popular movie and write an engaging, suspenseful 3-minute movie explanation voiceover script in a storytelling style. Also provide a catchy YouTube title and SEO description."
    
    response = model.generate_content(prompt)
    print("--- Generated AI Movie Script ---")
    print(response.text)

if __name__ == "__main__":
    generate_movie_script()
