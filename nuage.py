from httplib import HTTPSConnection
from base64 import urlsafe_b64encode
from json import loads, dumps
from pprint import pformat

class NuageHTTPError(Exception):
    
    def __init__(self, status, reason, body=""):
        self.status = status
        self.reason = reason
        self.body   = body
        
    def __str__(self):
        if self.body:
            return "%d %s\n%s" % (self.status, self.reason, self.body)
        else:
            return "%d %s" % (self.status, self.reason)
        
    def __repr__(self):
        return str(self)


class NuageResponse(object):


    def __init__(self, http_response):
        
        status, reason, body = http_response.status, http_response.reason, http_response.read()
        
        if status < 200 or status >= 300:
            raise NuageHTTPError(status, reason, body)
        
        self.count      = http_response.getheader('X-Nuage-Count', None)
        self.page       = http_response.getheader('X-Nuage-Page', None)
        self.pagesize   = http_response.getheader('X-Nuage-PageSize', None)
        self.filter     = http_response.getheader('X-Nuage-Filter', None)
        self.filter_type = http_response.getheader('X-Nuage-FilterType', None)
        self.orderby    = http_response.getheader('X-Nuage-OrderBy', None)
        
        self.status = status
        self.reason = reason
        self.body   = body
        self.obj_repr = loads(self.body) if body else []
                
        
    def __str__(self):
        return self.pretty_print()
    
    def __repr__(self):
        return self.body
    
    def obj(self):
        return self.obj_repr
    
    def pretty_print(self):
        return pformat(self.obj_repr)
    
    def id(self, name=None):
        if name:
            for dct in self.obj_repr:
                try:
                    if dct["name"] == name: return dct["ID"]
                except KeyError:
                    continue
            raise KeyError("No object with name %s" % name)
        else:
            try:
                return self.obj_repr[0]["ID"]
            except KeyError, IndexError:
                raise KeyError("No object in response.")

class NuageConnection(object):
    NUAGE_URLBASE = "/nuage/api"
    
    def __init__(self, hostname, enterprise="csp", username="csproot", password="csproot", version="v1_0", port=443):
        self._settings = locals().copy()
        self.me = None
        self._get_api_key()

    def get(self, url, filter=None, page=None, orderby=None):
        headers = {}
        if filter: headers['X-Nuage-Filter'] = filter
        if page: headers['X-Nuage-Page'] = page
        if orderby: headers['X-Nuage-OrderBy'] = orderby
        return self._do_http_request("GET", url, headers=headers)
    
   
    def post(self, url, body):
        #Convert it to a JSON string if required.
        if type(body) != str:
            body = dumps(body)
        return self._do_http_request("POST", url, body)
    
    def put(self, url, body):
        #Convert it to a JSON string if required.
        if type(body) != str:
            body = dumps(body)
        return self._do_http_request("PUT", url, body)
    
    def delete(self, url):
        return self._do_http_request("DELETE", url)
  
  
    def process_events(self, callback=None, *args, **kwargs):

        last_uuid = ""
        if not callback:
            callback = NuageConnection._default_event_callback
        
        while True:
            resp = self.get("events?uuid=%s" % last_uuid)
            last_uuid = resp.obj()["uuid"]
            callback(resp, *args, **kwargs)
      
    def _default_event_callback(self, nuage_response, *args, **kwargs):
        print "Received Push Event:"
        print "Called with args:"
        for arg in args: print arg
        for kw in kwargs: print kw
        print nuage_response        
  
    def _do_http_request(self, method, url, body=None, headers=None):
        conn = self._get_https_conn()
        request_headers = self._get_headers()
        if headers: request_headers.update(headers)
        conn.request(method, "%s/%s/%s" % (self.NUAGE_URLBASE, self._settings["version"], url), body=body, headers=request_headers)
        response = conn.getresponse()
        result = NuageResponse(response)
        conn.close()
        return result
    
    def _get_api_key(self):
        self._settings["auth_string"] = "XREST %s" % \
                                        urlsafe_b64encode("%s:%s" % (self._settings["username"], self._settings["password"]))
        self.me = self.get("me").obj()[0]
        #print self.me
        self._settings["auth_string"] = "XREST %s" % \
                                        urlsafe_b64encode("%s:%s" % (self._settings["username"], self.me["APIKey"]))
    
    def _get_https_conn(self):
        return HTTPSConnection(self._settings["hostname"], self._settings["port"],timeout=10)
    
    def _get_headers(self):
        return {
                "Content-Type" : "application/json",
                "Authorization" : self._settings["auth_string"],
                "X-Nuage-Organization" : self._settings["enterprise"]
                }
        
