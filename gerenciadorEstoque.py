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

#Retorno = 0 quando deu certo, 1 quando deu errado

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
            return "\nProduto já existe.\n"
    
        self.__listaProdutos[codigo] = produto(nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo)

        print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + " no estoque.\n")
        horaCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
        evento = "produto " + codigo + " cadastrado"
        self.__registros[horaCadastro] = evento

        return "\nProduto cadastrado com SUCESSO.\n"

    #Método para listar todos os produtos cadastrados no estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def listarProdutos(self):
        retorno = ''
        
        mensagem = "\nLista de produtos: \n"
        retorno += mensagem

        for produto in self.__listaProdutos.keys():
            mensagem = "Código do produto: " + produto + " Nome: " + self.__listaProdutos[produto].nome + " Quantidade: " + str(self.__listaProdutos[produto].quantidade) + " Estoque mínimo: " + self.__listaProdutos[produto].estoqueMinimo +"\n"
            retorno += mensagem

        return retorno


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
                        return "\nRetirado com SUCESSO.\n"
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

                            return "\nRetirado com SUCESSO.\n"
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

                            return "\nRetirado com SUCESSO.\n"
                else:
                    print("\nNão foi possível retirar do estoque, estoque insuficiente. \n")
                    return "\nEstoque insuficiente.\n"

        return "\nProduto não existe.\n"
    
    #Método para quantidade de produtos já existentes ao estoque
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def adicionarProduto(self, codigo, qtdAdicionar):

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
            
                return "\nUnidades adicionadas com SUCESSO.\n"

            
        print("\nNão foi possível adicionar ao estoque, produto não existe. \n")
        return "\nProduto não existe.\n"

    #Método para registrar um novo gestor
    @app.route('/clientes', methods=['POST'])
    @Pyro5.server.expose
    def registrarCliente(self, nomeCliente, uriCliente):
        if nomeCliente in self.__listaClientes:
            print('\nCliente já cadastrado. \n')

            return "\nCliente já cadastrado.\n"
        else:
            print("\nRegistrou cliente " + nomeCliente + "\n")
            self.__listaClientes[nomeCliente] = uriCliente
        
        print("Lista de clientes: \n")
        for chave in self.__listaClientes.keys():
            print("Nome= " + chave + " e Uri = " + str(self.__listaClientes[chave]))

        return "\nCliente cadastrado com SUCESSO.\n"

    #Método para gerar relatório de produtos que acabaram
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosEstoque(self):

        retorno = ''

        mensagem = "\nRelatório de produtos em estoque: \n\n"
        retorno += mensagem

        for produto in self.__listaProdutos.keys():
                
            mensagem = "Código do produto: " + produto + "\n"
            retorno += mensagem

            mensagem = "Nome: " + self.__listaProdutos[produto].nome + "\n"
            retorno += mensagem

            mensagem = "Quantidade: " + str(self.__listaProdutos[produto].quantidade) + "\n"
            retorno += mensagem

            mensagem = "Estoque mínimo: " + str(self.__listaProdutos[produto].estoqueMinimo) + "\n"
            retorno += mensagem

            mensagem = "Registros: " + "\n"
            retorno += mensagem

            regProcura = "produto " + self.__listaProdutos[produto].codigo

            for registro in self.__registros.keys():
                if regProcura in  self.__registros[registro]:
                    mensagem = "  " + registro + " - " + self.__registros[registro] + "\n"
                    retorno += mensagem
                
            mensagem = "\n"
            retorno += mensagem

        return retorno

    #Método para gerar relatório de registros
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioRegistros(self):
        retorno = ''
    
        mensagem = "\nRelatório de registros: \n\n"
        retorno += mensagem

        for registro in self.__registros.keys():
            mensagem = registro + " - " + self.__registros[registro] + "\n"
            retorno += mensagem
        
        return retorno

    #Método para gerar relatório de produtos que acabaram
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioProdutosAcabaram(self):
        retorno = ''

        mensagem = "\nRelatório de produtos que acabaram: \n\n"
        retorno += mensagem

        for produto in self.__listaProdutos.keys():
            if self.__listaProdutos[produto].acabou == 1:
                mensagem = "Código do produto: " + produto + "\n"
                retorno += mensagem

                mensagem = "Nome: " + self.__listaProdutos[produto].nome + "\n"
                retorno += mensagem

                mensagem = "Quantidade: " + str(self.__listaProdutos[produto].quantidade) + "\n"
                retorno += mensagem

                mensagem = "Estoque mínimo: " + str(self.__listaProdutos[produto].estoqueMinimo) + "\n"
                retorno += mensagem

                mensagem = "Registros: " + "\n"
                retorno += mensagem

                regProcura = "produto " + self.__listaProdutos[produto].codigo

                for registro in self.__registros.keys():
                    if regProcura in  self.__registros[registro]:
                        mensagem = "  " + registro + " - " + self.__registros[registro] + "\n"
                        retorno += mensagem
                
                mensagem = "\n"
                retorno += mensagem

        return retorno
    
    #Método para gerar relatório de fluxo de movimentação por período
    @app.route('/produto', methods=['POST'])
    @Pyro5.server.expose
    def relatorioFluxoMovimentacao(self, dataInicio, dataFim):
        retorno = ''
        
        mensagem = "\nRelatório de fluxo de movimentação: \n\n"
        retorno += mensagem

        for registro in self.__registros.keys():
            if dataInicio <= registro <= dataFim:
                mensagem = registro + " - " + self.__registros[registro] + "\n"
                retorno += mensagem
        
        return retorno

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