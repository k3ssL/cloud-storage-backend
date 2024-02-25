from django.urls import path
from .views import FileUploadAPIView, FileEditAPIView, FileDeleteAPIView, FileDownloadAPIView, FileAccessAPIView

app_name = 'files'

urlpatterns = [
    path('files', FileUploadAPIView.as_view(), name='file-upload'),
    path('files/<int:id>/', FileEditAPIView.as_view(), name='file-edit'),
    path('files/<int:id>/', FileDeleteAPIView.as_view(), name='file-delete'),
    path('files/<int:id>/', FileDownloadAPIView.as_view(), name='file-download'),
    path('files/<int:id>/accesses/', FileAccessAPIView.as_view(), name='file-access'),
]
