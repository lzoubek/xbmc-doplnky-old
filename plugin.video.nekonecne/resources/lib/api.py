import scraper

class Nekonecne(object):
    def __init__(self, useremail, password):
        self.url = scraper.get_login_url()
        self.user = useremail
        self.password = password
        self.isCookieValid = scraper.check_cookie(self.url, self.user, self.password)
    
    def get_useremail(self):
        return self.useremail
    
    def get_password(self):
        return self.password
    
    def check_settings(self):
        return scraper.check_settings(self.user, self.password)
    
    def is_cookie_valid(self):
        return self.is_cookie_valid
    
    def get_channels(self):
        if self.isCookieValid < 0:
            return -1
        return scraper.get_channels(self.url)
    
    def get_stream(self, url):
        return scraper.get_stream(url)