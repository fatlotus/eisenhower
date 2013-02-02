import interstate

def main():
  closure_test = "Jeremy"
  
  def job():
    import time
    for i in xrange(0, 10):
      time.sleep(1)
      print "Hello, %s!" % closure_test
    return 42
  
  interstate.execute(job, hosts = [ 'ssh://localhost', 'ssh://jeremy@some-remote-server' ])

if __name__ == '__main__':
  main()