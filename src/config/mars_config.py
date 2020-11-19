# -*- coding:utf-8 -*-


class MarsConfig:
    url = None
    user_name = None
    password = None
    base_path = None

    def __init__(self, url, user_name, password, base_path):
        self.user_name = user_name
        self.url = url
        self.password = password
        self.base_path = base_path

    def get_auth(self):
        return {"user_name": self.user_name, 'password': self.password}

    def get_url(self):
        return self.url

    def get_base_path(self):
        return self.base_path
