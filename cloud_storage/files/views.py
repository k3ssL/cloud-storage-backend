from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UploadedFile
from .serializers import FileSerializer
from users.models import User

class FileUploadAPIView(APIView):
    def post(self, request, *args, **kwargs):

        files = request.FILES.getlist('files')
        results = []

        # Проверяем, не пустой ли запрос
        if not files:
            return Response({
                "success": False,
                "message": "Request is empty"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Перебираем массив файлов
        for uploaded_file in files:
            serializer = FileSerializer(
                data={'file': uploaded_file, 'user': request.user.pk},
                context={'request': request}
            )
            # Проверяем, авторизован ли пользователь
            if not request.user.is_authenticated:
                return Response({
                    "success": False,
                    "message": "Login Failed"
                }, status=status.HTTP_401_UNAUTHORIZED)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                results.append({
                    "success": True,
                    "message": "Success",
                    "name": uploaded_file.name,
                    "url": f'host/files/{serializer.data['file_id']}',
                    "file_id": serializer.data['file_id']
                })
            else:
                error_messages = {}
                for key, value in serializer.errors.items():
                    error_messages[key] = value[0]
                results.append({
                    "success": False,
                    "message": error_messages,
                    "name": uploaded_file.name
                })

        return Response(results, status=status.HTTP_200_OK)


class FileEditAPIView(APIView):

    def patch(self, request, id):

        # Проверяем существует ли файл
        try:
            uploaded_file = UploadedFile.objects.filter(id=id).first()
        except UploadedFile.DoesNotExist:
            return Response({
                "success": False,
                "message": "File not found"
            }, status=status.HTTP_404_NOT_FOUND)
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)
        # Проверяем, имеет ли пользователь доступ к файлу
        if uploaded_file.user != request.user:
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = FileSerializer(uploaded_file, data=request.data, partial=True)

        # Проверяем, не пустой ли запрос был отправлен
        if 'name' not in request.data or not request.data['name']:
            return Response({
                "success": False,
                "message": "Name cannot be empty"
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            data = request.data
            new_name = data.get('name', '')

            # Редактируем имя файла
            UploadedFile.objects.filter(id=uploaded_file.id).update(name=new_name)

            return Response({
                "success": True,
                "message": "Renamed"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, id):

        # Проверяем существует ли файл
        try:
            uploaded_file = UploadedFile.objects.get(id=id)
        except UploadedFile.DoesNotExist:
            return Response({
                "success": False,
                "message": "File not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"},
                status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем, имеет ли пользователь доступ к файлу
        if uploaded_file.user != request.user:
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        # Удаляем файл
        uploaded_file.delete()

        return Response({
            "success": True,
            "message": "File already deleted"
        }, status=status.HTTP_200_OK)

    def get(self, request, id):

        # Проверяем, существует ли файл
        try:
            uploaded_file = UploadedFile.objects.get(id=id)
        except UploadedFile.DoesNotExist:
            return Response({
                "success": False,
                "message": "File not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем, имеет ли пользователь доступ к файлу
        if uploaded_file.user != request.user:
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        # Отдаем файл для скачивания
        file_path = uploaded_file.file.path
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{uploaded_file.name}"'
            return response


class FileAccessAPIView(APIView):
    def post(self, request, id):

        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем, существует ли файл
        try:
            uploaded_file = UploadedFile.objects.get(id=id)
        except UploadedFile.DoesNotExist:
            return Response({
                "success": False,
                "message": "File not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, имеет ли пользователь доступ к файлу
        if uploaded_file.user != request.user:
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        # Получаем email пользователя из тела запроса
        email = request.data.get('email', '')

        # Проверяем, существует ли пользователь с таким email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Добавляем пользователя к списку с доступом к файлу
        uploaded_file.access_users.add(user)

        # Возвращаем список пользователей с доступом к файлу
        access_list = [{
            "fullname": user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name} {user.last_name}",
            "email": user.email,
            "type": "co-author" if user != request.user else "author"
        } for user in uploaded_file.access_users.all()]

        return Response(access_list, status=status.HTTP_200_OK)

    def delete(self, request, id):

        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем, существует ли файл
        uploaded_file = get_object_or_404(UploadedFile, id=id)

        # Проверяем, является ли пользователь владельцем файла
        if uploaded_file.user != request.user:
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        # Получаем email из данных запроса
        email = request.data.get('email', '')

        # Проверяем, существует ли пользователь с указанным email
        try:
            user_to_remove = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "File not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли пользователь в списке доступа к файлу
        if user_to_remove not in uploaded_file.access_users.all():
            return Response({
                "success": False,
                "message": "Forbidden for you"
            }, status=status.HTTP_403_FORBIDDEN)

        # Удаляем пользователя из списка доступа к файлу
        uploaded_file.access_users.remove(user_to_remove)

        # Возвращаем обновленный список пользователей с доступом к файлу
        access_list = [{
            "fullname": user.get_full_name() if hasattr(user, 'get_full_name') else f"{user.first_name} {user.last_name}",
            "email": user.email,
            "type": "co-author" if user != request.user else "author"
        } for user in uploaded_file.access_users.all()]

        return Response(access_list, status=status.HTTP_200_OK)


class UserFilesView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_files = UploadedFile.objects.filter(user=request.user)
        serializer = FileSerializer(user_files, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SharedFilesView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Login Failed"
            }, status=status.HTTP_401_UNAUTHORIZED)

        shared_files = UploadedFile.objects.exclude(user=request.user)
        serializer = FileSerializer(shared_files, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)