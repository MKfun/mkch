from django.shortcuts import get_object_or_404

from boards.models import *

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import filters

from .serializers import BoardListSerializer, BoardSerializer, ThreadSerializer, ThreadDetailSerializer, AllThreadsSerializer

from boards.models_tools import get_or_create_anon

class BoardListView(APIView):
    def get(self, request):
        serializer = BoardListSerializer(Board.objects.all(), many=True, read_only=True)
        return Response(serializer.data)

class BoardView(APIView):
    def get(self, request, pk):
        b = get_object_or_404(Board, code=pk)

        threads = Thread.objects.filter(board__code=pk)
        serializer = BoardSerializer(threads, many=True, read_only=True)
        return Response(serializer.data)

class ThreadView(APIView):
    def get(self, request, pk, tpk):
        b = get_object_or_404(Board, code=pk)

        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))
        comments = Comment.objects.filter(thread=thread)

        serializer = ThreadSerializer(comments, many=True, read_only=True)
        return Response(serializer.data)

class ThreadDetailView(APIView):
    def get(self, request, pk, tpk):
        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))

        serializer = ThreadDetailSerializer(thread, read_only=True)
        return Response(serializer.data)

class AllThreadsView(generics.ListAPIView):
    queryset = Thread.objects.all()
    serializer_class = AllThreadsSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['id', 'creation']
