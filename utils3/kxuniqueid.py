
def uniqueid_generator(start=1, step=1):
    import time
    seconds = int(time.time())
    seconds = seconds << 16

    low     = start
    while True:
        yield seconds | low
        low += step


if __name__ == '__main__':
    g = uniqueid_generator()
    for i in range(10):
        print g.next()
