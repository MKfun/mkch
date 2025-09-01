import hashlib
import numpy as np

import requests
import json

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.db.models import F
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views import generic
from django.urls import reverse
from django.conf import settings

from .models import Board, Thread, Comment, ThreadFile, CommentFile, Anon, Category
from .models_tools import get_or_create_anon, available_boards

from passcode.models import Passcode

from .forms import *

from .tools import remove_exif

from passcode.models import Passcode

from .decorators import board_permission_required, BoardPermissionRequiredMixin

# Плохо реализована проверка пасскодов, в интернете DRY-решения не нашёл. Если кто знает - кидайте PR

def handler404(request, _):
    return render(request, 'not_found.html', {error: 'Мы искали по всем углам, но не нашли пост что вам нужен. Может, пост был удалён или вы ввели неправильные данные?'})

def index(request):
    anon = get_or_create_anon(request)

    boards = available_boards(anon)

    code, _ = Passcode.objects.validate(hash_code=request.session.get('passcode'))
    code_entered = 'passcode' in request.session

    return render(request, 'index.html', context={'boards': boards, 'passcode': code, 'passcode_entered': code_entered})

class ThreadListView(BoardPermissionRequiredMixin, generic.ListView):
    model = Thread
    paginate_by = 9

    def get_queryset(self):
        q = super().get_queryset().filter(board__code=self.kwargs['pk']).order_by("-pinned", "-rating")

        title = self.request.GET.get("title")
        if title:
            q = q.filter(title__icontains=title)

        return q

    def get_context_data(self, **kwargs):
        context = super(ThreadListView, self).get_context_data(**kwargs)
        context["board"] = get_object_or_404(Board, code=self.kwargs['pk'])
        context["blur"] = True if self.request.COOKIES.get("blur-nsfw") == "1" else False

        return context

class ThreadDetailView(BoardPermissionRequiredMixin, generic.DetailView):
    model = Thread

    def get_object(self):
        return Thread.objects.get(id=self.kwargs['tpk'], board__code=self.kwargs['pk'])

@board_permission_required
def create_new_thread(request, pk):
    board = get_object_or_404(Board, code=pk)
    if (not board.enable_posting and (request.user.is_anonymous or not request.user.is_staff)) or board.lockdown:
        return render(request, 'error.html', {'error': 'Борда назначена рид-онли.'})

    if 'passcode' in request.session:
        passcode, _ = Passcode.objects.validate(hash_code=request.session['passcode'])
    else:
        passcode = False

    if request.method == 'POST':
        anon = get_or_create_anon(request)
        if anon.banned:
            return render(request, 'error.html', {'error': 'Ваш IP-адрес был заблокирован. Только попробуй впн включить сука.'})

        if passcode:
            form = NewThreadFormP(request.POST)
        else:
            form = NewThreadForm(request.POST)

        if form.is_valid(request): # КОСТЫЫЫЫЛЬ (ДЖАНГО НЕ ПОДДЕРЖИВАЕТ МНОГО ФАЙЛОВ ПОЭТОМУ ДЕЛАЕМ ЧЕРЕЗ КОСТЫЫЫЫЫЫЫЫЫЫЛЬ, КАК СДЕЛАЮТ ПОДДЕРЖКУ 1+ ФАЙЛА (ПО ИДЕЕ В НЕКСТ ВЕРСИИ) СКАЖИТЕ МНЕ, Я ИСПРАВЛЮ КОСТЫЫЫЫЫЫЫЫЫЛЬ)
            data = form.cleaned_data

            nt = Thread(board=board, title=data['title'], text=data['text'], author=anon, is_nsfw=(data['is_nsfw']))
            nt.save()

            threads = Thread.objects.filter(board__code=board.code)
            if not board.thread_limit <= 0 and threads.count() > board.thread_limit:
                earliest = threads.earliest('id')
                earliest.delete()

            furls = []
            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for file in request.FILES.getlist('files'):
                    f = ThreadFile(thread=nt, file=file)
                    f.save()

                    if f.fclass() == "photo" and not f.type() == "gif":
                        remove_exif(f.file.path)

                    furls.append(f.file.url)

            if settings.MKBOT and settings.MKBOT_ADDR:
                data = {'board': board.code, 'is_nsfw': nt.is_nsfw, 'id': nt.id, 'title': nt.title, 'text': nt.text, 'files': furls}
                ans = requests.post(settings.MKBOT_ADDR + "/newthread", data=json.dumps(data))

            return HttpResponseRedirect(reverse("board", kwargs={"pk": pk}))
        else:
            return render(request, 'boards/create_new_thread.html', {'form': form, 'error': 'Неправильно введены данные (возможно, каптча)'})
    else:
        form = NewThreadForm(initial={"is_nsfw": board.is_nsfw}) if not passcode else NewThreadFormP(initial={"is_nsfw": board.is_nsfw})
        if not board.is_nsfw:
            form.fields['is_nsfw'].disabled = True

        return render(request, 'boards/create_new_thread.html', {'form': form})

