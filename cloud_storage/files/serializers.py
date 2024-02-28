from rest_framework import serializers

from .models import UploadedFile, FileAccess


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['user', 'file', 'file_id', 'name']
        extra_kwargs = {
            'name': {'required': False}
        }

        def create(self, validated_data):
            user = self.context['request'].user
            uploaded_file = validated_data['file']
            instance = UploadedFile(user=user, file=uploaded_file)
            instance.save()
            return instance


class FileAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAccess
        fields = ['user', 'access_type']

