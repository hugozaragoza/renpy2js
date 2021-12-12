from renpy_parser.graph import Graph


def test_graph_operators():
    g = Graph(8)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(0, 3)
    g.addEdge(1, 4)
    g.addEdge(1, 5)
    g.addEdge(2, 6)
    g.addEdge(4, 6)
    g.addEdge(5, 6)
    g.addEdge(6, 7)
    g.addEdge(3, 7)

    assert g.isCyclic() == False
    assert g.countPaths(0, 7) == 4

    g.addEdge(3, 0)
    assert g.isCyclic() == True