@board_permission_required
def add_comment_to_thread(request, pk, tpk):
    board = get_object_or_404(Board, code=pk)
    if (not board.enable_posting and (request.user.is_anonymous or not request.user.is_staff)) or board.lockdown:
        return render(request, 'error.html', {'error': 'Борда назначена рид-онли.'})

    thread = get_object_or_404(Thread, id=tpk)
    if not thread.board.code == board.code:
        return render(request, 'error.html', {'error': 'Тред не найден на борде.'})

    if 'passcode' in request.session:
        passcode, _ = Passcode.objects.validate(hash_code=request.session['passcode'])
    else:
        passcode = False

    if request.method == 'POST':
        anon = get_or_create_anon(request)

        if anon.banned:
            return render(request, 'error.html', {'error': 'Ваш IP-адрес был заблокирован. Только попробуй впн включить сука.'})

        form = ThreadCommentForm(request.POST) if not passcode else ThreadCommentFormP(request.POST)

        if form.is_valid(request): # КОСТЫЫЫЫЛЬ (ДЖАНГО НЕ ПОДДЕРЖИВАЕТ МНОГО ФАЙЛОВ ПОЭТОМУ ДЕЛАЕМ ЧЕРЕЗ КОСТЫЫЫЫЫЫЫЫЫЫЛЬ, КАК СДЕЛАЮТ ПОДДЕРЖКУ 1+ ФАЙЛА (ПО ИДЕЕ В НЕКСТ ВЕРСИИ) СКАЖИТЕ МНЕ, Я ИСПРАВЛЮ КОСТЫЫЫЫЫЫЫЫЫЛЬ)
            data = form.cleaned_data

            nc = Comment(thread=thread, text=data['text'], author=anon, author_code=hashlib.sha256((str(thread.id) + anon.ip).encode()).hexdigest()[:6])
            nc.save()

            thread.rating_pp()
            thread.save()

            if board.bump_limit > 0 and Comment.objects.filter(thread=thread).count() >= board.bump_limit:
                thread.delete()
                return HttpResponseRedirect(reverse("board", kwargs={"pk": board.code}))

            furls = []
            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for fi in request.FILES.getlist('files'):
                    f = CommentFile(comment=nc, file=fi)
                    f.save()

                    if f.fclass() == "photo" and not f.type() == "gif":
                        remove_exif(f.file.path)

                    furls.append(f.file.url)

            if settings.MKBOT and settings.MKBOT_ADDR:
                data = {'thread': thread.id, 'thread_title': thread.title, 'board': board.code, 'is_nsfw': nc.is_nsfw, 'id': nc.id, 'text': nc.text, 'files': furls}
                ans = requests.post(settings.MKBOT_ADDR + "/newcomment", data=json.dumps(data))

            return HttpResponseRedirect(reverse("thread_detail_view", kwargs={"pk": pk, "tpk": tpk}))
        else:
            return render(request, 'boards/create_new_thread.html', {'form': form, 'error': 'Неправильно введены данные (возможно, каптча)'})
    else:
        nsw = thread.is_nsfw

        e_form = ThreadCommentForm(initial={"is_nsfw": nsw}) if not passcode else ThreadCommentFormP(initial={"is_nsfw": nsw})
        if not nsw:
            e_form.fields['is_nsfw'].disabled = True

        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form})

@staff_member_required
def pin_toggle(request):
    if request.method == "POST":
        b = json.loads(request.body)

        thr = get_object_or_404(Thread, id=b['id'])

        thr.pinned = not thr.pinned
        thr.save()

        return HttpResponseRedirect(b['next'] if 'next' in b else reverse("board", kwargs={"pk": thr.board.code}))
    else:
        return HttpResponseRedirect('/')

@staff_member_required
def lockdown_all(request):
    if request.method == "POST":
        b = json.loads(request.body)
        a = True if b['lock'] == 1 else False
        Board.objects.all().update(lockdown=a)
        return HttpResponseRedirect(b["next"] if "next" in b else '/')
    else:
        return HttpResponseRedirect('/')
