import whisper
import os

class AudioTranscriber:
    def __init__(self, config):
        # config.json থেকে মডেল সাইজ নেবে (যেমন: "base" বা "tiny")
        model_size = config['settings'].get('whisper_model', 'base')
        print(f"[Whisper] '{model_size}' মডেল লোড হচ্ছে... (একটু সময় লাগতে পারে)")
        self.model = whisper.load_model(model_size)

    def generate_transcript(self, video_path):
        print(f"[Whisper] ভিডিও থেকে টেক্সট ও টাইমস্ট্যাম্প বের করা হচ্ছে: {video_path}")
        
        # ট্রান্সক্রিপশন প্রসেস
        result = self.model.transcribe(video_path)
        
        # Gemini-কে দেওয়ার জন্য টেক্সট ও টাইমস্ট্যাম্প সুন্দর করে সাজানো
        formatted_transcript = ""
        for segment in result['segments']:
            start = round(segment['start'], 2)
            end = round(segment['end'], 2)
            text = segment['text'].strip()
            formatted_transcript += f"[{start} - {end}] {text}\n"
            
        print("[Whisper] ট্রান্সক্রিপশন সফলভাবে সম্পন্ন হয়েছে!")
        return formatted_transcript
