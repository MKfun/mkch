import numpy as np
from .tools import get_client_ip
from .models import Anon, Board

def get_or_create_anon(request):
    ip = get_client_ip(request)

    try:
        anon = Anon.objects.get(ip=ip)
    except Anon.DoesNotExist:
        if 'ip' in request.session:
            anon, _ = Anon.objects.get_or_create(ip=request.session['ip'], defaults={'ip': ip, 'banned': False})
            anon.ip = ip
            anon.save()
        else:
            anon, _ = Anon.objects.get_or_create(ip=ip, defaults={'ip': ip, 'banned': False}) 
        request.session['ip'] = ip
    return anon

def available_boards(anon: Anon):
    ac = anon.permissions.all().values_list('id', flat=True)

    def my_func(i):
        document = i.permissions_required.all().values_list('id', flat=True)
        return document

    aaa = [i.pk for i in Board.objects.prefetch_related('permissions_required').all() if np.isin(my_func(i), ac).all()]
    boards = Board.objects.filter(pk__in=aaa)

    return boards
