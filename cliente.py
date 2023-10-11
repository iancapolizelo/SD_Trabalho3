import Pyro5.api
import logging
import threading
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

"""Classe cliente, que é responsável por fazer a comunicação com o servidor de nomes e com o servidor de estoque
    Atributos:
        nome: nome do cliente
        uriCliente: uri do cliente
    Métodos:
        pedeCriar: pede para criar o cliente
        inicializaDaemon: inicializa o daemon do cliente
        notificacao: notifica o cliente de algum acontecimento
            notificação é exposta para o servidor, para que possa acontecer a comunicação"""

class cliente():
    nome = ""
    uriCliente = ""

    def __init__(self):
        self.nome = input(
            "Bem vindo ao Gerenciador de Estoque!\n\nInforme seu nome de registro no servidor: ")

    def pedeCriar(self, uriCliente):
        self.uriCliente = uriCliente

    def inicializaDaemon(self, daemon):
        daemon.requestLoop()


    @Pyro5.api.expose
    @Pyro5.api.callback
    def notificacao(self, acontecimento):
        print(acontecimento)


if __name__ == '__main__':
    
    clienteInstancia = cliente()
    daemon = Pyro5.api.Daemon()
    uriCliente = daemon.register(clienteInstancia)
    clienteInstancia.pedeCriar(uriCliente)

    # Inicializa o daemon em uma thread separada para que o cliente possa receber notificações e não fique travado esperando resposta do servidor
    daemonThread = threading.Thread(
        target=clienteInstancia.inicializaDaemon, args=(daemon,), daemon=True)
    daemonThread.start()

    servidorNomes = Pyro5.api.locate_ns()
    uriGerenciadorEstoque = servidorNomes.lookup("Gerenciador de Estoque")
    servidorGerenciadorEstoque = Pyro5.api.Proxy(uriGerenciadorEstoque)

    servidorGerenciadorEstoque.registrarCliente(
        clienteInstancia.nome, clienteInstancia.uriCliente)
    
    # Interface do cliente
    while (1):
        print("As opções do servidor são:\n")
        print("1 - Cadastrar novo produto\n")
        print("2 - Adicionar produto existente\n")
        print("3 - Retirar produto\n")
        print("4 - Listar produtos\n\n")
        opcao = input()
        if opcao == '1':
            codigoProduto = input("Qual o código do produto?\n")
            nomeProduto = input("Qual nome do produto?\n")
            descricaoProduto = input("Qual a descrição do produto? \n")
            quantidadeProduto = input("Qual a quantidade do produto? \n")
            precoUnidadeProduto = input("Qual o preço por unidade do produto? \n")
            estoqueMinimoProduto = input("Qual o estoque mínimo do produto? \n")

            servidorGerenciadorEstoque.cadastrarProdutoNovo(
                clienteInstancia.nome, clienteInstancia.uriCliente, codigoProduto, nomeProduto, descricaoProduto, quantidadeProduto, precoUnidadeProduto, estoqueMinimoProduto)

        if opcao == '2':
            codigoProduto = input("Qual o código do produto? ")
            quantidadeProduto = input("Qual a quantidade que deseja adicionar? ")

            servidorGerenciadorEstoque.adicionarProduto(
                    clienteInstancia.nome, codigoProduto, quantidadeProduto)
            

        if opcao == '3':
            codigoProduto = input("Qual o código do produto? ")
            quantidadeProduto = input("Qual a quantidade do produto? ")
            servidorGerenciadorEstoque.retirarProduto(
                    clienteInstancia.nome, codigoProduto, quantidadeProduto)

        if opcao == '4':
            servidorGerenciadorEstoque.listarProdutos(clienteInstancia.nome)
            
