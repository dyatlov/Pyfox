import CssParser

import urllib2

response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/launchpad.css')
data = response.read()

result = CssParser.parse(data)

print result