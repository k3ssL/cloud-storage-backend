from rest_framework import serializers

from .models import UploadedFile


class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['user', 'file', 'file_id', 'name']

        def create(self, validated_data):
            user = self.context['request'].user
            print(user)
            uploaded_file = validated_data['file']
            instance = UploadedFile(user=user, file=uploaded_file)
            instance.save()
            return instance

        def update(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].required = True  # Делаем поле 'name' обязательным при обновлении