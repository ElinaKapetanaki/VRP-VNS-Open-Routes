from solver import *

m = Model()
m.ReadDataFromFile("Instance.txt")
m.BuildModel()
s = Solver(m)
solution = s.solve()
write_to_file(solution, 'output.txt')
