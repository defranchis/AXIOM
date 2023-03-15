import os
import json
import csv

from utils.logging import child_logger
log = child_logger(__name__)

# Base device class
class protocol(object):
    """
    Abstract base class for gpib devices based on pyvisa.
    
    Example:
    dev = device(address=24)
    """
    
    def __init__(self, directory, filename="protocol", metadata={}, filename_metadata="metadata", override=False):

        self.directory = directory
        self.filename = filename
        self.fieldnames = None

        self.filename_metadata = filename_metadata
        self.metadata = metadata
        
        if not os.path.isdir(directory):
            os.mkdir(directory)

        if os.path.isdir(f"{directory}/{filename_metadata}.json") and not override:
            raise IOError("An existing metadata file is found!")

        with open(f"{directory}/{filename_metadata}.json","w") as f:
            json.dump(metadata, f, indent=4)
                        
        if os.path.isdir(f"{directory}/{filename}.csv") and override:
            os.remove(f"{directory}/{filename}.csv")


    def read_metadata(self):
    
        with open(f"{self.directory}/{self.filename_metadata}.json","r") as f:
            metadata = json.load(f)
    
        self.metadata = metadata
    

    def write(self, info={}):
        if self.fieldnames is None:
            
            self.fieldnames = [n for n in info.keys()]

            with open(f"{self.directory}/{self.filename}.csv","a+", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerow(info)

        else:          
            with open(f"{self.directory}/{self.filename}.csv", "a+", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(info)
	
    def get_metadata(self):
        self.read_metadata()
        return self.metadata

    def update_pid_config(self, pid):
        self.read_metadata()

        pid.SetPoint = float(self.metadata["target_temperature"])
        pid.setKp (float(self.metadata["P"]))
        pid.setKi (float(self.metadata["I"]))
        pid.setKd (float(self.metadata["D"]))

