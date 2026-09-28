from flask import Flask, render_template, request
import os
import json

# আপনার তৈরি করা সমস্ত ইঞ্জিন ইমপোর্ট করা হচ্ছে
from modules.downloader import VideoDownloader
from modules.transcriber import AudioTranscriber
from modules.ai_selector import ViralClipSelector
from modules.tracker import FaceTracker
from modules.editor import FFmpegEditor

app = Flask(__name__)

# Config ফাইল রিড করা
with open("config.json", 'r') as f:
    config = json.load(f)

# ইনপুট এবং আউটপুট ফোল্ডার নিশ্চিত করা
os.makedirs(config['paths']['input_dir'], exist_ok=True)
os.makedirs(config['paths']['output_dir'], exist_ok=True)

# সমস্ত ইঞ্জিন ইনিশিয়ালাইজ (চালু) করা
print("--- Initializing AI Engines ---")
downloader = VideoDownloader(config)
transcriber = AudioTranscriber(config)
ai_selector = ViralClipSelector(config)
tracker = FaceTracker(config)
editor = FFmpegEditor(config)
print("--- System Ready! ---\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        video_file = request.files.get('video_file')
        video_path = None

        # ১. ভিডিও রিসিভ করা (YouTube বা Upload)
        if youtube_url:
            video_path = downloader.download(youtube_url)
            message = "YouTube ভিডিও ডাউনলোড সম্পন্ন। প্রসেসিং চলছে..."
        elif video_file and video_file.filename:
            video_path = os.path.join(config['paths']['input_dir'], video_file.filename)
            video_file.save(video_path)
            message = "ভিডিও আপলোড সম্পন্ন। প্রসেসিং চলছে..."

        # ২. মূল AI প্রসেসিং পাইপলাইন
        if video_path:
            try:
                # ধাপ ১: ভিডিও থেকে অডিও টেক্সটে রূপান্তর
                transcript = transcriber.generate_transcript(video_path)
                
                # ধাপ ২: Gemini দিয়ে স্ক্রিপ্ট পড়ে সেরা ভাইরাল অংশগুলো বের করা
                clips = ai_selector.find_best_clips(transcript)
                
                # ধাপ ৩ ও ৪: প্রতিটি ক্লিপের জন্য ট্র্যাকিং এবং এডিটিং
                for i, clip in enumerate(clips):
                    start_time = clip['start']
                    end_time = clip['end']
                    
                    # ফেস ট্র্যাকিং করে ক্রপ ডাইমেনশন বের করা
                    crop_data = tracker.get_crop_coordinates(video_path, start_time)
                    
                    # FFmpeg দিয়ে ভিডিও কাটা এবং রেন্ডার করা
                    output_name = f"viral_shorts_clip_{i+1}.mp4"
                    editor.render_clip(video_path, start_time, end_time, output_name, crop_data)
                    
                message = f"ম্যাজিক সফল! {len(clips)} টি ভাইরাল শর্টস তৈরি হয়েছে (data/output ফোল্ডার চেক করুন)।"
                
            except Exception as e:
                print(f"[Error] প্রসেসিংয়ে সমস্যা: {e}")
                message = "ভিডিও প্রসেস করতে গিয়ে কোনো সমস্যা হয়েছে, টার্মিনাল লগ চেক করুন।"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    # Railway বা লোকাল মেশিনের জন্য সার্ভার রান
    app.run(debug=True, host='0.0.0.0', port=5000)
