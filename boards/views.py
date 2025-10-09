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
from django.utils.html import escape
from .models import Board, Thread, Comment, ThreadFile, CommentFile, Anon, Category
from .models_tools import get_or_create_anon

from passcode.models import Passcode
from keyauth.decorators import *

from .forms import *
from pow.decorators import require_pow

from .tools import remove_exif

from passcode.models import Passcode

from datetime import timedelta
from django.utils import timezone

# Плохо реализована проверка пасскодов, в интернете DRY-решения не нашёл. Если кто знает - кидайте PR

def handler404(request, _):
    return render(request, 'not_found.html', {error: 'Мы искали по всем углам, но не нашли пост что вам нужен. Может, пост был удалён или вы ввели неправильные данные?'})

@key_required
def thread_tracker(request):
    ordb = request.GET.get('order_by', '-creation')
    ordb = ordb if ordb in settings.VALID_TRACKER_ORDER else '-creation'

    maxn = request.GET.get('max_num', 10)
    try:
        maxn = int(maxn)
        if maxn < 0:
            maxn = 0
    except:
        maxn = 10

    blur = True if request.COOKIES.get("blur-nsfw") == "1" else False

    return render(request, 'tracker.html', {'threads': Thread.objects.all().order_by(ordb)[:maxn], 'sort_method': ordb, 'max_threads': maxn, 'blur': blur})

@key_required
def index(request):
    anon = get_or_create_anon(request)

    code, _ = Passcode.objects.validate(hash_code=request.session.get('passcode'))
    code_entered = 'passcode' in request.session

    boards = Board.objects.all()

    yesterday = timezone.now().date() - timedelta(days=1)

    threads_yesterday = Thread.objects.filter(creation__date=yesterday).count()
    posts_yesterday = Comment.objects.filter(creation__date=yesterday).count()

    threads_total = Thread.objects.count()
    posts_total = Comment.objects.count()
    
    return render(request, 'index.html', context={'boards': boards, 'passcode': code, 'passcode_entered': code_entered, 'threads_yesterday': threads_yesterday, 'posts_yesterday': posts_yesterday, 'threads_total': threads_total, 'posts_total': posts_total,})

class BoardRedirectView(KeyRequiredMixin, generic.RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return f"/boards/board/{kwargs['pk']}"

class ThreadRedirectView(KeyRequiredMixin, generic.RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return f"/boards/board/{kwargs['pk']}/thread/{kwargs['tpk']}"

class ThreadListView(KeyRequiredMixin, generic.ListView):
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

class ThreadDetailView(KeyRequiredMixin, generic.DetailView):
    model = Thread

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        board = get_object_or_404(Board, code=self.kwargs['pk'])


        if 'passcode' in self.request.session:
            passcode, _ = Passcode.objects.validate(hash_code=self.request.session['passcode'])
        else:
            passcode = False

        form = ThreadCommentFormPoW(initial={"is_nsfw": board.is_nsfw}) if not passcode else ThreadCommentFormP(initial={"is_nsfw": board.is_nsfw})
        if not board.is_nsfw:
            form.fields['is_nsfw'].disabled = True

        user_posts = self.request.session.get('user_posts', [])
        replies_to_user = []
        comments = context['thread'].comment_set.all()
        for comment in comments:
            for user_post_id in user_posts:
                if f"#{user_post_id}" in comment.text:
                    replies_to_user.append(comment.id)
                    break
        context['user_posts'] = user_posts
        context['replies_to_user'] = replies_to_user

        context['passcode'] = passcode
        context['form'] = form
        context['blur'] = True if self.request.COOKIES.get("blur-nsfw") == "1" else False
        return context

    def get_object(self):
        return Thread.objects.get(id=self.kwargs['tpk'], board__code=self.kwargs['pk'])

@key_required
@require_pow
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
            form = NewThreadFormPoW(request.POST)

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
            return render(request, 'boards/create_new_thread.html', {'form': form, 'error': 'Неправильно введены данные (возможно, капча)', 'passcode': passcode})
    else:
        form = NewThreadFormPoW(initial={"is_nsfw": board.is_nsfw}) if not passcode else NewThreadFormP(initial={"is_nsfw": board.is_nsfw})
        if not board.is_nsfw:
            form.fields['is_nsfw'].disabled = True

        return render(request, 'boards/create_new_thread.html', {'form': form, 'passcode': passcode})

@key_required
@require_pow
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
            return render(request, 'error.html', {'error': 'Ваш IP-адрес был заблокирован.'})

        form = ThreadCommentFormPoW(request.POST) if not passcode else ThreadCommentFormP(request.POST)

        if form.is_valid(request): # КОСТЫЫЫЫЛЬ (ДЖАНГО НЕ ПОДДЕРЖИВАЕТ МНОГО ФАЙЛОВ ПОЭТОМУ ДЕЛАЕМ ЧЕРЕЗ КОСТЫЫЫЫЫЫЫЫЫЫЛЬ, КАК СДЕЛАЮТ ПОДДЕРЖКУ 1+ ФАЙЛА (ПО ИДЕЕ В НЕКСТ ВЕРСИИ) СКАЖИТЕ МНЕ, Я ИСПРАВЛЮ КОСТЫЫЫЫЫЫЫЫЫЛЬ)
            data = form.cleaned_data

            nc = Comment(thread=thread, text=data['text'], author=anon, is_nsfw=data["is_nsfw"], author_code=hashlib.sha256((str(thread.id) + anon.ip).encode()).hexdigest()[:6])
            nc.save()

            user_posts = request.session.get('user_posts', [])
            user_posts.append(nc.id)
            request.session['user_posts'] = user_posts

            thread.rating_pp()
            thread.save()

            if board.bump_limit > 0 and Comment.objects.filter(thread=thread).count() >= board.bump_limit:
                thread.rating = 0
                thread.save()

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

            return HttpResponseRedirect(reverse("thread_detail_view", kwargs={"pk": pk, "tpk": tpk}) + f"#comment_{nc.id}")
        else:
            return render(request, 'boards/add_comment_to_thread.html', {'form': form, 'error': 'Неправильно введены данные (возможно, капча)', 'passcode': passcode})
    else:
        nsw = thread.is_nsfw

        e_form = ThreadCommentFormPoW(initial={"is_nsfw": nsw}) if not passcode else ThreadCommentFormP(initial={"is_nsfw": nsw})
        if not nsw:
            e_form.fields['is_nsfw'].disabled = True

        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'passcode': passcode})

# КРАСНАЯ ШАПОЧКА СОСИ МОЙ ЖИРНЫЙ ЧЛЕН

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
