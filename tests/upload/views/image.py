#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.upload.views.image import UploadImage
from hichao.upload.views.image import CheckUpload

def callback_upload_image(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class UploadImageTests(TestCaseBase):
    view_class = UploadImage
    request_methods = {
        'img_upload_token' : {
            'params' : [
                {},
            ],
            'callback' : callback_upload_image,
        },
    }


@auto_generate_test_method
class CheckUploadTests(TestCaseBase):
    view_class = CheckUpload
    request_methods = {
        'img_upload_check' : {
            'params' : [
                {
                    'tag' : '',
                    'key' : '',
                    'category' : '',
                    'etag' : '',
                    'imageInfo' : '',
                    'fname' : '',
                    'content' : '',
                    'rotate' : '',
                },
            ],
            'callback' : callback_upload_image,
        },
    }



