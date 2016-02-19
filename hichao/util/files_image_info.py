# -*- coding:utf-8 -*-

from icehole_client.files_client import get_filename, get_image_filename

class ImageMsg():
    def __init__(self,img):
        self.filename = img.filename
        self.width = img.width
        self.height = img.height

def get_filename_new(ns,filename):
    return get_filename(ns,filename)

def get_image_filename_new(ns,filename):
    img = get_image_filename(ns,filename)
    img_msg = ImageMsg(img)
    return img_msg

