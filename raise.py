import os, sys, time

args = sys.argv

if __name__ == '__main__':
    print('hello world' + args[1])
    #raise RuntimeError('OBELIX threw an exception!')
    try:
        while True:
            print('hi there')
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting in the raise program now....')
        exit(5)

