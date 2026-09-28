import yt_dlp
import os

class VideoDownloader:
    def __init__(self, config):
        self.input_dir = config['paths']['input_dir']
        os.makedirs(self.input_dir, exist_ok=True)

    def download(self, url):
        print("[Downloader] ইউটিউব ভিডিও ডাউনলোড শুরু হয়েছে...")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': os.path.join(self.input_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
