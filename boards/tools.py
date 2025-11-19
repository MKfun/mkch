from PIL import Image

import secrets
import os

def get_client_ip(request):
    print(request)
    print(type(request))

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def remove_exif(fname: str): # по факту просто копирует файл
    image = Image.open(fname)

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    image.close()

    image_without_exif.save(fname)

    image_without_exif.close()

def generate_anonymous_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    random_name = secrets.token_urlsafe(32)
    return f"{random_name}{ext}"

def anonymous_file_upload_to(instance, filename):
    return f"uploads/{generate_anonymous_filename(filename)}"
