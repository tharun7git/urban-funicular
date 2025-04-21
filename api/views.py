from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from photoapp.models import Photo, Folder
from .serializers import PhotoSerializer, FolderSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from photoapp.models import Folder, Photo
from .serializers import PhotoSerializer
from django.utils.text import slugify

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({"message": "API is working!"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if (self.action == 'create'):
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def delete_folder(self, request, pk=None):
        try:
            folder = self.get_object()
            Photo.objects.filter(folder=folder).delete()
            folder.delete()
            return Response({'status': 'folder and its photos deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Folder.DoesNotExist:
            return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Photo.objects.filter(user=self.request.user)
        folder_id = self.request.query_params.get('folder', None)
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        foldername = request.query_params.get('foldername')
        filename = request.query_params.get('filename')

        if not user_id or not foldername or not filename:
            return Response({'error': 'user_id, foldername, and filename are required as query parameters.'}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        if 'image' not in request.FILES:
            return Response({'error': 'Image file is required.'}, status=400)

        # Get or create folder
        folder, _ = Folder.objects.get_or_create(name=foldername, user=user)

        image_file = request.FILES['image']
        image_file.name = filename

        photo = Photo.objects.create(
            title=filename,
            folder=folder,
            user=user,
            image=image_file
        )

        serializer = self.get_serializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_photo_custom(request):
    foldername = request.query_params.get('foldername')
    filename = request.query_params.get('filename')

    if not foldername or not filename or 'image' not in request.FILES:
        return Response({"error": "Missing foldername, filename or image"}, status=400)

    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    # Get or create the folder
    folder, _ = Folder.objects.get_or_create(user=user, name=foldername)

    image_file = request.FILES['image']
    image_file.name = filename  # Rename the uploaded file

    # Save the photo
    photo = Photo.objects.create(
        title=filename,
        folder=folder,
        user=user,
        image=image_file
    )

    serializer = PhotoSerializer(photo)
    return Response(serializer.data, status=201)
