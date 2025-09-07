# Thêm vào file views.py

class AdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Admin management
    """
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [AllowAny]  # Có thể thay đổi thành IsAuthenticated nếu cần

    def get_queryset(self):
        return Admin.objects.all()

    @action(detail=False, methods=['post'], url_path='create-admin')
    def create_admin(self, request):
        """
        Create a new admin user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            return Response({
                'success': True,
                'message': 'Tạo tài khoản admin thành công',
                'admin_id': admin.id,
                'phone_number': admin.phone_number,
                'email': admin.email
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Lỗi khi tạo tài khoản admin',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='admin-login')
    def admin_login(self, request):
        """
        Admin login with phone number and password
        """
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        if not phone_number or not password:
            return Response({
                'success': False,
                'message': 'Vui lòng cung cấp số điện thoại và mật khẩu'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            admin = Admin.objects.get(phone_number=phone_number)
            if admin.check_password(password) and admin.is_active:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(admin)
                return Response({
                    'success': True,
                    'message': 'Đăng nhập admin thành công',
                    'admin': AdminSerializer(admin).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Mật khẩu không đúng hoặc tài khoản bị vô hiệu hóa'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Admin.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Không tìm thấy tài khoản admin với số điện thoại này'
            }, status=status.HTTP_404_NOT_FOUND)
 
 
 
 