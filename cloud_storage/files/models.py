import random
import string
from os.path import basename, splitext

from django.conf import settings
from django.db import models

from users.models import User


class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    file_id = models.CharField(max_length=10, unique=True, editable=False)
    access_users = models.ManyToManyField(User, related_name='access_files')

    def save(self, *args, **kwargs):
        if not self.file_id:
            self.file_id = self.generate_file_id()

        # Получение имя файла без пути
        original_name = basename(self.file.name)
        self.file = f'uploads/{original_name}'

        # Изменение имени файла, удалив случайные символы в конце
        new_name = self.generate_unique_filename(original_name)

        # Установление значения для self.name
        self.name = new_name

        super().save(*args, **kwargs)

    def generate_unique_filename(self, original_name):
        """
        Генерация уникального имени файла, добавляя порядковый номер, если файл с таким именем уже существует.
        """
        count = 1
        base_name, ext = splitext(original_name)
        new_name = f"{base_name}{ext}"

        while UploadedFile.objects.filter(name=new_name).exists():
            count += 1
            new_name = f"{base_name} ({count}){ext}"

        return new_name

    def generate_file_id(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


class FileAccess(models.Model):
    FILE_ACCESS_TYPES = (
        ('author', 'Author'),
        ('co-author', 'Co-Author'),
    )

    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=FILE_ACCESS_TYPES)
