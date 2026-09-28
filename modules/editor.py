import subprocess
import os

class FFmpegEditor:
    def __init__(self, config):
        self.output_dir = config['paths']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def render_clip(self, input_video, start_time, end_time, output_name):
        output_path = os.path.join(self.output_dir, output_name)
        print(f"[FFmpeg] ক্লিপ তৈরি হচ্ছে: {output_path}")
        
        # FFmpeg কমান্ড (ভিডিও কাটা)
        cmd = [
            "ffmpeg", "-y", "-i", input_video,
            "-ss", str(start_time), "-to", str(end_time),
            "-c:v", "libx264", "-c:a", "aac", output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return output_path
