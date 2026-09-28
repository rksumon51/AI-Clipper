import google.generativeai as genai
import json

class ViralClipSelector:
    def __init__(self, config):
        # config.json থেকে API Key লোড করা
        api_key = config['api_keys']['gemini_api_key']
        genai.configure(api_key=api_key)
        # ফাস্ট প্রসেসিংয়ের জন্য flash মডেল
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def find_best_clips(self, transcript):
        print("[Gemini AI] স্ক্রিপ্ট অ্যানালাইসিস করে ভাইরাল অংশ খোঁজা হচ্ছে...")
        
        # প্রম্পট (AI-কে ঠিকমতো ইনস্ট্রাকশন দেওয়া)
        prompt = f"""
        You are an expert AI video editor making viral shorts like Opus Clips. 
        I will give you a video transcript with timestamps. 
        Find the 3 most engaging, hook-driven, and interesting parts to create YouTube Shorts/TikToks.
        Each clip must be between 15 to 60 seconds long.
        
        Transcript:
        {transcript}
        
        Respond ONLY in a valid JSON array format like this, nothing else:
        [
            {{"start": 12.5, "end": 45.0, "reason": "A strong hook discussing the main topic"}},
            {{"start": 120.0, "end": 155.0, "reason": "Funny or interesting moment"}},
            {{"start": 210.0, "end": 260.0, "reason": "Valuable advice/conclusion"}}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Gemini অনেক সময় ```json ... ``` এর ভেতরে উত্তর দেয়, সেটা পরিষ্কার করা
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
                
            # JSON-কে পাইথনের লিস্টে কনভার্ট করা
            clips = json.loads(result_text)
            print(f"[Gemini AI] সফলভাবে {len(clips)} টি ভাইরাল ক্লিপ খুঁজে পাওয়া গেছে!")
            return clips
            
        except Exception as e:
            print(f"[Gemini Error] ক্লিপ খুঁজতে সমস্যা হয়েছে: {e}")
            # API এ কোনো সমস্যা হলে ব্যাকআপ হিসেবে প্রথম ৬০ সেকেন্ড রিটার্ন করবে
            return [{"start": 0.0, "end": 60.0, "reason": "Default fallback clip"}]
