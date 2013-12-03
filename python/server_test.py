#!/usr/bin/python


__author__ = 'Masato Taruishi'
__copyright__ = 'Copyright 2013 Masato Taruishi'


import server
import tornado.testing
import tornado.web
import unittest
import subprocess


def _Escape(str):
  """Escapes byte string for html CDATA.

  Args:
    str: byte string

  Returns:
    Unicode object which is valid within html.  

  Raises:
    UnicodeDecodeError: Thrown when the specified byte string
                        can't be decoded.
  """
  return tornado.escape.xhtml_escape(tornado.escape.to_unicode(str))


class StubAuth:
  """Stub of auth

  This Class just return AuthId as testUser
  """

  def AuthId(self):
    return "testUser"


class StubAuthenticator:
  """Stub of authenticator

  This Class used to pass authentication forcely by test porpose.
  """

  def Authenticate(self, handler):
    return StubAuth()

  def Authenticated(self, handler, auth):
    handler.set_secure_cookie("authid", auth.AuthId())


class StubService:
  """To test back console, this object return virtual result.

  This Class may be used stub by test class.
  """

  def LsCommand(self):
    return """total 16453
drwxrwxr-x+ 134 root  admin     4556 11 26 22:58 Applications
drwxrwxr-x+   6 root  wheel      204 11  7 00:08 Incompatible Software
drwxr-xr-x+  69 root  wheel     2346 11 26 10:15 Library
drwxr-xr-x@   2 root  wheel       68  9 13 04:10 Network
drwxr-xr-x+   4 root  wheel      136 11 26 10:00 System
drwxr-xr-x    6 root  admin      204 11 26 10:03 Users
drwxrwxrwt@   4 root  admin      136 11 26 22:24 Volumes
drwxr-xr-x@  39 root  wheel     1326 11 26 10:01 bin
drwxrwxr-t@   2 root  admin       68  9 13 04:09 cores
dr-xr-xr-x    3 root  wheel     4436 11 26 22:19 dev
lrwxr-xr-x@   1 root  wheel       11 11 26 09:56 etc -> private/etc
dr-xr-xr-x    2 root  wheel        1 11 26 22:25 home
-rwxr-xr-x@   1 root  wheel  8393032  9 30 11:39 mach_kernel
dr-xr-xr-x    2 root  wheel        1 11 26 22:25 net
drwxr-xr-x@   2 root  wheel       68 11 20 11:58 opt
drwxr-xr-x@   6 root  wheel      204 11 26 10:03 private
drwxr-xr-x@  65 root  wheel     2210 11 26 10:08 sbin
lrwxr-xr-x@   1 root  wheel       11 11 26 09:56 tmp -> private/tmp
drwxr-xr-x@  11 root  wheel      374 11 26 10:08 usr
lrwxr-xr-x@   1 root  wheel       11 11 26 09:56 var -> private/var
"""

  def DfCommand(self):
    return """Filesystem      Size   Used  Avail Capacity  iused     ifree %iused  Mounted on
/dev/disk0s2   931Gi  317Gi  614Gi    35% 83058606 161007755   34%   /
devfs          188Ki  188Ki    0Bi   100%      650         0  100%   /dev
map -hosts       0Bi    0Bi    0Bi   100%        0         0  100%   /net
map auto_home    0Bi    0Bi    0Bi   100%        0         0  100%   /home
/dev/disk1s2   931Gi  310Gi  621Gi    34% 81328163 162778503   33%   /Volumes/FailSafe"""

  # Because Mac have not "free" command, so it needs implement fake method.
  def FreeCommand(self):
    return """             total       used       free     shared    buffers     cached
Mem:        616392     566840      49552          0     151448     153464
-/+ buffers/cache:     261928     354464
Swap:            0          0          0"""

  def UptimeCommand(self):
    return """ 1:21  up  3:02, 3 users, load averages: 2.59 2.54 2.66"""


