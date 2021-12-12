# From https://www.geeksforgeeks.org/count-possible-paths-two-vertices/

# NOT USED YET (probably best to do path counting in the javascript app)

from collections import defaultdict


class Graph():
    def __init__(self, vertices):
        self.graph = defaultdict(list)
        self.V = vertices

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif recStack[neighbour] == True:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if visited[node] == False:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True
        return False

    # Returns count of paths from 's' to 'd'
    def countPaths(self, s, d):
        visited = [False] * self.V
        pathCount = [0]
        self.countPathsUtil(s, d, visited, pathCount)
        return pathCount[0]

    def countPathsUtil(self, u, d,
                       visited, pathCount):
        visited[u] = True
        if (u == d):
            pathCount[0] += 1
        else:
            i = 0
            while i < len(self.graph[u]):
                if (not visited[self.graph[u][i]]):
                    self.countPathsUtil(self.graph[u][i], d,
                                        visited, pathCount)
                i += 1
        visited[u] = False
