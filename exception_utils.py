import traceback, sys
import datetime


def print_exception(extraMessage=None):
    print ''
    print '-' * 70
    print 'Exception:'
    if extraMessage:
        print 'ExtraMessage: ', extraMessage
    print 'Time: ', datetime.datetime.now().strftime("%H_%M_%S_%f")
    traceback.print_exc(file=sys.stdout)
    print '-' * 70
    print ''
    #import pdb; pdb.set_trace()


def get_exception_str():
    return str(traceback.format_exc())