from rest_framework import serializers
from boards.models import *

class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

class BoardSerializer(ReadOnlyModelSerializer):
    files = serializers.SlugRelatedField(source="threadfile_set", slug_field="file.url", many=True, read_only=True)

    class Meta:
        model = Thread
        read_only = True
        fields = ['id', 'creation', 'title', 'text', 'author', 'board', 'files']

class ThreadSerializer(ReadOnlyModelSerializer):
    files = serializers.SlugRelatedField(source="commentfile_set", slug_field="file.url", many=True, read_only=True)

    class Meta:
        model = Comment
        read_only = True
        fields = ['id', 'creation', 'text', 'author', 'thread', 'files']
