import time

def spin():
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

