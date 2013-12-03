#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example server to show the files in your root directory.
# 
#  1. Runs this server and checks whether it shows the contents of
#     your root directory:
#
#      $ python server.py --port=<port>
#      $ w3m http://localhost:<port>/ # from a different console
#
#  2. Runs the test and checks whether the test passes:
#
#      $ python server_test.py 
#
#        <snip>
# 
#      OK
#      [I 130605 12:35:16 testing:436] PASS
#
#  3. Reads the tornado document and this code to check how it works:
#
#      $ w3m http://www.tornadoweb.org/en/stable/
#      $ w3m http://www.tornadoweb.org/en/branch2.1/web.html
#
#  4. Use pydoc and take a look at the document and checks how
#     inline comments are genearted as user's documentation:
#
#      $ pydoc server
#      $ pydoc server.LsHandler
#
# Homework:
#
#   1. Adds a new handler called 'DfHandler' to show the output of 'df'
#      and make it accessible at http://localhost:12345/df. In addition,
#      adds the appropriate testcase for it in server_test.py. When
#      you write your code, please follow the coding style defined
#      below. Also, use the following command to see what assertions
#      are available in your testcase:
#
#       $ pydoc tornado.testing.AsyncHTTPTestCase
#
#   2. Creates a new handler called 'StatuszHandler' to show useful
#      information in your real admin work and make it accessible at
#      http://localhost:12345/statusz.
#
#   3. Creates a fake stub for command execution and write a test
#      for /bin/ls failures in LsHandlerTest.
#
#   4. Creates setup.py and generates your package. Nice to have
#      your script and library separeted.
#
#   5. Adds authentication and authorization layer.
#
# Coding style:
#
# - Each definition in top level should be separated by 2 empty lines.
# - Each line should not exceed 80 columns.
# - Comments by '#' are for code readers.
# - Comments by '"""', or docstring, are both for users and readers.
# - Functions which starts with '_' doesn't appear in pydoc so you can
#   define private functions.
# - Use "'" for string literal except that it contains "'".
# - All public methods/function should have docstring.
# - Starts with capital case when you put '.' at the end.
# - Describes who is the first author and copyright holder.
# - import libraries to use should be ordered in alpabetical order.
# - 2 spaces for structual indent and 4 spaces for line-wrap
# - Method/Function name starts with capital case.
# - If your method/functions accepts argument, then you should write it
#   in your docstring. Return value and expected exceptions should be
#   mentioned as well.
# - Considers code readers to make it easy to understand.
# - Tests do not have to follow the above policies but better to follow.
#


"""
simple web server to show the system information

This is a simple web server to execute several command line tools
and show the output for your browser.

The easiest way to use this module to run this module directly by:

 python server.py

This listens the port 12345 and handles http requests. Go to:

 http://localhost:12345/

to see the server output.
"""


__author__ = 'Masato Taruishi'
__copyright__ = 'Copyright 2013 Masato Taruishi'


from tornado.options import define, options

import subprocess
import sys
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import urllib


define('port', default=12345, help='port to listen', metavar='PORT')


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


class Auth:

  def __init__(self, authid):
    self.authid = authid

  def AuthId(self):
    return self.authid


class Authenticator:

  def Authenticate(self, handler):
    return None

  def Authenticated(self, handler, auth):
    return None


class SessionAuthenticator(Authenticator):

  def Authenticate(self, handler):
    authid = handler.get_secure_cookie("authid")
    if authid:
      return Auth(authid)
    return None

  def Authenticated(self, handler, auth):
    handler.set_secure_cookie("authid", auth.authid)


class PasswordAuthenticator(Authenticator):

  _PASSDB = {
      'user1': 'passw0rd'
  }

  def Authenticate(self, handler):
    user = handler.get_argument("user","")
    password = handler.get_argument("password","")
    if self.__class__._PASSDB.has_key(user):
      if self.__class__._PASSDB[user] == password:
        return Auth(user)
    return None


class Service:
  """Set of utilities to show system information.

  This class provides a set of utilities to show system information.
  These system information are escaped in html CDATA so that you
  can easily put the information as html contents.

  >>> service = Services()
  >>> service.LsCommand()
  """
  def _ExecCommand(self, cmd):
    p = subprocess.Popen(
        'LANG=ja_JP.UTF-8 ' + cmd, shell=True, stdout=subprocess.PIPE)
    buf = ('<pre>%s</pre>' % _Escape(p.stdout.read()))
    p.wait()
    return buf

  def LsCommand(self):
    return self._ExecCommand('ls -l /')

  def DfCommand(self):
    return self._ExecCommand('df -h')

  def FreeCommand(self):
    return self._ExecCommand('free')

  def UptimeCommand(self):
    return self._ExecCommand('uptime')


