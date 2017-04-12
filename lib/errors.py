# -*- coding: utf-8 -*-


class Error(Exception):
    pass


class WebSiteError(Error):

    def __init__(self, title='Acestream Sports', message='Se ha producido un error', time=5000):

        self.title = title
        self.message = message
        self.time = time
