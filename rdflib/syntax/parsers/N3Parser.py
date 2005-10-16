from rdflib import URIRef, BNode, Literal, RDF, Variable

from rdflib.util import from_n3

from rdflib.syntax.parsers import Parser
from rdflib.syntax.parsers.n3p.n3proc import N3Processor

from rdflib.Graph import Graph, QuotedGraph


class N3Parser(Parser):

    def __init__(self):
        pass
    
    def parse(self, source, graph):
	# we're currently being handed a Graph, not a ConjunctiveGraph
	assert graph.backend.context_aware # is this implied by formula_aware
	assert graph.backend.formula_aware

        sink = Sink(graph)
        if False: 
            sink.quantify = lambda *args: True
            sink.flatten = lambda *args: True
        baseURI = graph.absolutize(source.getSystemId() or "")
        p = N3Processor("nowhere", sink, baseURI=baseURI) # pass in "nowhere" so we can set data instead
	p.userkeys = True # bah
	p.data = source.getByteStream().read() # TODO getCharacterStream?
        p.parse()


class Sink(object):
    def __init__(self, sink): 
        self.sink = sink 
	self.identifier = sink.identifier

    def convert(self, t):
	if t.startswith("_"):
	    return BNode(unicode(t[2:]))
	elif t.startswith("<"):
	    return URIRef(unicode(t[1:-1]))
	elif t.startswith("?"):
	    return Variable(unicode(t[1:]))
	elif t.startswith('"'):
	    return from_n3(t)
	elif t.startswith('{'):
	    cid = from_n3(t[1:-1])
	    return QuotedGraph(self.sink.backend, cid)
	elif t.startswith('['):
	    cid = from_n3(t[1:-1])
	    return Graph(self.sink.backend, cid)
	else:
	    raise "NYI:", "%s %s" % (t, type(t))
	return 

    def absolutize(self, u):
        return self.sink.absolutize(u, defrag=0)

    def start(self, root): 
        self.root = self.convert(root)
	assert self.root.identifier == self.sink.identifier

    def statement(self, s, p, o, f): 
        s, p, o  = self.convert(s), self.convert(p), self.convert(o)
        c = self.convert(f)
        quoted = (c.identifier != self.root.identifier)  # TODO: should be able to do c != self.root 
        c.add((s, p, o))

    def quantify(self, formula, var): 
        #print "quantify(%s, %s)" % (formula, var)
        pass
