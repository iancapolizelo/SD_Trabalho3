from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from gestor import gestor
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler

#Gerenciador de estoque

class gerenciadorEstoque(object):
    __listaClientes = {}

    def __init__(self):
        self.__listaProdutos = []
        self.__registros = []

    @Pyro5.server.expose 
    def cadastrarProdutoNovo(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        if codigo in self.__listaProdutos:
            raise ValueError('Já existe este produto. \n')
        self.__listaProdutos.append(produto(nomeGestor, uriGestor,codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo))
        print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + "\n")

    @Pyro5.server.expose
    def listarProdutos(self):
        for produto in self.__listaProdutos:
            print("Código: " + str(produto.getCodigoProduto()) + " Nome: " + produto.getNomeProduto() + "\n")
    
    @Pyro5.server.expose
    def getProdutos(self):
        return self.__listaProdutos

    def listarClientes(self):
        return self.__listaClientes
    
    @Pyro5.server.expose
    def retirarProduto(self, codigo, qtdRetirar):
        for produto in self.__listaProdutos:
            if produto.codigo == codigo:
                produto.setQuantidadeProduto(int(produto.quantidade) - int(qtdRetirar))
                print(produto.nomeGestor + " retirou " + qtdRetirar + " unidades do produto " + produto.nome + ". \n")
                print("Restaram " + produto.quantidade + " unidades do produto. \n")
                return 1
        return 0
    
    @Pyro5.server.expose
    def adicionarProduto(self, codigo, qtdAdicionar):
        for produto in self.__listaProdutos:
            if produto.codigo == codigo:
                produto.setQuantidadeProduto(produto.quantidade + qtdAdicionar)
                print("Adicionou " + str(qtdAdicionar) + " unidades de " + produto.getNomeProduto() + " ao estoque. \n")
                return 1
        print("Não foi possível adicionar ao estoque, produto não existe. \n")
        return 0

    @Pyro5.server.expose
    def registrarCliente(self, nome, uriCliente):
        print("Tentou Registrar Cliente " + nome)
        if nome in self.__listaClientes:
            print('Cliente já cadastrado. \n')
        else:
            print("Registrou cliente " + nome)
            self.__listaClientes[nome] = uriCliente