import json
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.app.models.oauth2 import OAuth2AccessToken
from hichao.user.models.device import  user_identify_last_new


def check_permission(func):

    def _(self, *args, **kwargs):
        try:
            self.access_token = self.request.params.get('access_token', '')
            self.access_token = self.access_token if len(self.access_token) else self.request.headers.get('Access-Token','')
            app_from = self.request.params.get('gf', '')
            app_from = app_from if len(app_from) else self.request.headers.get('Gf','')
            app_name = self.request.params.get('gn', '')
            app_name = app_name if len(app_name) else self.request.headers.get('Gn','')
            app_version = self.request.params.get('gv', '')
            app_version = app_version if len(app_version) else self.request.headers.get('Gv','')
            app_identify = self.request.params.get('gi', '')
            app_identify = app_identify if len(app_identify) else self.request.headers.get('Gi', '')
            user_identify_last_new(app_name, app_from, app_version, app_identify)

            if self.access_token == None or self.access_token == '':
                raise KeyError
            self.user_id = OAuth2AccessToken.get_user_id(self.access_token)
            if not self.user_id or self.user_id == 'None':
                #self.error["error"] = "invalid_token"
                #self.error["errorCode"] = "21324"
                #self.error["error_code"] = "21324"
                self.user_id = -2
                #raise KeyError

        except KeyError:
            self.user_id = -1
        if self.error:
            return Response(json.dumps(self.error))
        self.user_id = int(self.user_id)
        return func(self, *args, **kwargs)
    return _



