from flask import Flask, render_template, request
import os
import json
from modules.downloader import VideoDownloader
from modules.editor import FFmpegEditor

app = Flask(__name__)

# Config লোড
with open("config.json", 'r') as f:
    config = json.load(f)

# ফোল্ডার সেটআপ
os.makedirs(config['paths']['input_dir'], exist_ok=True)
os.makedirs(config['paths']['output_dir'], exist_ok=True)

downloader = VideoDownloader(config)
editor = FFmpegEditor(config)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        # ১. ইউটিউব লিংক চেক
        youtube_url = request.form.get('youtube_url')
        # ২. ফাইল আপলোড চেক
        video_file = request.files.get('video_file')
        
        video_path = None

        if youtube_url:
            video_path = downloader.download(youtube_url)
            message = f"YouTube ভিডিও ডাউনলোড সম্পন্ন: {os.path.basename(video_path)}"
            
        elif video_file and video_file.filename:
            video_path = os.path.join(config['paths']['input_dir'], video_file.filename)
            video_file.save(video_path)
            message = f"ভিডিও আপলোড সম্পন্ন: {video_file.filename}"
            
        if video_path:
            # এখানে আপাতত টেস্ট হিসেবে প্রথম ৬০ সেকেন্ড কেটে দেখা হচ্ছে
            # পরবর্তীতে এখানে Whisper ও Gemini এর লজিক বসবে
            output_name = "test_clip_1.mp4"
            editor.render_clip(video_path, 0, 60, output_name)
            message += " | ভিডিও প্রসেসিং (ভিডিও কাটা) সফল হয়েছে!"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
