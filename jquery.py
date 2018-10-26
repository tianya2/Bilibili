import json,requests
import  http.cookiejar as cookielib
from utils import singleton
class session(requests.Session):
    def __init__(self,headers={},cookie_file=None):
        requests.Session.__init__(self)
        self.cookies = cookielib.LWPCookieJar(filename=cookie_file)
        try:self.cookies.load(ignore_discard=True)
        except Exception as e:print(e,"failed load cookie_file")
        self.headers=headers
        self.auth = ('user', 'pass')
        self._type='str'
    def save(self):
        self.cookies.save()
@singleton
class http():
    def get(self,s,url,data=None):
        r=s.get(url,params=data)
        self.error(r.status_code,url)
        return self.res_data(r,s._type)
        
    def post(self,s,url,data):
        r=s.post(url,data=data)
        self.error(r.status_code,url)
        return self.res_data(r,s._type)
        
    def error(self,code,url):
        if code==200:return
        elif code==403:raise RuntimeError('403 - Forbidden '+url)
        elif code==404:raise RuntimeError('404 -  Not Found '+url)
        
    def res_data(self,r,_type):
        if _type=='json':return json.loads(r.content)
        return r.content
