import subprocess
import os

class FFmpegEditor:
    def __init__(self, config):
        self.output_dir = config['paths']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def render_clip(self, input_video, start_time, end_time, output_name, crop_data):
        output_path = os.path.join(self.output_dir, output_name)
        print(f"[FFmpeg] রেন্ডারিং শুরু হচ্ছে (Time: {start_time} - {end_time}): {output_name}")
        
        # ট্র্যাকার থেকে পাওয়া ডেটা দিয়ে ক্রপ ফিল্টার তৈরি করা
        # ফরম্যাট: crop=width:height:x:y
        crop_filter = f"crop={crop_data['w']}:{crop_data['h']}:{crop_data['x']}:{crop_data['y']}"
        print(f"[FFmpeg] ক্রপ ডাইমেনশন অ্যাপ্লাই করা হচ্ছে: {crop_filter}")
        
        # FFmpeg কমান্ড (-vf বা Video Filter দিয়ে ক্রপ যুক্ত করা হয়েছে)
        cmd = [
            "ffmpeg", "-y", 
            "-i", input_video,
            "-ss", str(start_time), 
            "-to", str(end_time),
            "-vf", crop_filter,           # এখানেই ম্যাজিকটা হচ্ছে!
            "-c:v", "libx264",            # ভিডিও কোডেক
            "-c:a", "aac",                # অডিও কোডেক
            output_path
        ]
        
        # টার্মিনালে কমান্ড রান করা (অপ্রয়োজনীয় লগ হাইড করা হয়েছে)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"[FFmpeg] রেন্ডারিং সফল! ভিডিও সেভ হয়েছে: {output_path}\n")
        return output_path
