from typing import List

class NodeBase:
    def __init__(self, name : str):
        self.name = name
    
    def scribe(self) -> str:
        pass

class MinNode(NodeBase):
    def __init__(self, name : str, children : List[NodeBase]):
        super(MinNode, self).__init__(name)
        self.children = children
    
    def scribe(self) -> str:
        if len(self.children) == 1:
            return self.children[0].scribe()
        elif len(self.children) > 1:
            ret = f"min({self.children[0].scribe()},{self.children[1].scribe()})"
            for c in self.children[2:]:
                ret = f"min({ret},{c.scribe()})"
            return ret

class SoftMinNode(NodeBase):
    def __init__(self, name : str, child1 : NodeBase, child2 : NodeBase, k : float):
        super(SoftMinNode, self).__init__(name)
        self.child1 = child1
        self.child2 = child2
        self.k = k
    
    def scribe(self) -> str:
        return f"smin({self.child1.scribe()},{self.child2.scribe()}, {self.k})"

class SphereNode(NodeBase):
    def __init__(self, name : str, radius : float):
        super(SphereNode, self).__init__(name)
        self.radius = radius
    
    def scribe(self) -> str:
        return f"sdSphere(point, {self.radius})"

class TanslateNode(NodeBase):
    def __init__(self, name : str, child : NodeBase, offset : tuple):
        super(TanslateNode, self).__init__(name)
        self.offset = offset
        self.child = child
    
    def scribe(self) -> str:
        return self.child.scribe().replace("point", f"point + vec3{self.offset}")

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
        return f"sdCone(point, vec2{self.c}, {self.h}"

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

children = [SphereNode(f"sphere{i}", i* 1.0) for i in range(3)]
children.extend([
    SoftMinNode("smin1", SphereNode("sp1", 2), SphereNode("sp2", 4), .1),
    SoftMinNode("smin2", SphereNode("sp3", 4), SphereNode("sp4", 2), .2),
    ])

children.append(
    TanslateNode( "tx1",
        SoftMinNode("smin3", SphereNode("sp10", 2), SphereNode("sp20", 4), .1),
        (1,2,3)
    )
)

children.append(TanslateNode("tx2", SphereNode("sp100", 2), (7,8,9)))

import random


random.shuffle(children)
root = MinNode("root", children)

print(root.scribe())
