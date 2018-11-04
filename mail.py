import urllib2
import re
import sys
import cookielib
from threading import Timer
from multiprocessing import Process, Queue
 
class GetResults(Process): 
    def __init__(self, rezqueue):
        Process.__init__(self)
        self.rezqueue = rezqueue
   
    def run(self):
        while True:
            email = self.rezqueue.get()
            if email is None:   return False
            with open("emails.txt","a") as EmailFile:
                EmailFile.write(email.rstrip()+"\n")
            print email
 
class Crawler(Process): 
    def __init__(self, queue, rezqueue):
        Process.__init__(self)
        self.queue = queue
        self.rezqueue = rezqueue
   
    def run(self):
        while True:
            site = self.queue.get()
            if site is None:    return False
            self.crawl(site)
         
    def crawl(self,site):
        try:
            WatchIt = Timer(15.0, self.WatchDog)
            WatchIt.start()
 
            cj = cookielib.CookieJar()        
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('Accept:','*'),("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:31.0) Gecko/20100101 Firefox/31.0")]
            opener.addheaders = [('Content-Type', 'text/html; charset=utf-8'),("Accept-Encoding", "")]
            resp = opener.open(site,timeout=10)
            WatchIt.cancel()
            self.getem(resp.read())         
        except Exception, e:
            #print e
            f = 1
             
    def getem(self,resp):
        try:
            emails = re.findall(r"[A-Za-z0-9%&*+?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&*+?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[a-z0-9-]*[A-Za-z0-9])?\.)+(?:[A-Za-z]{2}|com|org|net|edu|gov|mil|biz|info|mobi|name|aer  o|asia|jobs|museum)\b", str(resp))
            CleanEmails = set(emails)
            for em in CleanEmails:
                self.rezqueue.put(em.lower())
        except Exception, e:
            return False
 
    def WatchDog(self):
        return False           
              
 
             
if __name__ == "__main__":
 
    if len(sys.argv) < 3:
        print "Usage:",sys.argv[0],"Threads DomainFile.txt"
        print "\tExample: ",sys.argv[0],"30 domains.txt"
        sys.exit()
 
    queue = Queue(maxsize=30000)
    rezqueue = Queue()
    ThreadNumber = int(sys.argv[1])
    ThreadList = []
 
    for i in range(ThreadNumber):
        t = Crawler(queue,rezqueue)
        t.daemon = True
        t.start()
        ThreadList.append(t)
         
    GR = GetResults(rezqueue)
    GR.daemon = True
    GR.start()
     
    with open(sys.argv[2],"rU") as urls:
        for url in urls:
            try:
                if url.startswith('http://'):
                    queue.put(url.rstrip())
                else:
                    url = 'http://'+url.rstrip()
                    queue.put(url.rstrip())
            except Exception, e:
                print e
                 
    for i in range(ThreadNumber):
        queue.put(None)
              
    for Worker in ThreadList:
        Worker.join()
         
    GR.join()
