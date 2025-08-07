from rest_framework import serializers
from boards.models import *

class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

class BoardListSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Board
        read_only = True
        fields = '__all__'

class BoardSerializer(ReadOnlyModelSerializer):
    files = serializers.SlugRelatedField(source="threadfile_set", slug_field="file.url", many=True, read_only=True)

    class Meta:
        model = Thread
        read_only = True
        fields = ['id', 'creation', 'title', 'text', 'pinned', 'rating', 'board', 'files']

class ThreadSerializer(ReadOnlyModelSerializer):
    files = serializers.SlugRelatedField(source="commentfile_set", slug_field="file.url", many=True, read_only=True)

    class Meta:
        model = Comment
        read_only = True
        fields = ['id', 'creation', 'text', 'author', 'thread', 'files']

class ThreadDetailSerializer(ReadOnlyModelSerializer):
    files = serializers.SlugRelatedField(source="threadfile_set", slug_field="file.url", many=True, read_only=True)

    class Meta:
        model = Thread
        read_only = True
        fields = ['id', 'creation', 'title', 'text', 'board', 'files']
