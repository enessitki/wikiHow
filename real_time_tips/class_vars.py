import time


class DataClass:
    def __init__(self):
        self.speed = [10]

    def get_data(self):
        return self.speed

    def get_copy_of_data(self):
        return [x for x in self.speed]


data = DataClass()
# speed = data.speed
speed = data.get_data()
# speed = data.get_copy_of_data()

while True:
    speed[0] += 1

    print(data.speed, speed)
    time.sleep(1)
