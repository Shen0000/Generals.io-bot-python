from init_game import general
import time

if __name__ == '__main__':
    time.sleep(1)
    general._get_stats()
    for msg in general.get_updates():
        pass