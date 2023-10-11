from typing import Any
from time import gmtime, strftime



class produto:
    
    codigo = 0
    nome = ""
    descricao = ""
    quantidade = 0
    precoUnidade = ""
    estoqueMinimo = 0
    acabou = 0
    estoqueBaixo = 0
    uriGestor = ""
    nomeGestor = ""
    listaInteressados = []
    timestampCadastro = ''

    def __init__(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.quantidade = quantidade
        self.precoUnidade = precoUnidade
        self.estoqueMinimo = estoqueMinimo
        self.acabou = 0
        self.estoqueBaixo = 0
        self.listaInteressados.append(uriGestor)
        self.timestampCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
        self.nomeGestor = nomeGestor
        self.uriGestor = uriGestor

    
    def getCodigoProduto(self):
        return self.codigo
    
    def getNomeProduto(self):
        return self.nome
    
    def getDescricaoProduto(self):
        return self.descricao
    
    def getQuantidadeProduto(self):
        return self.quantidade
    
    def getPrecoUnidadeProduto(self):
        return self.precoUnidade
    
    def getEstoqueMinimoProduto(self):
        return self.estoqueMinimo
    
    def getAcabouProduto(self):
        return self.acabou
    
    def getListaInteressadosProduto(self):
        return self.listaInteressados
    
    def getUriClienteProduto(self):
        return self.uriCliente
    
    def getTimestampCadastroProduto(self):
        return self.timestampCadastro
    
    def setEstoqueBaixo(self, estoqueBaixo):
        self.estoqueBaixo = estoqueBaixo

    def setQuantidadeProduto(self, quantidade):
        self.quantidade = quantidade

    def getNomeGestor(self):
        return self.nomeGestor
    
    def getUriGestor(self):
        return self.uriGestor