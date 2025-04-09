from .a import *
import google.generativeai as genai

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Nếu muốn chỉ cho xem/cập nhật profile của chính mình
    def get_queryset(self):
        # Chỉ trả về profile của người dùng hiện tại
        return UserProfile.objects.filter(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save()  # Bạn có thể gắn thêm logic ở đây nếu muốn log cập nhật


genai.configure(api_key=settings.GOOGLE_API_KEY)
class chatGemini(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, format=None, *args, **kwargs):
        user=request.user
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'error': 'Vui lòng gửi prompt!'}, status=400)
        try:
            # Dữ liệu ngữ cảnh cài sẵn
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "hello"
                        }
                    ]
                }
            ]
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(contents)
            return Response({
                'prompt': prompt,
                'response': response.text
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)