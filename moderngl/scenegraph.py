from typing import List

class NodeBase:
    def __init__(self, name : str):
        self.name = name
    
    def scribe(self) -> str:
        pass

# operators

class MinNode(NodeBase):
    def __init__(self, name : str, children : List[NodeBase]):
        super().__init__(name)
        self.children = children
    
    def scribe(self) -> str:
        if len(self.children) < 1:
            raise
        elif len(self.children) == 1:
            return self.children[0].scribe()
        else:
            ret = f"min({self.children[0].scribe()},{self.children[1].scribe()})"
            for c in self.children[2:]:
                ret = f"min({ret},{c.scribe()})"
            return ret

class SoftMinNode(NodeBase):
    def __init__(self, name : str, child1 : NodeBase, child2 : NodeBase, k : float):
        super().__init__(name)
        self.child1 = child1
        self.child2 = child2
        self.k = k
    
    def scribe(self) -> str:
        return f"smin({self.child1.scribe()},{self.child2.scribe()}, {self.k})"


class MaxNode(NodeBase):
    def __init__(self, name : str, child1 : NodeBase, child2 : NodeBase, negate : List[bool]):
        super().__init__(name)
        self.child1 = child1
        self.child2 = child2
        self.negate = negate
    
    def scribe(self) -> str:        
        return f"max({'-' if self.negate[0] else ''}{self.child1.scribe()},{'-' if self.negate[1] else ''}{self.child2.scribe()})"

# modifiers

class TranslateNode(NodeBase):
    def __init__(self, name : str, child : NodeBase, offset : tuple):
        super().__init__(name)
        self.offset = offset
        self.child = child
    
    def scribe(self) -> str:
        neg = tuple(-i for i in self.offset)
        return self.child.scribe().replace("point", f"point + vec3{neg}")

# primitives

class SphereNode(NodeBase):
    def __init__(self, name : str, radius : float):
        super(SphereNode, self).__init__(name)
        self.radius = radius
    
    def scribe(self) -> str:
        return f"sdSphere(point, {self.radius})"

class TorusNode(NodeBase):
    def __init__(self, name: str, center : tuple, normal : tuple, radii : tuple):
        super().__init__(name)
        self.center = center
        self.normal = normal
        self.radii = radii
    def scribe(self) -> str:
        return f"sdTorus(point, vec3{self.center}, vec3{self.normal}, vec3{self.radii})"

class ConeNode(NodeBase):
    def __init__(self, name: str, c : tuple, h : float):
        super().__init__(name)
        self.c = c
        self.h = h
    def scribe(self) -> str:
        return f"sdCone(point, vec2{self.c}, {self.h})"

class PlaneNode(NodeBase):
    def __init__(self, name: str, plane : tuple):
        super().__init__(name)
        self.plane = plane
    def scribe(self) -> str:
        return f"sdPlane(point, vec4{self.plane})"

class BoxNode(NodeBase):
    def __init__(self, name: str, sides : tuple):
        super().__init__(name)
        self.sides = sides
    def scribe(self) -> str:
        return f"sdBox(point, vec3{self.sides})"

# tests

from math import sqrt

children = []

children.append(TranslateNode("tx1", SphereNode("sphere", 10), (-50, 0, 0)))
children.append(TranslateNode("tx2", TorusNode("torus", (0,0,0), (0,0,-1), (10, 2,0)), (-20, 0, 0)))
children.append(ConeNode("cone", (.5, sqrt(3)/2), 10))
children.append(PlaneNode("plane", (0, 1, 0, -20)))
children.append(TranslateNode("tx5", BoxNode("box", (10,10,10)), (20, 0, 0)))

base = MinNode("min", children)

box = BoxNode("box2", (50, 2, 2))

kkk = SoftMinNode("root", base, box, 4)

box2 = BoxNode("box3", (55, 2.2, 2.2))

root = MaxNode("max", kkk , box2, [False, True])

print(root.scribe())
