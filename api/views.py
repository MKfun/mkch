from django.shortcuts import get_object_or_404

from boards.models import *

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http.response import JsonResponse

from rest_framework import filters

from .serializers import BoardListSerializer, BoardSerializer, ThreadSerializer, ThreadDetailSerializer, AllThreadsSerializer

from boards.models_tools import get_or_create_anon

from keyauth.decorators import KeyRequiredMixin, key_required

# Update 4.1:
# Now API is only available for users who entered key.

class BoardListView(KeyRequiredMixin, APIView):
    def get(self, request):
        serializer = BoardListSerializer(Board.objects.all(), many=True, read_only=True)
        return Response(serializer.data)

class BoardView(KeyRequiredMixin, APIView):
    def get(self, request, pk):
        b = get_object_or_404(Board, code=pk)

        threads = Thread.objects.filter(board__code=pk)
        serializer = BoardSerializer(threads, many=True, read_only=True)
        return Response(serializer.data)

class ThreadView(KeyRequiredMixin, APIView):
    def get(self, request, pk, tpk):
        b = get_object_or_404(Board, code=pk)

        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))
        comments = Comment.objects.filter(thread=thread)

        serializer = ThreadSerializer(comments, many=True, read_only=True)
        return Response(serializer.data)

class ThreadDetailView(KeyRequiredMixin, APIView):
    def get(self, request, pk, tpk):
        thread = get_object_or_404(Thread, id=tpk, board=get_object_or_404(Board, code=pk))

        serializer = ThreadDetailSerializer(thread, read_only=True)
        return Response(serializer.data)

class AllThreadsView(KeyRequiredMixin, generics.ListAPIView):
    queryset = Thread.objects.all()
    serializer_class = AllThreadsSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['id', 'creation']

class ThreadsSinceView(KeyRequiredMixin, generics.ListAPIView):
    def get_queryset(self):
        try:
            mid = int(self.request.GET.get("min_id", 0))
        except:
            mid = 0

        return Thread.objects.filter(id__gt=mid)

    serializer_class = AllThreadsSerializer

@key_required
def thread_count_view(request):
    return JsonResponse(status=200, data={'count': Thread.objects.all().count()})
