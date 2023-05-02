import sys
import pyscipopt
import time
#preprocessing data
#global variables
def createGraph(x,y):
      numNodes = x*y
      with open("dimacs.txt", "w") as file:
            # write amount of nodes and edges
            file.write("p edge " +  str(numNodes) + " "+ str(numNodes + x*(numNodes -x))+ "\n")
            # this will make the x graphs multiple times
            for i in range(1,numNodes+1):
                 if (i % x != 0):
                       file.write("e "+ str(i) + " " + str(i+1) + "\n")
                 else: 
                       file.write("e "+ str(i) + " " + str(i-x+1) + "\n")
            # this will make the first graph connect to all other nodes
            for i in range (1, x+1):
                  for j in range (1, numNodes-x+ 1):
                        file.write("e "+ str(i) + " " + str(j+x) + "\n")
s = int(sys.argv[1])
num = int(sys.argv[2])
if num < 2:
    print("n cannot be lower than 2!")
    sys.exit()
createGraph(s,num)
n = 0
edgeList = []
with open('dimacs.txt', 'r') as file:
    for line in file:
        words = line.split()
        if words[0] == "p":
            n =int(words[2])
        if words[0] == "e":
            node1 = int(words[1])-1
            node2 = int(words[2])-1

            if node1 < node2:
                newEdge = (node1,node2)
            else:
                newEdge = (node2,node1)
            edgeList.append(newEdge)
#solving
#create a scip model
startTime = time.time()
model = pyscipopt.Model("problem")
model.setParams({'presolving/maxrounds': 0, 'limits/time': 300})
#add decision variables
#nodes
nodes = {}
for i in range(n):
    nodes[i] = model.addVar(vtype="B", name = "node(%d)" %i)
#edges
edges = {}
for i in range(n-1):
    for j in range(i+1, n):
        edges[i,j] = model.addVar(vtype="B", name="edges(%s,%s)" % (i,j))
#objetive function
removed = pyscipopt.quicksum(nodes[i] for i in range(n))
model.setObjective(removed, sense='minimize')
#1st req
component = 0
for i in range(n-1):
    component = pyscipopt.quicksum(edges[i,j] for j in range(i+1,n))
    component +=1
    model.addCons(component - removed <= 0)
#2nd req
for i in range(n-2):
    for j in range(i+1, n-1):
        for k in range(j+1, n):
            if (i,j) in edgeList and (j,k) in edgeList and (i,k) not in edgeList:
                model.addCons(1-edges[i,j] + 1- edges[j,k] + edges[i,k] >= 1)
                model.addCons(1-edges[i,j] + 1- edges[j,k] + edges[i,k] <= 2)
                model.addCons(1-edges[i,j] + edges[i,k] <= 1)
                model.addCons(1-edges[j,k] + edges[i,k] <= 1)
#3rd req
for i in range(n-1):
    for j in range(i+1, n):
        if (i,j) in edgeList:
            model.addCons(nodes[i] + nodes[j] + edges[i,j]>=1)
            model.addCons(nodes[i] + nodes[j] + edges[i,j]<=2)
            model.addCons(nodes[i] + edges[i,j]<=1)
            model.addCons(nodes[j] + edges[i,j]<=1)
endTime = time.time()

solveStart = time.time()
model.optimize()
solveEnd = time.time()
if model.getStatus() == "optimal":
    print("Optimal solution found")
    count = 0
    for i in range(n):
        n, val = (i+1, model.getVal(nodes[i]))
        if val == 1:
            count+=1
    print("Modelling time is: ", endTime-startTime)
    print("Solving time is: ", solveEnd-solveStart)
    print("Fracture Numbers is:"+str(count))
    print("Nodes being removed: ")
    for i in range(n):
        n, val = (i+1, model.getVal(nodes[i]))
        if val == 1:
            print(str(n))
    
    # for i in range(n):
    #     print("node %d = %d" % (i, model.getVal(nodes[i])))
    #     for j in range (i+1,n):
    #         print("edge(",i+1,",",j+1,") = ", model.getVal(edges[i,j]))
else:
    print("No optimal solution found")