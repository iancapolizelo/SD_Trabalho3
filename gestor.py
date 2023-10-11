from __future__ import print_function
import Pyro5.api
import Pyro5.server

class gestor(object):

    def __init__(self, nome, uriGestor):
        self.nome = nome
        self.uri = uriGestor

    def getNome(self):
        return self.nome
    
    def getUri(self):
        return self.uri