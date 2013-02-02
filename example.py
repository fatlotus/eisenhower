import interstate

def main():
  closure_test = "Jeremy"
  
  def job(environ):
    import time
    for i in xrange(0, 10):
      time.sleep(1)
      print "%s | Hello, %s!" % (environ['current_host'], closure_test)
    return 42
  
  interstate.execute(job, hosts = [ 'ssh://localhost', 'ssh://jeremy@some-remote-server' ])

if __name__ == '__main__':
  main()