import os
import time
import getpass
import socket
import glob
import logging


def mkdir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class measurement(object):
    """ Abstract measurement class. """
    
    def __init__(self, wafer_id="", logdir=""):
        self.wafer_id = wafer_id
        self.wafer_type = "HPK128"
        
        ## Create wafer directory
        self.wafdir = "logs/%s" % (self.wafer_id)
        mkdir(self.wafdir)
        
        ## Create log directory
        self.nrun = self.get_run_id(self.wafer_id)
        self.logdir = "logs/%s/%s" % (self.wafer_id, self.nrun)
        mkdir(self.logdir)
        
        ## Set log file
        self.logfile = '%s/log.txt' % (self.logdir)

        ## Create logger and formater
        logFormatter = logging.Formatter(fmt="[%(asctime)s] [%(levelname)-5.5s]  %(message)s", datefmt='%H:%M:%S')
        self.logging = logging.getLogger('root')
        self.logging.setLevel(logging.DEBUG)

        ## Add logging to console
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.logging.addHandler(consoleHandler)
    
        ## Add logging to file
        fileHandler = logging.FileHandler(filename=self.logfile)
        fileHandler.setFormatter(logFormatter)
        self.logging.addHandler(fileHandler)     
    
    def get_time(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def get_date_time(self):
        return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    
    def get_user_name(self):
        return getpass.getuser()

    def get_host_name(self):
        return socket.gethostname()
    
    def get_run_id(self, die_name):
        id_list = [-1]
        for dname in glob.glob("logs/%s/*" % die_name):
            name = os.path.basename(dname)
            if len(name.split("_")) == 3:
                i = int(name.split("_")[0])
                id_list.append(i)
        new_id = max(id_list) + 1
        now = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        run_id = "%02d_%s" % (new_id, now)
        return run_id



    # Prepare
    # ---------------------------------
    
    def _initialise(self):
        self.logging.info("Start date          : %s" % self.get_date_time())
        self.logging.info("User                : %s" % self.get_user_name())
        self.logging.info("Host                : %s" % self.get_host_name())
        self.logging.info("Wafer ID            : %s" % self.wafer_id)
        self.logging.info("Wafer Type          : %s" % self.wafer_type)
        self.logging.info("Log will be stored to %s" % self.logfile)
        self.logging.info("\n")
        
    def _finalise(self):
        print 'common finalisation not implemented yet'
        
        
        
    