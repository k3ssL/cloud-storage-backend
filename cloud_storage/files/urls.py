from django.urls import path
from .views import FileUploadAPIView, FileEditAPIView, FileAccessAPIView, UserFilesView, SharedFilesView

app_name = 'files'

urlpatterns = [
    path('files', FileUploadAPIView.as_view(), name='file-upload'),
    path('files/<int:id>/', FileEditAPIView.as_view(), name='file-edit'),
    path('files/<int:id>/accesses/', FileAccessAPIView.as_view(), name='file-access'),
    path('files/disk/', UserFilesView.as_view(), name='user-files'),
    path('shared', SharedFilesView.as_view(), name='shared-files'),
]
