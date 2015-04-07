# -*- coding: utf-8 -*-

import re

from random import random

from pyload.plugin.internal.SimpleHoster import SimpleHoster


class NarodRu(SimpleHoster):
    __name    = "NarodRu"
    __type    = "hoster"
    __version = "0.12"

    __pattern = r'http://(?:www\.)?narod(\.yandex)?\.ru/(disk|start/\d+\.\w+-narod\.yandex\.ru)/(?P<ID>\d+)/.+'
    __config  = [("use_premium", "bool", "Use premium account if available", True)]

    __description = """Narod.ru hoster plugin"""
    __license     = "GPLv3"
    __authors     = [("zoidberg", "zoidberg@mujmail.cz")]


    NAME_PATTERN = r'<dt class="name">(?:<[^<]*>)*(?P<N>[^<]+)</dt>'
    SIZE_PATTERN = r'<dd class="size">(?P<S>\d[^<]*)</dd>'
    OFFLINE_PATTERN = r'<title>404</title>|Файл удален с сервиса|Закончился срок хранения файла\.'

    SIZE_REPLACEMENTS = [(u'КБ', 'KB'), (u'МБ', 'MB'), (u'ГБ', 'GB')]
    URL_REPLACEMENTS = [("narod.yandex.ru/", "narod.ru/"),
                             (r"/start/\d+\.\w+-narod\.yandex\.ru/(\d{6,15})/\w+/(\w+)", r"/disk/\1/\2")]

    CAPTCHA_PATTERN = r'<number url="(.*?)">(\w+)</number>'
    LINK_FREE_PATTERN = r'<a class="h-link" rel="yandex_bar" href="(.+?)">'


    def handleFree(self, pyfile):
        for _i in xrange(5):
            self.html = self.load('http://narod.ru/disk/getcapchaxml/?rnd=%d' % int(random() * 777))

            m = re.search(self.CAPTCHA_PATTERN, self.html)
            if m is None:
                self.error(_("Captcha"))

            post_data = {"action": "sendcapcha"}
            captcha_url, post_data['key'] = m.groups()
            post_data['rep'] = self.decryptCaptcha(captcha_url)

            self.html = self.load(pyfile.url, post=post_data, decode=True)

            m = re.search(self.LINK_FREE_PATTERN, self.html)
            if m:
                url = 'http://narod.ru' + m.group(1)
                self.correctCaptcha()
                break

            elif u'<b class="error-msg"><strong>Ошиблись?</strong>' in self.html:
                self.invalidCaptcha()

            else:
                self.error(_("Download link"))

        else:
            self.fail(_("No valid captcha code entered"))

        self.download(url)