from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from gestor import gestor
from datetime import datetime
import time
from flask import Flask, Response
from apscheduler.schedulers.background import BackgroundScheduler

#Gerenciador de estoque

app = Flask(__name__)

class gerenciadorEstoque(object):
    __listaClientes = {}

    def __init__(self):
        self.__listaProdutos = {}
        self.__registros = {}

    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def cadastrarProdutoNovo(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        if codigo in self.__listaProdutos:
            raise ValueError('Já existe este produto. \n')
        self.__listaProdutos[codigo] = produto(nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo)

        print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + "\n")
        mensagem = nomeGestor + "cadastrou novo produto: " + nome
        user = Pyro5.api.Proxy(self.__listaClientes[nomeGestor])
        user.notificacao(mensagem)

    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def listarProdutos(self, nomeCliente):
        for produto in self.__listaProdutos.keys():
            mensagem = "Código do produto: " + produto + " Nome: " + self.__listaProdutos[produto].nome + " Quantidade: " + str(self.__listaProdutos[produto].quantidade) + " Estoque mínimo: " + self.__listaProdutos[produto].estoqueMinimo +"\n"
            user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
            user.notificacao(mensagem)

    @app.route('/produto', methods=['POST'])    
    @Pyro5.server.expose
    def retirarProduto(self,nomeCliente, codigo, qtdRetirar):
        for chave in self.__listaProdutos.keys():
            if chave == codigo:

                nova_qtd = int(int(self.__listaProdutos[chave].quantidade) - int(qtdRetirar))

                if nova_qtd >= 0:
                    if nova_qtd >= int(self.__listaProdutos[chave].estoqueMinimo):
                        self.__listaProdutos[chave].quantidade = nova_qtd

                        print("Retirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n")
                        mensagem = "Retirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n"
                        
                        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
                        user.notificacao(mensagem)
                        return 1
                    else:
                        print("Não foi possível retirar do estoque, quantidade ficará abaixo do mínimo. \n")
                        mensagem = "Não foi possível retirar do estoque, quantidade ficará abaixo do mínimo. \n"
                        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
                        user.notificacao(mensagem)
                        return 0
                else:
                    print("Não foi possível retirar do estoque, estoque insuficiente. \n")
                    mensagem = "Não foi possível retirar do estoque, estoque insuficiente. \n"
                    user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
                    user.notificacao(mensagem)
                    return 0

        print("Não foi possível retirar do estoque, produto não existe. \n")
        mensagem = "Não foi possível retirar do estoque, produto não existe. \n"
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        user.notificacao(mensagem)
        return 0
    
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def adicionarProduto(self,nomeCliente, codigo, qtdAdicionar):
        for chave in self.__listaProdutos.keys():
            if chave == codigo:
                
                nova_qtd = int(int(self.__listaProdutos[chave].quantidade) + int(qtdAdicionar))

                self.__listaProdutos[chave].quantidade = nova_qtd

                print("Adicionou " + str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " ao estoque. \n")
                mensagem = "Adicionou " + str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " ao estoque. \n"

                user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
                user.notificacao(mensagem)
                return 1
        print("Não foi possível adicionar ao estoque, produto não existe. \n")
        return 0

    @app.route('/clientes', methods=['POST'])
    @Pyro5.server.expose
    def registrarCliente(self, nomeCliente, uriCliente):
        if nomeCliente in self.__listaClientes:
            print('Cliente já cadastrado. \n')
        else:
            print("Registrou cliente " + nomeCliente + "\n")
            self.__listaClientes[nomeCliente] = uriCliente
        
        print("Lista de clientes: \n")
        for chave in self.__listaClientes.keys():
            print("Nome= " + chave + " e Uri = " + str(self.__listaClientes[chave]))

        mensagem = "Registro do cliente " + nomeCliente + " realizado com sucesso."
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        user.notificacao(mensagem)