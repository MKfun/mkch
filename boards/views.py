import hashlib

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required
from django.views import generic
from django.urls import reverse

from .models import Board, Thread, Comment, ThreadFile, CommentFile, Anon
from .forms import NewThreadForm, ThreadCommentForm

from .tools import get_client_ip

from keyauth.decorators import key_required, KeyRequiredMixin

@key_required
def index(request):
    boards = Board.objects.all()
    return render(request, 'index.html', context={'boards': boards})

class ThreadListView(KeyRequiredMixin, generic.ListView):
    model = Thread
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(board__code=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(ThreadListView, self).get_context_data(**kwargs)
        context["board"] = get_object_or_404(Board, code=self.kwargs['pk'])
        return context

class ThreadDetailView(KeyRequiredMixin, generic.DetailView):
    model = Thread

@key_required
def create_new_thread(request, pk):
    board = get_object_or_404(Board, code=pk)

    if request.method == 'POST':
        ip = get_client_ip(request)
        anon, _ = Anon.objects.get_or_create(ip=ip, defaults={'ip': ip, 'code': hashlib.sha256(ip.encode("utf-8")).hexdigest()[:6], 'banned': False})
        if anon.banned:
            return render(request, 'error.html', {'error': 'Ваш IP-адрес был заблокирован. Только попробуй впн включить сука.'})

        form = NewThreadForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            nt = Thread(board=board, title=data['title'], text=data['text'], author=anon)

            threads = Thread.objects.filter(board__code=board.code)
            if not board.thread_limit == 0 and threads.count() > board.thread_limit:
                earliest = threads.earliest('id')
                earliest.delete()
                earliest.save()

            nt.save()

            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for file in request.FILES.getlist('files'):
                    if file.size > 25 * 1000 * 1000 and not request.user.has_perm("boards.upload_large_files"):
                        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'error': 'You don`t have permission to upload files larger than 25 megabytes.'})

                    f = ThreadFile(thread=nt, file=file)
                    f.save()

            return HttpResponseRedirect(reverse("board", kwargs={"pk": pk}))
        else:
            return render(request, 'error.html', {'error': 'Неправильно введены данные!'})
    else:
        form = NewThreadForm(initial={'title': "Заголовок", 'text': "Текст"})
        return render(request, 'boards/create_new_thread.html', {'form': form})

@key_required
def add_comment_to_thread(request, pk, tpk):
    board = get_object_or_404(Board, code=pk)
    thread = get_object_or_404(Thread, id=tpk)

    e_form = ThreadCommentForm({'text': 'Введите текст...'})

    if not thread.board.code == board.code:
        return render(request, 'error.html', {'error': 'Тред не найден на борде.'})

    if request.method == 'POST':
        ip = get_client_ip(request)
        anon, _ = Anon.objects.get_or_create(ip=ip, defaults={'ip': ip, 'code': hashlib.sha256(ip.encode("utf-8")).hexdigest()[:6], 'banned': False})
        if anon.banned:
            return render(request, 'error.html', {'error': 'Ваш IP-адрес был заблокирован. Только попробуй впн включить сука.'})

        form = ThreadCommentForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            nc = Comment(thread=thread, text=data['text'], author=anon)
            nc.save()

            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for file in request.FILES.getlist('files'):
                    if file.size > 25 * 1000 * 1000 and not request.user.has_perm("boards.upload_large_files"):
                        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'error': 'You don`t have permission to upload files larger than 25 megabytes.'})

                    f = CommentFile(comment=nc, file=file)
                    f.save()

            return HttpResponseRedirect(reverse("thread_detail_view", kwargs={"bpk": pk, "pk": tpk}))
        else:
            return render(request, 'error.html', {'error': "Неправильно введена капча!"})
    else:
        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form})
