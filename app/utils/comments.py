# coding=utf-8

from werkzeug.routing import BaseConverter

class RegexUrl(BaseConverter):
    def __init__(self,map_url,*args):
        super(RegexUrl, self).__init__(map_url)
        self.regex = args[0]