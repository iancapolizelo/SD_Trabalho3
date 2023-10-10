from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler

#Gerenciador de estoque

@Pyro5.behavior(instance_mode="single")
class gerenciadorEstoque(object):

    def __init__(self):
        self.__listaProdutos = []
        self.__listaClientes = []
        self.__registros = []

    @Pyro5.server.expose
    def cadastrarProdutoNovo(self, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        if codigo in self.__listaProdutos:
            raise ValueError('Já existe este produto. \n')
        self.__listaProdutos.append(produto(uriGestor,codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo))
        print("Cadastrou produto " + nome + " com código " + str(codigo) + "\n")

    @Pyro5.server.expose
    def listarProdutos(self):
        return self.__listaProdutos
    
    def listarClientes(self):
        return self.__listaClientes
    
    @Pyro5.server.expose
    def retirarProduto(self, codigo, qtdRetirar):

        for produto in self.__listaProdutos:
            if produto.getCodigoProduto() == codigo and produto.getQuantidadeProduto() >= qtdRetirar:
                if produto.getEstoqueMinimoProduto() >= produto.getQuantidadeProduto() - qtdRetirar:
                    self.__registros.append(produto.getNomeProduto() + " está com estoque baixo. \n")
                    produto.setEstoqueBaixoProduto(1)
                    produto.setQuantidadeProduto(produto.getQuantidadeProduto() - qtdRetirar)

                    #Adicionar para mandar notificação para quem é interessado

                    if produto.getQuantidadeProduto() == 0:
                        self.__listaProdutos.remove(produto)
                        produto.setAcabouProduto(1)
                return 1
        return 0
    
    @Pyro5.server.expose
    def adicionarProduto(self, codigo, qtdAdicionar):
        for produto in self.__listaProdutos:
            if produto.getCodigoProduto() == codigo:
                produto.setQuantidadeProduto(produto.getQuantidadeProduto() + qtdAdicionar)
                print("Adicionou " + str(qtdAdicionar) + " unidades de " + produto.getNomeProduto() + " ao estoque. \n")
                return 1
        print("Não foi possível adicionar ao estoque, produto não existe. \n")
        return 0

    @Pyro5.server.expose
    def registrarCliente(self, nome, uriCliente):
        if nome in self.__listaClientes:
            raise ValueError('Já existe gestor com esse nome')
        self.__listaClientes[nome] = uriCliente
        print("Registrado cliente " + nome + " com uri " + uriCliente + "\n")
