from django.shortcuts import get_object_or_404

from boards.models import *

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BoardListSerializer, BoardSerializer, ThreadSerializer, ThreadDetailSerializer

from boards.models_tools import get_or_create_anon, available_boards

def has_board_access(request, pk):
    b = get_object_or_404(Board, code=pk)
    return b in available_boards(get_or_create_anon(request))

class BoardListView(APIView):
    def get(self, request):
        boards = available_boards(get_or_create_anon(request))
        serializer = BoardListSerializer(boards, many=True, read_only=True)
        print(serializer.data)
        return Response(serializer.data)

class BoardView(APIView):
    def get(self, request, pk):
        b = get_object_or_404(Board, code=pk)
        if not has_board_access(request, pk):
            return Response([])

        threads = Thread.objects.filter(board__code=pk)
        serializer = BoardSerializer(threads, many=True, read_only=True)
        return Response(serializer.data)

class ThreadView(APIView):
    def get(self, request, pk, tpk):
        b = get_object_or_404(Board, code=pk)
        if not has_board_access(request, pk):
            return Response([])

        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))
        comments = Comment.objects.filter(thread=thread)

        serializer = ThreadSerializer(comments, many=True, read_only=True)
        return Response(serializer.data)

class ThreadDetailView(APIView):
    def get(self, request, pk, tpk):
        if not has_board_access(request, pk):
            return Response([])

        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))

        serializer = ThreadDetailSerializer(thread, read_only=True)
        return Response(serializer.data)
