'''
auth  : m4h
date  : 2017/June/08
desc  :
sensu in HA environment have to have persistent data (redis) replicated between instances.
redis HA is managed by redis sentinel and have 1 master and 2 slaves.
this script is an attempt to always keep sensu.json pointed to current redis master:
  - sn_host = sentinel host we want to query
  - sn_port = sentinel port
  - cluster_name = sentinel cluster name
  - config_path  = path to sensu.json
  - interval     = interval between probes (redis-cli) in seconds
run this script on sensu node
'''

import json
import time
import subprocess

def get_redis_master(host, port, cluster):
  '''
  query sentinel for current redis master address and port
    @host - redis sentinel host 
    @port - redis sentinel port
    @cluster - redis cluster name
    return tuple of current redis master and port
  '''
  master_host = None
  master_port = None
  args = 'redis-cli -h {0} -p {1} sentinel get-master-addr-by-name {2}'.format(host, port, cluster)
  proc = subprocess.Popen(args.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  sout,serr = proc.communicate()
  lines = sout.split('\n')
  master_host = lines[0]
  master_port = int(lines[1])
  return (master_host, master_port)

def update_sensu_config(path, host, port):
  '''
  read sensu config and update (if master changed) with current redis master host and port
    @path - path to sensu config file (file in json format)
    @host - current redis master host
    @port - current redis master port
    return True
  '''
  sensu = ''
  with open(path, 'r') as fopen:
    lines = fopen.readlines()
    sensu = json.loads(''.join(lines))
    if sensu['redis']['host'] != host or sensu['redis']['port'] != port:
      sensu['redis']['host'] = host
      sensu['redis']['port'] = port
    else:
      return False
  with open(path, 'w') as fopen:
    fopen.write(json.dumps(sensu, sort_keys=True, indent=2, separators=(',', ': ')))
  return True

def run(opts):
  '''
  watchdog run with opt.interval and update config
    @opts - static class with attributes
    do not return (run forever)
  '''
  while True:
    try:
      master_host, master_port = get_redis_master(opts.sn_host, opts.sn_port, opts.cluster_name)
      if update_sensu_config(opts.config_path, master_host, master_port):
        print '[INFO]: config {0} was updated: redis master set to {1}:{2}'.format(opts.config_path, master_host, master_port)
    except Exception as ex:
      print '[ERROR]: config {0} update failed: {1}'.format(opts.config_path, ex)
    time.sleep(opts.interval)
     
 
if __name__ == '__main__':
  #FIXME: pass args via cmd
  class opts:
    sn_host = 'localhost'
    sn_port = 26379 
    cluster_name = 'sensu'
    config_path = 'sensu.json'
    interval = 1
  run(opts)
