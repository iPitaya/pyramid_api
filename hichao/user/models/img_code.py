#!/usr/bin/env python
#coding=utf-8

import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import StringIO
import hashlib
import time
from hichao.user.models.redis_sms import set_img_code_redis, get_img_code_redis

_letter_cases = "abcdefghjkmnpqrstuvwxy"
_upper_cases = _letter_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))

def create_validate_code(size=(120, 30),
                         chars=init_chars,
                         img_type="GIF",
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(0, 0, 255),
                         font_size=18,
                         font_type="ubuntu.ttf",
                         length=4,
                         draw_lines=True,
                         n_line=(1, 2),
                         draw_points=True,
                         point_chance = 2):

    width, height = size
    img  = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)
    def get_chars():
        return random.sample(chars, length)

    def create_lines():
        line_num = random.randint(*n_line)
        for i in range(line_num):
            # Æʼµã           beg
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            #½áµã           end 
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        chance = min(100, max(0, int(point_chance)))
       
        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)
       
        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)

        draw.text(((width - font_width) / 3, (height - font_height) / 3),
                    strs, font=font, fill=fg_color)
       
        return ''.join(c_chars)

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()

    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    print strs
    return img,strs
    
def get_img_code_content():
    mstream = StringIO.StringIO()
    validate_code = create_validate_code()
    img = validate_code[0]
    code = validate_code[1]
    img.save(mstream, "GIF")
    return mstream.getvalue(),code

def get_code_key(code):
    temp = time.time()
    key = hashlib.md5(str(temp)).hexdigest()
    code_key = hashlib.md5(str(key)+str(code)).hexdigest()
    set_img_code_redis(code_key,code)
    return key,code_key

def check_img_code(key,code):
    code_key = hashlib.md5(str(key)+str(code)).hexdigest()
    value = get_img_code_redis(code_key)
    if value:
        if value == code:
            return 1
    return 0

#if __name__ == "__main__":
#    #code_img = create_validate_code()
#    #code_img.save("validate.gif", "GIF")
#    
#    import StringIO
#    mstream = StringIO.StringIO()
#    validate_code = create_validate_code()
#    img = validate_code
#    img.save(mstream, "GIF")
#    print mstream.getvalue()    
#    #request.session['validate'] = validate_code[1]
#    
#    #return HttpResponse(mstream.getvalue(), "image/gif")
