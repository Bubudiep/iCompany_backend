import yt_dlp

class YoutubeService:
    @staticmethod
    def get_video_info(query, is_url=False, limit=20):
        """
        Lấy thông tin video hoặc tìm kiếm bài hát karaoke
        """
        ydl_opts = {
            # Ép lấy 1080p mp4 để tương thích tốt nhất
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            'noplaylist': True,
            'quiet': True,
            'nocheckcertificate': True,
            'extract_flat': 'in_playlist' if not is_url else False,
        }
        search_query = query if is_url else f"ytsearch{limit}:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_query, download=False)
                return info
            except Exception as e:
                print(f"YTDLP Error: {e}")
                return None