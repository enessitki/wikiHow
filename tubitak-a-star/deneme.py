class Node:
    def __init__(self, x, y, cost, parent_index):
        self.x = x  # index of grid
        self.y = y  # index of grid
        self.cost = cost
        self.parent_index = parent_index

n1 = Node(x=1,y=1,cost=10, parent_index=1)
n2 = Node(x=2,y=2,cost=200, parent_index=2)
n3 = Node(x=3,y=3,cost=3, parent_index=3)
n4 = Node(x=4,y=4,cost=40, parent_index=4)

open_set = dict()

open_set[(100,100)] = n1
open_set[(200,200)] = n2
open_set[(300,300)] = n3
open_set[(400,400)] = n4

c_id = min(open_set, key=lambda o: open_set[o].cost + 45)

print(c_id)