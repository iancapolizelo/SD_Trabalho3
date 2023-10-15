from typing import Any
from time import gmtime, strftime



class produto:
    
    codigo = 0
    nome = ""
    descricao = ""
    quantidade = 0
    precoUnidade = ""
    estoqueMinimo = 0
    estoqueBaixo = 0
    acabou = 0
    uriGestorCriador = ""
    nomeGestorCriador = ""
    listaInteressados = {}

    def __init__(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.quantidade = quantidade
        self.precoUnidade = precoUnidade
        self.estoqueMinimo = estoqueMinimo
        self.acabou = 0
        self.estoqueBaixo = 0
        self.listaInteressados[nomeGestor] = uriGestor
        self.timestampCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
        self.nomeGestorCriador = nomeGestor
        self.uriGestorCriador = uriGestor

    
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
    
    def getEstoqueBaixoProduto(self):
        return self.estoqueBaixo
    
    def getUriGestorCriadorProduto(self):
        return self.uriGestorCriador
    
    def getNomeGestorCriadorProduto(self):
        return self.nomeGestorCriador
    
    def getListaInteressadosProduto(self):
        return self.listaInteressados
    
    def getRegistrosMovimentacaoProduto(self):
        return self.registrosMovimentacao
    