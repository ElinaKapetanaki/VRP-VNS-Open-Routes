import random
import math


class Model:

# instance variables
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1

    def ReadDataFromFile(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Parse capacity and other information
        capacity_line = lines[0].strip().split(',')
        self.capacity = int(capacity_line[1])

        # Process customer nodes
        for line in lines[5:]:
            data = line.strip().split(',')
            node_id = int(data[0])
            x_coord = int(data[1])
            y_coord = int(data[2])
            demand = float(data[3])

            node = Node(node_id, x_coord, y_coord, demand)
            self.allNodes.append(node)

            if node_id > 0:
                self.customers.append(node)

    def BuildModel(self):

        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]

                if j == 0:
                    self.matrix[i][j] = 0
                else:
                    dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                    self.matrix[i][j] = dist


class Node:
    def __init__(self, idd, xx, yy, dem):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = dem
        self.isRouted = False

class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0
