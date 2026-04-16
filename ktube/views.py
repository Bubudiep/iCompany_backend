from rest_framework.views import APIView
from rest_framework.response import Response
from .services import YoutubeService
from rest_framework.permissions import AllowAny

class SearchKaraokeAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        query = request.query_params.get('q', '')
        limit = request.query_params.get('l', 20)
        if not query:
            return Response({"error": "Vui lòng nhập từ khóa"}, status=400)
        data = YoutubeService.get_video_info(query,limit)
        if not data:
            return Response({"error": "Không tìm thấy kết quả"}, status=500)
        # Chuẩn hóa dữ liệu trả về cho Frontend
        results = []
        for entry in data.get('entries', []):
            results.append({
                "id": entry.get("id"),
                "title": entry.get("title"),
                "thumbnail": f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg",
                "duration": entry.get("duration"),
                "uploader": entry.get("uploader")
            })
        return Response(results)

class GetStreamUrlAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        video_id = request.query_params.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        data = YoutubeService.get_video_info(video_url, is_url=True)
        if data and 'url' in data:
            return Response({"stream_url": data['url']})
        
        return Response({"error": "Không lấy được link stream"}, status=500)