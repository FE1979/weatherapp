""" Funny decorators for weatherapp """

import time

def pause_moment(func, *args, **kwargs):
    """ Pause for 1 second """
    def wrapper(*args, **kwargs):
        print('One moment, please...\n')
        time.sleep(1)
        res = func(*args, **kwargs)
        return res
    return wrapper

def pause(func, *args, **kwargs):
    """ Pause for user defined time in seconds """
    def wrapper(*args, **kwargs):
        pause_time = int(input("Enter time in second to pause\n"))
        time.sleep(pause_time)
        res = func(*args, **kwargs)
        return res
    return wrapper
