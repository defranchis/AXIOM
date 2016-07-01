from devices import *
from measurements import *


def main():
    msr = iv_scan(wafer_id="C7")
    msr.initialise()
    msr.execute()
    msr.finalise()

if __name__ == "__main__":
    main()