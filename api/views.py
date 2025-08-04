from django.shortcuts import get_object_or_404

from boards.models import *

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BoardListSerializer, BoardSerializer, ThreadSerializer, ThreadDetailSerializer

class BoardListView(APIView):
    def get(self, request):
        boards = Board.objects.all()
        serializer = BoardListSerializer(boards, many=True, read_only=True)
        return Response(serializer.data)

class BoardView(APIView):
    def get(self, request, pk):
        threads = Thread.objects.filter(board__code=pk)
        serializer = BoardSerializer(threads, many=True, read_only=True)
        return Response(serializer.data)

class ThreadView(APIView):
    def get(self, request, bpk, pk):
        thread = get_object_or_404(Thread, id=pk)
        comments = Comment.objects.filter(thread=thread)

        serializer = ThreadSerializer(comments, many=True, read_only=True)
        return Response(serializer.data)

class ThreadDetailView(APIView):
    def get(self, request, bpk, pk):
        thread = get_object_or_404(Thread, id=pk)

        serializer = ThreadDetailSerializer(thread, read_only=True)
        return Response(serializer.data)
