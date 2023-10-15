from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from datetime import datetime
from time import gmtime, strftime
from flask import Flask, Response
from apscheduler.schedulers.background import BackgroundScheduler

#Gerenciador de estoque

app = Flask(__name__)

class gerenciadorEstoque(object):
    __listaClientes = {}

    def __init__(self):
        self.__listaProdutos = {}
        self.__registros = {}

    #Método para cadastrar novos produtos no estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def cadastrarProdutoNovo(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):
        if codigo in self.__listaProdutos:
            print(nomeGestor + 'tentou cadastradar produto que já existe. \n')
            mensagem = 'Produto já existe. \n'
            user = Pyro5.api.Proxy(self.__listaClientes[nomeGestor])
            user.notificacao(mensagem)
            return 1
    
        self.__listaProdutos[codigo] = produto(nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo)

        print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + " no estoque.\n")
        mensagem = "Novo produto cadastrado com sucesso"
        user = Pyro5.api.Proxy(self.__listaClientes[nomeGestor])
        user.notificacao(mensagem)
        return 0

    #Método para listar todos os produtos cadastrados no estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def listarProdutos(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "Lista de produtos: \n"

        for produto in self.__listaProdutos.keys():
            horaCad = self.__listaProdutos[produto].registrosMovimentacao['Cadastro']
            mensagem = "Código do produto: " + produto + " Nome: " + self.__listaProdutos[produto].nome + " Quantidade: " + str(self.__listaProdutos[produto].quantidade) + " Estoque mínimo: " + self.__listaProdutos[produto].estoqueMinimo + " Cadastrado em: " + horaCad +"\n"
            user.notificacao(mensagem)


    #Método para retirar produtos do estoque
    @app.route('/produto', methods=['POST'])    
    @Pyro5.server.expose
    def retirarProduto(self,nomeCliente, codigo, qtdRetirar):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])

        for chave in self.__listaProdutos.keys(): #Verifica se o produto existe
            if chave == codigo:

                nova_qtd = int(int(self.__listaProdutos[chave].quantidade) - int(qtdRetirar))
                horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

                if nova_qtd >= 0: #Verifica se o estoque é suficiente
                    if nova_qtd >= int(self.__listaProdutos[chave].estoqueMinimo): #Verifica se o estoque ficará acima do mínimo
                        self.__listaProdutos[chave].quantidade = nova_qtd
                        self.__listaProdutos[chave].registrosMovimentacao['Retirada'] = horarioEvento

                        print("Retirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n")
                        mensagem = "Retirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n"
                        user.notificacao(mensagem)
                        return 1
                    else:

                        if nova_qtd == 0: #Verifica se o estoque acabou
                            self.__listaProdutos[chave].quantidade = nova_qtd
                            self.__listaProdutos[chave].acabou = 1
                            self.__listaProdutos[chave].estoqueBaixo = 1
                            self.__listaProdutos[chave].registrosMovimentacao['Acabou'] = horarioEvento

                            print("Produto +" + self.__listaProdutos[chave].nome + " acabou. \n")
                            mensagem = "Você retirou todo o estoque do produto: " + self.__listaProdutos[chave].nome + "\n"
                            user.notificacao(mensagem)
                            return 1
                        else: #Verifica se o estoque ficará abaixo do mínimo
                            self.__listaProdutos[chave].quantidade = nova_qtd
                            self.__listaProdutos[chave].estoqueBaixo = 1
                            self.__listaProdutos[chave].registrosMovimentacao['Abaixo do mínimo'] = horarioEvento

                            print("Estoque de " + self.__listaProdutos[chave].nome + " está abaixo do mínimo. \n")
                            mensagem = "Você retirou " + str(qtdRetirar) + " unidades do produto: " + self.__listaProdutos[chave].nome + " e o estoque está abaixo do mínimo. \n"
                            user.notificacao(mensagem)
                            return 1
                else:
                    print("Não foi possível retirar do estoque, estoque insuficiente. \n")
                    mensagem = "Não foi possível retirar do estoque, estoque insuficiente. \n"
                    user.notificacao(mensagem)
                    return 0

        mensagem = "Produto não existe. \n"
        user.notificacao(mensagem)
        return 0
    
    #Método para quantidade de produtos já existentes ao estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def adicionarProduto(self,nomeCliente, codigo, qtdAdicionar):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

        for chave in self.__listaProdutos.keys(): 
            if chave == codigo: #Verifica se o produto existe
                
                nova_qtd = int(int(self.__listaProdutos[chave].quantidade) + int(qtdAdicionar))
                self.__listaProdutos[chave].quantidade = nova_qtd
                self.__listaProdutos[chave].registrosMovimentacao['Adicionou'] = horarioEvento

                print("Adicionou " + str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " ao estoque. \n")
                mensagem = "Adicionou " + str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " ao estoque. \n"
                user.notificacao(mensagem)
                return 1
            
        print("Não foi possível adicionar ao estoque, produto não existe. \n")
        return 0

    #Método para registrar um novo gestor
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

        mensagem = "Registro do gestor " + nomeCliente + " realizado com sucesso."
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        user.notificacao(mensagem)

    #Método para gerar relatório de produtos que acabaram
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosEstoque(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "Relatório de produtos em estoque: \n"
        user.notificacao(mensagem)

        for produto in self.__listaProdutos.keys():
                
            mensagem = "Código do produto: " + produto
            user.notificacao(mensagem)

            mensagem = "Nome: " + self.__listaProdutos[produto].nome
            user.notificacao(mensagem)

            mensagem = "Quantidade: " + str(self.__listaProdutos[produto].quantidade)
            user.notificacao(mensagem)

            mensagem = "Estoque mínimo: " + str(self.__listaProdutos[produto].estoqueMinimo)
            user.notificacao(mensagem)

            mensagem = "Registros: "
            user.notificacao(mensagem)

            for registro in self.__listaProdutos[produto].registrosMovimentacao.keys():
                mensagem = "  " + registro + " - " + self.__listaProdutos[produto].registrosMovimentacao[registro]
                user.notificacao(mensagem)

            mensagem = "\n"
            user.notificacao(mensagem)