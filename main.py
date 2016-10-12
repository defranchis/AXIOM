from devices import *
from measurements import *

def main():
    msr = iv_scan(wafer_id="1007")
    msr.initialise()
    msr.execute()
    msr.finalise()

if __name__ == "__main__":
    main()

 