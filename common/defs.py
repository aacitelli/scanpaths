class Vertex:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y 
    def __str__(self):
        return "({},{})".format(self.x, self.y)

class Segment:
    def __init__(self, v1=Vertex(), v2=Vertex()):
        self.v1 = v1
        self.v2 = v2
    def __str__(self):
        return "<{}->{}>".format(self.v1, self.v2)

class BoundingBox:
    def __init__(self, tl=Vertex(), tr=Vertex(), bl=Vertex(), br=Vertex()):
        self.tl = tl 
        self.tr = tr 
        self.bl = bl 
        self.br = br 
        self.width = tl.x - tr.x
        self.height = tr.y - br.y 
    def __str__(self):
        return "<tl={},tr={},bl={},br={}>".format(self.tl, self.tr, self.bl, self.br)