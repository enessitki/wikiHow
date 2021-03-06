import threading
import time


def doit(arg):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print("working on %s" % arg)

    print("Stopping as you wish.")


def main():
    t = threading.Thread(target=doit, args=("task",))
    t.start()
    # t.join()
    time.sleep(5)
    t.do_run = False
    # t.join()

if __name__ == "__main__":
    main()