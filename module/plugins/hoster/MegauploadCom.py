#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from module.plugins.Hoster import Hoster

from module.network.RequestFactory import getURL

from module.unescape import unescape

from pycurl import error

def getInfo(urls):
    url = "http://megaupload.com/mgr_linkcheck.php"
    
    ids = [x.split("=")[-1] for x in urls]
    
    i = 0
    post = {}
    for id in ids:
        post["id%i"%i] = id
        i += 1
        
    api = getURL(url, {}, post)
    api = [re.split(r"&(?!amp;|#\d+;)", x) for x in re.split(r"&?(?=id[\d]+=)", api)]
    
    result = []
    i=0
    for data in api:
        if data[0].startswith("id"):
            tmp = [x.split("=") for x in data]
            if tmp[0][1] == "0":
                status = 2
            elif tmp[0][1] == "1":
                status = 1
            elif tmp[2][1] == "3":
                status = 3
            else:
                status = 3

            name = None
            size = 0
            if status != 1:
                name = unescape(tmp[3][1])
                size = tmp[1][1]
            
            result.append( (name, size, status, urls[i] ) )
            i += 1
    
    yield result

class MegauploadCom(Hoster):
    __name__ = "MegauploadCom"
    __type__ = "hoster"
    __pattern__ = r"http://[\w\.]*?(megaupload)\.com/.*?(\?|&)d=[0-9A-Za-z]+"
    __version__ = "0.21"
    __description__ = """Megaupload.com Download Hoster"""
    __author_name__ = ("spoob")
    __author_mail__ = ("spoob@pyload.org")

    def init(self):
        self.html = [None, None]

        if not self.premium:
            self.multiDL = False
            self.chunkLimit = 1

        self.api = {}
        none, sep, self.fileID = self.pyfile.url.partition("d=")
        self.pyfile.url = "http://www.megaupload.com/?d=" + self.fileID

        
    def process(self, pyfile):
        if not self.account or not self.premium:
            self.download_html()
            self.download_api()

            if not self.file_exists():
                self.offline()

            time = self.get_wait_time()
            self.setWait(time)
            self.wait()
            
            pyfile.name = self.get_file_name()
            self.download(self.get_file_url())

            check = self.checkDownload({"limit": "Download limit exceeded"})
            if check == "limit":
                wait = self.load("http://www.megaupload.com/?c=premium&l=1")
                try:
                    wait = re.search(r"Please wait (\d+) minutes", wait).group(1)
                except:
                    wait = 1
                self.log.info(_("Megaupload: waiting %d minutes") % int(wait))
                self.setWait(int(wait)*60, True)
                self.wait()
                if not self.premium:
                    self.req.clearCookies()
                self.process(pyfile)
        else:
            self.download_api()
            pyfile.name = self.get_file_name()

            try:
                self.download(pyfile.url)
            except error, e:
                if e.args and e.args[0] == 33:
                    # undirect download and resume , not a good idea
                    page = self.load(pyfile.url)
                    self.download(re.search(r'href=\"(http://[^\"]*?)\" class=\"down_ad_butt1\">', page).group(1))
                    return 
                else:
                    raise

            check = self.checkDownload({"dllink": re.compile(r'href=\"(http://[^\"]*?)\" class=\"down_ad_butt1\">')})
            if check == "dllink":
                self.log.warning(_("You should enable direct Download in your Megaupload Account settings"))

                pyfile.size = 0
                self.download(self.lastCheck.group(1))

    def download_html(self):        
        for i in range(3):
            self.html[0] = self.load(self.pyfile.url)
            self.html[1] = self.html[0] # in case of no captcha, this already contains waiting time, etc
            count = 0
            if "The file that you're trying to download is larger than 1 GB" in self.html[0]:
                self.fail(_("You need premium to download files larger than 1 GB"))
                
            if r'Please enter the password below' in self.html[0]:
                pw = self.getPassword()
                if not pw:
                    self.fail(_("The file is password protected, enter a password and restart."))

                self.html[1] = self.load(self.pyfile.url, post={"filepassword":pw})
                break # looks like there is no captcha for pw protected files

            while "document.location='http://www.megaupload.com/?c=msg" in self.html[0]:
                # megaupload.com/?c=msg usually says: Please check back in 2 minutes,
                # so we can spare that http request
                self.setWait(120)
                if count > 1:
                    self.wantReconnect = True

                self.wait()
                
                self.html[0] = self.load(self.pyfile.url)
                count += 1
                if count > 5:
                    self.fail(_("Megaupload is currently blocking your IP. Try again later, manually."))
            
            try:
                url_captcha_html = re.search('(http://[\w\.]*?megaupload\.com/gencap.php\?.*\.gif)', self.html[0]).group(1)
            except:
                continue

            captcha = self.decryptCaptcha(url_captcha_html)
            captchacode = re.search('name="captchacode" value="(.*)"', self.html[0]).group(1)
            megavar = re.search('name="megavar" value="(.*)">', self.html[0]).group(1)
            self.html[1] = self.load(self.pyfile.url, post={"captcha": captcha, "captchacode": captchacode, "megavar": megavar})
            if re.search(r"Waiting time before each download begins", self.html[1]) is not None:
                break

    def download_api(self):

        url = "http://megaupload.com/mgr_linkcheck.php"

        id = self.pyfile.url.split("=")[-1]


        post = {"id0": id}

        api = self.load(url, {}, post)
        self.log.debug("MU API: %s" % api)
        api = [re.split(r"&(?!amp;|#\d+;)", x) for x in re.split(r"&?(?=id[\d]+=)", api)]

        for data in api:
            if data[0].startswith("id"):
                tmp = [x.split("=") for x in data]
                if tmp[0][1] == "1":
                    self.offline()

                name = unescape(tmp[3][1])
                #size = tmp[1][1]

                self.api["name"] = name
                self.pyfile.name = name


    def get_file_url(self):
        file_url_pattern = 'id="downloadlink"><a href="(.*)"\s+(?:onclick|class)="'
        search = re.search(file_url_pattern, self.html[1])
        return search.group(1).replace(" ", "%20")

    def get_file_name(self):
        if not self.api:
            file_name_pattern = 'id="downloadlink"><a href="(.*)" onclick="'
            return re.search(file_name_pattern, self.html[1]).group(1).split("/")[-1]
        else:
            return self.api["name"]

    def get_wait_time(self):
        time = re.search(r"count=(\d+);", self.html[1])
        if time:
            return time.group(1)
        else:
            return 45

    def file_exists(self):
        #self.download_html()
        if re.search(r"Unfortunately, the link you have clicked is not available.", self.html[0]) is not None or \
            re.search(r"Download limit exceeded", self.html[0]) is not None:
            return False
            
        if re.search("The file you are trying to access is temporarily unavailable", self.html[0]) is not None:
            self.setWait(120)
            self.log.debug("%s: The file is temporarily not available. Waiting 2 minutes." % self.__name__)
            self.wait()
            
            self.download_html()
            if re.search("The file you are trying to access is temporarily unavailable", self.html[0]) is not None:
                self.fail(_("Looks like the file is still not available. Retry downloading later, manually."))
            
        if re.search("The password you have entered is not correct", self.html[1]):
            self.fail(_("Wrong password for download link."))
            
        return True
