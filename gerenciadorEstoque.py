from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from datetime import datetime
from time import gmtime, strftime
from flask import Flask, Response
from apscheduler.schedulers.background import BackgroundScheduler
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

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
            print('\n' + nomeGestor + ' tentou cadastradar produto que já existe. \n')
            mensagem = '\nProduto já existe. \n'
            user = Pyro5.api.Proxy(self.__listaClientes[nomeGestor])
            user.notificacao(mensagem)
            return 1
    
        self.__listaProdutos[codigo] = produto(nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo)

        print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + " no estoque.\n")
        horaCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
        evento = "produto " + codigo + " cadastrado"
        self.__registros[horaCadastro] = evento

        mensagem = "\nNovo produto cadastrado com sucesso"
        user = Pyro5.api.Proxy(self.__listaClientes[nomeGestor])
        user.notificacao(mensagem)
        return 0

    #Método para listar todos os produtos cadastrados no estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def listarProdutos(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nLista de produtos: \n"

        for produto in self.__listaProdutos.keys():
            mensagem = "Código do produto: " + produto + " Nome: " + self.__listaProdutos[produto].nome + " Quantidade: " + str(self.__listaProdutos[produto].quantidade) + " Estoque mínimo: " + self.__listaProdutos[produto].estoqueMinimo +"\n"
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

                        evento = "retirado " + str(qtdRetirar) + " unidades do produto " + self.__listaProdutos[chave].codigo + " do estoque"
                        self.__registros[horarioEvento] = evento

                        print("\nRetirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n")
                        mensagem = "\nRetirou " + str(qtdRetirar) + " unidades de " + self.__listaProdutos[chave].nome + " do estoque. \n"
                        user.notificacao(mensagem)
                        return 1
                    else:

                        if nova_qtd == 0: #Verifica se o estoque acabou
                            self.__listaProdutos[chave].quantidade = nova_qtd
                            self.__listaProdutos[chave].acabou = 1
                            self.__listaProdutos[chave].estoqueBaixo = 1

                            evento = "retirado " + qtdRetirar + " unidades do produto " + codigo + " e ele ACABOU"
                            self.__registros[horarioEvento] = evento

                            print("\nProduto " + self.__listaProdutos[chave].nome + " acabou. \n")
                            mensagem = "\nVocê retirou todo o estoque do produto: " + self.__listaProdutos[chave].nome + "\n"
                            user.notificacao(mensagem)

                            mensagem = "\nProduto: " + self.__listaProdutos[chave].nome + " ACABOU.\n"
                            userGestor = Pyro5.api.Proxy(self.__listaProdutos[chave].uriGestorCriador)
                            userGestor.notificacao(mensagem)

                            return 1
                        else: #Verifica se o estoque ficará abaixo do mínimo
                            self.__listaProdutos[chave].quantidade = nova_qtd
                            self.__listaProdutos[chave].estoqueBaixo = 1

                            evento = "retirado " + qtdRetirar + " unidades do produto " + codigo + " e ele está ABAIXO DO MÍNIMO" 
                            self.__registros[horarioEvento] = evento

                            print("\nEstoque de " + self.__listaProdutos[chave].nome + " está abaixo do mínimo. \n")
                            mensagem = "\nVocê retirou " + str(qtdRetirar) + " unidades do produto: " + self.__listaProdutos[chave].nome + "\n"
                            user.notificacao(mensagem)

                            mensagem = "\nProduto: " + self.__listaProdutos[chave].nome + " ABAIXO DO ESTOQUE MÍNIMO.\n"
                            userGestor = Pyro5.api.Proxy(self.__listaProdutos[chave].uriGestorCriador)
                            userGestor.notificacao(mensagem)

                            return 1
                else:
                    print("\nNão foi possível retirar do estoque, estoque insuficiente. \n")
                    mensagem = "\nNão foi possível retirar do estoque, estoque insuficiente. \n"
                    user.notificacao(mensagem)
                    return 0

        mensagem = "\nProduto não existe. \n"
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
                
                evento = "adicionado " + str(qtdAdicionar) + " unidades do produto " + codigo + " ao estoque"
                self.__registros[horarioEvento] = evento

                if self.__listaProdutos[chave].acabou == 1:
                    self.__listaProdutos[chave].acabou = 0

                    evento = "produto " + codigo + " voltou ao estoque"
                    horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                    self.__registros[horaVoltou] = evento

                if self.__listaProdutos[chave].estoqueBaixo == 1 and nova_qtd >= int(self.__listaProdutos[chave].estoqueMinimo):
                    self.__listaProdutos[chave].estoqueBaixo = 0

                    evento = "estoque do produto " + codigo + " voltou ao normal"
                    horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                    self.__registros[horaVoltou] = evento


                print("\nAdicionou " + str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " ao estoque. \n")
                
                
                mensagem = '\n'+str(qtdAdicionar) + " unidades de " + self.__listaProdutos[chave].nome + " foram adicionadas ao estoque. \n"
                userGestor = Pyro5.api.Proxy(self.__listaProdutos[chave].uriGestorCriador)
                userGestor.notificacao(mensagem)
                user.notificacao(mensagem)
            
                return 1

            
        print("\nNão foi possível adicionar ao estoque, produto não existe. \n")
        return 0

    #Método para registrar um novo gestor
    @app.route('/clientes', methods=['POST'])
    @Pyro5.server.expose
    def registrarCliente(self, nomeCliente, uriCliente):
        if nomeCliente in self.__listaClientes:
            print('\nCliente já cadastrado. \n')
        else:
            print("\nRegistrou cliente " + nomeCliente + "\n")
            self.__listaClientes[nomeCliente] = uriCliente
        
        print("Lista de clientes: \n")
        for chave in self.__listaClientes.keys():
            print("Nome= " + chave + " e Uri = " + str(self.__listaClientes[chave]))

        mensagem = "\nRegistro do gestor " + nomeCliente + " realizado com sucesso. \n"
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        user.notificacao(mensagem)

    #Método para gerar relatório de produtos que acabaram
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosEstoque(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nRelatório de produtos em estoque: \n"
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

            regProcura = "produto " + self.__listaProdutos[produto].codigo

            for registro in self.__registros.keys():
                if regProcura in  self.__registros[registro]:
                    mensagem = "  " + registro + " - " + self.__registros[registro]
                    user.notificacao(mensagem)
                
            mensagem = "\n"
            user.notificacao(mensagem)

    #Método para gerar relatório de registros
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioRegistros(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nRelatório de registros: \n"
        user.notificacao(mensagem)

        for registro in self.__registros.keys():
            mensagem = registro + " - " + self.__registros[registro]
            user.notificacao(mensagem)

    #Método para gerar relatório de produtos que acabaram
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosAcabaram(self, nomeCliente):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nRelatório de produtos que acabaram: \n"
        user.notificacao(mensagem)

        for produto in self.__listaProdutos.keys():
            if self.__listaProdutos[produto].acabou == 1:
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

                regProcura = "produto " + self.__listaProdutos[produto].codigo

                for registro in self.__registros.keys():
                    if regProcura in  self.__registros[registro]:
                        mensagem = "  " + registro + " - " + self.__registros[registro]
                        user.notificacao(mensagem)
                
                mensagem = "\n"
                user.notificacao(mensagem)
    
    #Método para gerar relatório de fluxo de movimentação por período
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioFluxoMovimentacao(self, nomeCliente, dataInicio, dataFim):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nRelatório de fluxo de movimentação: \n"
        user.notificacao(mensagem)

        for registro in self.__registros.keys():
            if dataInicio <= registro <= dataFim:
                mensagem = registro + " - " + self.__registros[registro]
                user.notificacao(mensagem)

    #Método para gerar relatório de produtos sem saída por período
    """
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosSemSaida(self, nomeCliente, dataInicio, dataFim):
        user = Pyro5.api.Proxy(self.__listaClientes[nomeCliente])
        mensagem = "\nRelatório de produtos sem saída: \n"
        user.notificacao(mensagem)

        for produto in self.__listaProdutos.keys():
            codigoProd = "produto " + self.__listaProdutos[produto].codigo
            retirada = "retirado "
            for registro in self.__registros.keys():
                if dataInicio <= registro <= dataFim:
                    if retirada in self.__registros[registro]:
                        break
                    else:
                        if codigoProd in self.__registros[registro]:
                            mensagem = "Produto " + self.__listaProdutos[produto].nome + " teve saída no período. \n"
                            user.notificacao(mensagem)
    """