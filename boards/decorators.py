import hashlib

from functools import wraps

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from .models import Board, Permission
from .models_tools import get_or_create_anon, available_boards

def board_permission_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        anon = get_or_create_anon(request)
        board = get_object_or_404(Board, code=kwargs['pk'])
        if board not in available_boards(anon):
            return render(request, 'error.html', {'error': 'Доступ к этой борде запрещён.'})
        return function(request, *args, **kwargs)

    return wrap

class BoardPermissionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            anon = get_or_create_anon(request)
            board = get_object_or_404(Board, code=self.kwargs['pk'])
            if board not in available_boards(anon):
                return render(request, 'error.html', {'error': 'Любопытно что тут? Напиши @botaner_1987 и попроси разрешения.'})

        return super().dispatch(request, *args, **kwargs)
