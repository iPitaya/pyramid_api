from urlparse import urljoin 
import os

image_size_dict = {
    'normal': '_wnormal',
    'small': '_small'
}

def build_image_url(prefix, str_url):
    return str_url.replace('_.webp', '')  if str_url.startswith("http://") \
        else urlparse.urljoin(prefix, remove_first_slash(str_url))

def remove_first_slash(str_url):
    return str_url[1:] if str_url.startswith(r'/')  else str_url


def resize_image_url(prefix, size, image_url):
    file_name, file_ext = os.path.splitext(image_url)
    ret = file_name+image_size_dict[size] + file_ext
    return build_image_url(prefix, ret)
    