class BaseHandler(tornado.web.RequestHandler):
  """Base Handler

  This handler is Base Class for tornado.web.RequestHandler.
  If you need authentication on handler, extend BaseHandler.

  Default setting using two different authenticate.
  1. Session authenticate
    Check cookie information.
  2. Password authenticate
    Check user ID and password.
    If you passed authenticate, create cookie.
  """

  def initialize(self, service=None, authenticators=None):
    """Initializes the handler."""
    if service:
      self.service = service
    else:
      self.service = Service()

    if authenticators:
      self._authenticators = authenticators
    else :
      self._authenticators = [SessionAuthenticator(), PasswordAuthenticator()]

  def get_current_user(self):
    auth = self._IsAuthenticated()
    if auth:
      return auth.AuthId()
    else :
      return None

  def _IsAuthenticated(self):
    for authenticator in self._authenticators:
      auth = authenticator.Authenticate(self)
      if auth:
        self._Authenticated(auth)
        return auth
    return None

  def _Authenticated(self, auth):
    for authenticator in self._authenticators:
      authenticator.Authenticated(self, auth)


class LoginHandler(BaseHandler):
  def get(self):
    self.render(
    "login.html",
    next=self.get_argument("next","/"),
    error=self.get_argument("error",False)
    )

  def post(self):
    auth = self._IsAuthenticated()
    if auth:
      self.redirect(self.get_argument("next", "/"))
    else :
      params = urllib.urlencode({
      "error": "Login incorrect",
      "next": self.get_argument("next", "/")
      })
      self.redirect("/login?" + params)


class LogoutHandler(BaseHandler):
  def get(self):
    self.clear_cookie("user")
    self.redirect("/login")


class LsHandler(BaseHandler):
  """Shows the output of '/bin/ls'.

  This handler accepts GET requests and send the output of
  '/bin/ls -l /'

  The typical use case is as follows:

  >>> app = tornado.web.Application([(r'/', LsHandler)])
  >>> app.listen(12345)
  >>> tornado.ioloop.IOLoop.instance().start()
  """

  @tornado.web.authenticated
  def get(self):
    """Handles GET requests.

    This handles http GET requests and sends the files in your
    root directory in the simple http format as follows:

    <pre>
    ...
    </pre>
    """
    self.write(self.service.LsCommand())


class DfHandler(BaseHandler):
  """Shows the output of '/bin/df -h'.

  This handler accepts GET requests and send the output of
  '/bin/df -h'

  The typical use case is as follows:

  >>> app = tornado.web.Application([(r'/df', DfHandler)])
  >>> app.listen(12345)
  >>> tornado.ioloop.IOLoop.instance().start()
  """

  @tornado.web.authenticated
  def get(self):
    """Handles GET requests.

    This handles http GET requests and sends the files in your
    root directory in the simple http format as follows:

    <pre>
    ...
    </pre>
    """
    self.write(self.service.DfCommand())


class StatuszHandler(BaseHandler):
  """Shows the output of system status.

  This handler accepts GET requests and send the output of
  '/usr/bin/free'
  '/usr/bin/uptime'
  '/bin/df -h'

  The typical use case is as follows:

  >>> app = tornado.web.Application([(r'/statusz', StatuszHandler)])
  >>> app.listen(12345)
  >>> tornado.ioloop.IOLoop.instance().start()
  """

  @tornado.web.authenticated
  def get(self):
    """Handles GET requests.

    This handles http GET requests and sends the files in your
    root directory in the simple http format as follows:

    <pre>
    ...
    </pre>
    """
    #output free
    self.write('<h2>Memory</h2>')
    self.write(self.service.FreeCommand())

    #output uptime
    self.write('<h2>Uptime</h2>')
    self.write(self.service.UptimeCommand())

    #output df
    self.write('<h2>Disk usage</h2>')
    self.write(self.service.DfCommand())

def main(args):
  """Starts the server.

  This runs the web server of this module at the port '12345' as
  well as parsing command line options. You can use --port option
  to change the port to listen.

  >>> import server
  >>> server.main(['server.py', '--help'])

  Args
    args : list of command line arguments.
  """
  tornado.options.parse_command_line(args)
  settings = {
    "cookie_secret": "ADA7D03B-B889-45C7-ACB9-423DDD88A725",
    "login_url": "/login",
    "xsrf_cookies": True,
  }
  app = tornado.web.Application(
      [
          (r'/', LsHandler),
          (r'/ls', LsHandler),
          (r'/login', LoginHandler),
          (r'/logout', LogoutHandler),
          (r'/df', DfHandler),
          (r'/statusz', StatuszHandler),
      ], **settings)
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
  main(sys.argv)
