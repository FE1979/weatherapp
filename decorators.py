""" Funny decorators for weatherapp """

import time

""" Globals """

FUNCTIONS_CACHE = {}

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
        for i in range(pause_time):
            print(i, end=" ", flush=True)
            time.sleep(1)
        print("\n")
        res = func(*args, **kwargs)
        return res
    return wrapper

def run_time(func, *args, **kwargs):
    """ Displays run time of a function """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        res = func(*args, *kwargs)
        run_time = time.perf_counter() - start_time
        print(f'Function {func.__name__} from {func.__module__}  ran for {run_time:.5f} seconds')

        return res
    return wrapper

def show_variables(func, *args, **kwargs):
    """ Shows functions variables """
    def wrapper(*args, **kwargs):
        if args is not None:
            print(f'\nFunction {func.__name__} got positional vars:')
            for item in args:
                print(item)
        if len(kwargs) != 0:
            print("\nand keyword arguments:\n")
            for item in kwargs:
                print(item, args[item])
        print('\n')
        res = func(*args, **kwargs)
        return res
    return wrapper


def times_called(func, count = 0, *args, **kwargs):
    """ Counts function calling times """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return res
    count += 1
    print(f'Function {func.__name__} was called {count} times')

    return wrapper

def function_cache(func, count = 0, *args, **kwargs):
    """ Saves to global FUNCTIONS_CACHE result of called function """
    def wrapper(*args, **kwargs):
        res = func(*args, *kwargs)
        FUNCTIONS_CACHE[f"{func.__name__}_{count}"] = res
        return res
    return wrapper

def show_loading(func, *args, **kwargs):
    def wrapper(*args, **kwargs):
        for i in range(10):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print('\n')
        res = func(*args, **kwargs)
        return res
    return wrapper
