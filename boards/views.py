from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required

from .models import Board, Thread, Comment, ThreadFile, CommentFile
from .forms import NewThreadForm, ThreadCommentForm

def index(request):
    boards_o = Board.objects.all()
    boards = boards_o.count()
    threads = Thread.objects.all().count()
    comments = Comment.objects.all().count()

    return render(request, 'index.html', context={'boards': boards_o, 'n_boards': boards, 'n_threads': threads, 'n_comments': comments})

@login_required
def threads(request, pk):

    threads = Thread.objects.filter(board__code=pk)

    for t in threads:
        t.files = ThreadFile.objects.filter(thread__id=t.id)
        print(t.files)

        t.comments = Comment.objects.filter(thread__id=t.id)
        for comment in t.comments:
            comment.files = CommentFile.objects.filter(comment__id=comment.id)
            print(comment.files)

    return render(request, 'boards/thread_list.html', context={'board': pk, 'threads': threads})

@login_required
@permission_required("boards.create_new_threads")
def create_new_thread(request, pk):
    board = get_object_or_404(Board, code=pk)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            nt = Thread(board=board, title=data['title'], text=data['text'], author=request.user)
            nt.save()

            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for file in request.FILES.getlist('files'):
                    if file.size > 25 * 1000 * 1000 and not request.user.has_perm("boards.upload_large_files"):
                        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'error': 'You don`t have permission to upload files larger than 25 megabytes.'})

                    f = ThreadFile(thread=nt, file=file)
                    f.save()

            return HttpResponseRedirect('/') # todo: переброс в тред
        else:
            return render(request, 'error.html', {'error': 'Неправильно введены данные!'})
    else:
        form = NewThreadForm(initial={'title': "Заголовок", 'text': "Текст"})
        return render(request, 'boards/create_new_thread.html', {'form': form})

@login_required
@permission_required("boards.comment_threads")
def add_comment_to_thread(request, pk, tpk):
    board = get_object_or_404(Board, code=pk)
    thread = get_object_or_404(Thread, id=tpk)

    e_form = ThreadCommentForm({'text': 'Введите текст...'})

    if not thread.board.code == board.code:
        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'error': 'Тред не найден на борде.'})

    if request.method == 'POST':
        form = ThreadCommentForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            nc = Comment(thread=thread, text=data['text'], author=request.user)
            nc.save()

            if request.FILES is not None and len(request.FILES.getlist('files')) > 0:
                for file in request.FILES.getlist('files'):
                    if file.size > 25 * 1000 * 1000 and not request.user.has_perm("boards.upload_large_files"):
                        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form, 'error': 'You don`t have permission to upload files larger than 25 megabytes.'})

                    f = CommentFile(comment=nc, file=file)
                    f.save()

            return HttpResponseRedirect('/') # todo: переброс в тред
    else:
        return render(request, 'boards/add_comment_to_thread.html', {'form': e_form})
