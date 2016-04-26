# Copyright 2015 Maxime Terras <maxime.terras@numergy.com>
# Copyright 2015 Pierre Padrixe <pierre.padrixe@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import json
import base64


class VSDConnection(object):
    def __init__(self, username, password, organization,
                 base_url, debug=False, force_auth=False):
        if base_url.endswith('/'):
            self.base_url = base_url
        else:
            self.base_url = "%s/" % base_url
        self.username = username
        auth_base64 = base64.urlsafe_b64encode('%s:%s' % (username, password))
        self.headers = {
            'Authorization': "XREST %s" % auth_base64,
            'Content-Type': "application/json",
            'X-Nuage-Organization': organization
        }
        self.debug = debug
        self.force_auth = force_auth

    def _do_request(self, method, url, headers=None, params=None):
        import requests
        requests.packages.urllib3.disable_warnings()
        try:
            data = json.dumps(params) if params is not None else None
            if self.debug:
                print_headers = "# Headers:"
                for line in json.dumps(headers, indent=4).split('\n'):
                    print_headers += '\n#    %s' % line
                print '#####################################################'
                print '# Request'
                print '# Method: %s' % method
                print '# URL: %s' % url
                print print_headers
                print "# Parameters: %s" % data
                print '#####################################################'
            response = requests.request(method, url, headers=headers,
                                        verify=False, timeout=10, data=data)
        except requests.exceptions.RequestException as error:
            print 'Error: Unable to connect.'
            print 'Detail: %s' % error
            raise SystemExit(1)
        if self.debug:
            print_headers = "# Headers:"
            for line in json.dumps(dict(response.headers),
                                   indent=4).split('\n'):
                print_headers += '\n#    %s' % line
            print '# Response'
            print '# Status code: %s' % response
            print print_headers
            print '# Body: %s' % response.text
            print '#####################################################'
            print ''
        return response

    def _response(self, resp):
        if resp.status_code == 401:
            print('Error: Athentication failed. '
                  'Please verify your credentials.')
            raise SystemExit(1)
        if resp.status_code < 200 or resp.status_code >= 300:
            try:
                print('Error: %s' % resp.json()['errors'][0]
                      ['descriptions'][0]['description'])
                raise SystemExit(1)
            except ValueError:
                print 'Unknown Error: VSD returns\n%s' % resp.text
                raise SystemExit(1)
        if resp.text == '':
            return []
        return resp.json()

    def get(self, url, filter=None):
        def _next_page_is_invalid(headers):
            if ('X-Nuage-PageSize' not in headers or
                    'X-Nuage-Page' not in r.headers or
                    'X-Nuage-Count' not in r.headers):
                return True
            if (int(r.headers['X-Nuage-PageSize']) *
                    (1+int(r.headers['X-Nuage-Page'])) >=
                    int(r.headers['X-Nuage-Count'])):
                return True
            return False

        self.authenticate()
        if filter:
            self.headers['X-Nuage-Filter'] = filter
        resp = []
        self.headers['X-Nuage-Page'] = 0
        while True:
            r = self._do_request('GET', self.base_url + url,
                                 headers=self.headers)
            resp += self._response(r)
            self.headers['X-Nuage-Page'] += 1
            if _next_page_is_invalid(r.headers):
                break
        return resp

    def post(self, url, params):
        self.authenticate()
        r = self._do_request('POST', self.base_url + url,
                             headers=self.headers, params=params)
        return self._response(r)

    def put(self, url, params):
        self.authenticate()
        r = self._do_request('PUT', self.base_url + url,
                             headers=self.headers, params=params)
        return self._response(r)

    def delete(self, url):
        self.authenticate()
        r = self._do_request('DELETE', self.base_url + url,
                             headers=self.headers)
        return self._response(r)

    def me(self):
        r = self._do_request('GET', self.base_url + "me",
                             headers=self.headers)
        return self._response(r)

    def authenticate(self):
        import os
        import time
        data_dir = '%s/.vsd' % os.path.expanduser("~")
        APIKey_file = data_dir + '/APIKey'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        do_auth = False
        if os.path.exists(APIKey_file) and not self.force_auth:
            with open(APIKey_file) as data_file:
                api_session = json.load(data_file)
            # replay auth if expire
            if int(api_session['APIKeyExpiry'])/1000 < int(time.time()):
                do_auth = True
            # replay auth every 5 min
            if int(api_session['APIKeyCreation']) + 300 < int(time.time()):
                do_auth = True
        else:
            do_auth = True
        if do_auth:
            r = self._do_request('GET', self.base_url + "me",
                                 headers=self.headers)
            rjson = self._response(r)[0]
            api_session = {'APIKey': rjson['APIKey'],
                           'APIKeyExpiry': rjson['APIKeyExpiry'],
                           'APIKeyCreation': time.time()}
            with open(APIKey_file, 'w') as data_file:
                json.dump(api_session, data_file)
        auth_base64 = base64.urlsafe_b64encode(
            '%s:%s' % (self.username, api_session['APIKey']))
        self.headers['Authorization'] = "XREST %s" % auth_base64