APP_SETTINGS = {
  "cookie_secret": "ADA7D03B-B889-45C7-ACB9-423DDD88A725",
  "login_url": "/login",
  "xsrf_cookies": True,
}
STUB_AUTHENTICATORS = dict(authenticators=[StubAuthenticator()])


class LoginHandlerTest(tornado.testing.AsyncHTTPTestCase):
  def get_app(self):
    _auth = StubAuth()
    return tornado.web.Application(
      [
        (r'/login', server.LoginHandler)
      ],
      **APP_SETTINGS)

  def test_login_xsrf_using(self):
    self.http_client.fetch(self.get_url('/login'), self.stop)
    res = self.wait()
    self.assertTrue(res.body.find('_xsrf') >= 0)

  def test_login_fields_display(self):
    self.http_client.fetch(self.get_url('/login'), self.stop)
    res = self.wait()
    # check user input field
    self.assertTrue(res.body.find('name="user"') >= 0)
    # check user input field
    self.assertTrue(res.body.find('name="password"') >= 0)

  #def test_login_user_authenticate(self):
  #  kwargs = {
  #    "method": "POST",
  #  }
  #  self.http_client.fetch(self.get_url('/login'), self.stop, **kwargs)
  #  res = self.wait()


class LsHandlerTest(tornado.testing.AsyncHTTPTestCase):

  def get_app(self):
    return tornado.web.Application(
      [
        (r'/', server.LsHandler, STUB_AUTHENTICATORS),
        (r'/ls', server.LsHandler, STUB_AUTHENTICATORS),
      ],
      **APP_SETTINGS)

  def test_toppage_should_contain_bin(self):
    self.http_client.fetch(self.get_url('/'), self.stop)
    res = self.wait()
    self.assertTrue(res.body.find('bin') >= 0)

  def test_lspage_should_contain_bin(self):
    self.http_client.fetch(self.get_url('/ls'), self.stop)
    res = self.wait()
    self.assertTrue(res.body.find('bin') >= 0)


class DfHandlerTest(tornado.testing.AsyncHTTPTestCase):

  def get_app(self):
    return tornado.web.Application(
      [
        (r'/df', server.DfHandler, STUB_AUTHENTICATORS),
      ],
      **APP_SETTINGS)

  def test_dfpage_should_contain_disks(self):
    self.http_client.fetch(self.get_url('/df'), self.stop)
    res = self.wait()
    self.assertTrue(res.body.find('/dev/disk0s2') >= 0)
    self.assertTrue(res.body.find('devfs') >= 0)
    self.assertTrue(res.body.find('map -hosts') >= 0)
    self.assertTrue(res.body.find('map auto_home') >= 0)


class StatuszHandlerTest(tornado.testing.AsyncHTTPTestCase):

  def get_app(self):
    _stub = StubService()
    return tornado.web.Application(
      [
        (r'/statusz', server.StatuszHandler,
         dict(authenticators=[StubAuthenticator()],
              service=StubService())),
      ],
      **APP_SETTINGS)

  def test_statuszpage_should_contain_needed_result(self):
    self.http_client.fetch(self.get_url('/statusz'), self.stop)
    res = self.wait()

    #check free result
    self.assertTrue(res.body.find('-/+ buffers/cache') >= 0)

    #check uptime result
    self.assertTrue(res.body.find('users, load averages:') >= 0)

    #check df result
    self.assertTrue(res.body.find('/dev/disk0s2') >= 0)
    self.assertTrue(res.body.find('devfs') >= 0)
    self.assertTrue(res.body.find('map -hosts') >= 0)
    self.assertTrue(res.body.find('map auto_home') >= 0)


def all():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(LoginHandlerTest))
  suite.addTests(unittest.makeSuite(LsHandlerTest))
  suite.addTests(unittest.makeSuite(DfHandlerTest))
  suite.addTests(unittest.makeSuite(StatuszHandlerTest))
  return suite


if __name__ == '__main__':
  tornado.testing.main()
