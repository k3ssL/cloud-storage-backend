import random
import string
from os.path import basename, splitext

from django.conf import settings
from django.db import models


class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    file_id = models.CharField(max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.file_id:
            self.file_id = self.generate_file_id()

        # Получите имя файла без пути
        original_name = basename(self.file.name)
        self.file = f'uploads/{original_name}'

        # Измените имя файла, удалив случайные символы в конце
        new_name = self.generate_unique_filename(original_name)

        # Установите значение для self.name
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
