#!/usr/bin/env python

import json
import base64


class VSDConnection(object):
    def __init__(self, username, password, enterprise, base_url):
        self.base_url = base_url
        self.username = username
        self.headers = {
            'Authorization' : "XREST %s" %
                              base64.urlsafe_b64encode('%s:%s' %(username, password)),
            'Content-Type' : "application/json",
            'X-Nuage-Organization' : enterprise
        }

    def _do_request(self, method, url, headers=None, params=None):
        import requests
        try:
            data = json.dumps(params) if params else None
            return requests.request(method, url, headers=headers, verify=False, timeout=2, data=data)
        except requests.exceptions.RequestException as error:
            print 'Error: Unable to connect.'
            print 'Detail: %s' % error
            raise SystemExit(1)

    def _response(self, resp):
        if resp.status_code == 401:
            print 'Error: Athentication failed. Please verify your credentials.'
            raise SystemExit(1)
        if resp.status_code < 200 or resp.status_code >= 300:
            print 'Error: %s' % resp.json()['errors'][0]['descriptions'][0]['description']
            raise SystemExit(1)
        if resp.text == '':
            return []
        return resp.json()

    def get(self, url, filter=None):
        self.authenticate()
        if filter: self.headers['X-Nuage-Filter'] = filter
        r = self._do_request('GET', self.base_url + url, headers=self.headers)
        return self._response(r)

    def post(self, url, params):
        self.authenticate()
        r = self._do_request('POST', self.base_url + url, headers=self.headers, params=params)
        return self._response(r)

    def put(self, url, params):
        self.authenticate()
        r = self._do_request('PUT', self.base_url + url, headers=self.headers, params=params)
        return self._response(r)

    def delete(self, url):
        self.authenticate()
        r = self._do_request('DELETE', self.base_url + "me", headers=self.headers)
        return self._response(r)

    def me(self):
        r = self._do_request('GET', self.base_url + "me", headers=self.headers)
        return self._response(r)

    def authenticate(self):
        import os
        import time
        data_dir = '%s/.vsd' % os.path.expanduser("~")
        APIKey_file = data_dir + '/APIKey'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        do_auth = False
    
        if os.path.exists(APIKey_file):
            with open(APIKey_file) as data_file:
                api_session = json.load(data_file)
            # replay auth if expire
            if int(api_session['APIKeyExpiry'])/1000 < time.time():
                do_auth = True
            # replay auth every 5 min
            if int(api_session['APIKeyCreation']) + 300 < time.time():
                do_auth = True
        else:
            do_auth = True

        if do_auth:
            r = self._do_request('GET', self.base_url + "me", headers=self.headers)
            rjson = self._response(r)[0]
            api_session = {'APIKey' : rjson['APIKey'],
                           'APIKeyExpiry' : rjson['APIKeyExpiry'],
                           'APIKeyCreation' : time.time()
                          }
            with open(APIKey_file, 'w') as data_file:
                json.dump(api_session, data_file)
    
        self.headers['Authorization'] = "XREST %s" % base64.urlsafe_b64encode(
                                    '%s:%s' %(self.username, api_session['APIKey']))
