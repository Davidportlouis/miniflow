import numpy as np

class Node(object):
    def __init__(self,inbound_nodes=[]):
        # node properties
        # node(s) from which current node receives values
        self.inbound_nodes = inbound_nodes
        # node(s) to which current node passes value
        self.outbound_nodes = []
        # for each inbound_node add current node(self) as outbound node
        for node in self.inbound_nodes:
            node.outbound_nodes.append(self)
        # value of current node
        self.value = None
        # gradients of current node
        self.gradients = {}
        
    def forward(self):
        """
        must be implemented in all subclasses
        """
        raise NotImplementedError

    def backward(self):
        """
        must be implemented in all subclasses 
        """
        raise NotImplementedError

class Input(Node):
    def __init__(self):
        # An input Node has no inbound nodes
        # so no need to pass anything to Node class instantiator
        Node.__init__(self)

    # NOTE: Input node is the only node where the value
    # may be passed as an argument to forward().
    #
    # All other node implementations should get the value
    # of the previous node from self.inbound_nodes
    #
    # Example:
    # val0 = self.inbound_nodes[0].value

    def forward(self):
        pass

    def backward(self):
        self.gradients = {"self":0}
        for n in self.outbound_nodes:
            grad_cost = n.gradients[self]
            self.gradients[self] += grad_cost * 1

    

## simple mathematical operations
class Add(Node):
    def __init__(self,*inputs):
        Node.__init__(self,inputs)

    def forward(self):
        self.value = 0
        for i in range(len(self.inbound_nodes)):
            self.value += self.inbound_nodes[i].value

class Mul(Node):
    def __init__(self,*inputs):
        Node.__init__(self,inputs)

    def forward(self):
        self.value = 1
        for i in range(len(self.inbound_nodes)):
            self.value *= self.inbound_nodes[i].value

class Linear(Node):
    def __init__(self,inputs,weights,bias):
        Node.__init__(self,[inputs,weights,bias])

    def forward(self):
        self.value = np.dot(self.inbound_nodes[0].value,self.inbound_nodes[1].value) + self.inbound_nodes[2].value

class Sigmoid(Node):
    def __init__(self,node):
        Node.__init__(self,[node])

    def sigmoid(self,z):
        return 1.0/(1 + np.exp(-z))

    def forward(self):
        self.value = self.sigmoid(self.inbound_nodes[0].value)


class MSE(Node):
    def __init__(self,y,a):
        Node.__init__(self,[y,a])

    def forward(self):
        y = self.inbound_nodes[0].value.reshape(-1,1)
        a = self.inbound_nodes[1].value.reshape(-1,1)
        self.value = np.sum((y-a)**2)/len(y)



def topological_sort(feed_dict):
    """
    used to resolve dependencies and sort the nodes of graph in 
    sequence of process to be done.
    """
    input_nodes = [n for n in feed_dict.keys()]

    G = {}
    nodes = [n for n in input_nodes]
    while len(nodes) > 0:
        n = nodes.pop(0)
        if n not in G:
            G[n] = {"in":set(),"out":set()}
        for m in n.outbound_nodes:
            if m not in G:
                G[m] = {"in":set(),"out":set()}
            G[n]["out"].add(m)
            G[m]["in"].add(n)
            nodes.append(m)

    L = []
    S = set(input_nodes)
    while len(S) > 0:
        n = S.pop()

        if isinstance(n,Input):
            n.value = feed_dict[n]
        L.append(n)

        for m in n.outbound_nodes:
            G[n]["out"].remove(m)
            G[m]["in"].remove(n)
            if(len(G[m]["in"])) == 0:
                S.add(m)

    return L

def forward_and_backward(graph):

    """
    Performs a forward pass and backward pass through a list 
    of sorted nodes
    """

    for n in graph:
        n.forward()

    for n in graph[::-1]:
        n.backward()

