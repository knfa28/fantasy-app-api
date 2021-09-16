import datetime
import hashlib
import os
import re
import requests
import sys
import time

LAG = 0    # seconds ahead of stats server
HOST = 'http://api.stats.com/v1/stats/basketball/nba/'
PUBLIC_KEY = os.environ.get('STATSPERFORM_PUBLIC_KEY', '')
SECRET_KEY = os.environ.get('STATSPERFORM_PRIVATE_KEY', '')

def get(url, args=[], stream=False):
  try:
    if args:
      params = dict(f.split('=') for f in args)
    else:
      params = {}

    params.update(get_sig())

    url = HOST + url

    return requests.get(
      url,
      params=params,
      stream=stream
    )
  except requests.Timeout:
    log.error('HTTP timeout when downloading: %s' % url)
    sys.exit(1)
  except requests.exceptions.ConnectionError as e:
    log.error('HTTP Connection Error when downloading: %s' % url)
    sys.exit(2)

def get_sig():
  timestamp = repr(int(time.time()))
  all = str.encode(PUBLIC_KEY + SECRET_KEY + timestamp)
  signature = hashlib.sha256(all).hexdigest()
  params = {
    'accept': 'xml',
    'api_key': PUBLIC_KEY,
    'sig': signature 
  }
  #print league, key, secret, signature
  return params

  #TODO: Test requests once we get access