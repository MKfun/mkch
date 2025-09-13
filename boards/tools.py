import numpy as np
from PIL import Image

def get_client_ip(request):
    from django.conf import settings
    
    # х форвадд для запросов через прокси
    remote_addr = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for and remote_addr in getattr(settings, 'TRUSTED_PROXIES', []):
        # хватаем первый IP из списка (не уверен что работает)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = remote_addr
    
    return ip

def remove_exif(fname: str): # по факту просто копирует файл
    image = Image.open(fname)

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    image.close()

    image_without_exif.save(fname)

    image_without_exif.close()
