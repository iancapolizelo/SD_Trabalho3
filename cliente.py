import Pyro5.api
import logging
import threading
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

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

    print(servidorGerenciadorEstoque.registrarCliente(
        clienteInstancia.nome, clienteInstancia.uriCliente))
    
    # Interface do cliente
    while (1):
        print("\nAs opções do servidor são:")
        print("1 - Cadastrar novo produto")
        print("2 - Adicionar produto existente")
        print("3 - Retirar produto")
        print("4 - Listar produtos")
        print("5 - Gerar relatórios\n")
        opcao = input()

        if opcao == '1':
            codigoProduto = input("\nQual o código do produto? ")
            nomeProduto = input("Qual nome do produto? ")
            descricaoProduto = input("Qual a descrição do produto? ")
            quantidadeProduto = input("Qual a quantidade do produto? ")
            precoUnidadeProduto = input("Qual o preço por unidade do produto? ")
            estoqueMinimoProduto = input("Qual o estoque mínimo do produto? ")

            retorno = servidorGerenciadorEstoque.cadastrarProdutoNovo(
                clienteInstancia.nome, clienteInstancia.uriCliente, codigoProduto, nomeProduto, descricaoProduto, quantidadeProduto, precoUnidadeProduto, estoqueMinimoProduto)
            
            print(retorno)

        if opcao == '2':
            codigoProduto = input("\nQual o código do produto? ")
            quantidadeProduto = input("Qual a quantidade que deseja adicionar? ")

            retorno = servidorGerenciadorEstoque.adicionarProduto(codigoProduto, quantidadeProduto)

            print(retorno)
            

        if opcao == '3':
            codigoProduto = input("\nQual o código do produto? ")
            quantidadeProduto = input("Qual a quantidade do produto? ")
            print(servidorGerenciadorEstoque.retirarProduto(codigoProduto, quantidadeProduto))

        if opcao == '4':
            print(servidorGerenciadorEstoque.listarProdutos())

        if opcao == '5':
            print("\nAs opções de relatório são:")
            print("a - Relatório de produtos em estoque")
            print("b - Relatório de registros de movimentação de produtos")
            print("c - Relatório de produtos que acabaram")
            print("d - Relatório do fluxo de movimentação por período\n")
            #print("e - Relatório do produtos sem saída por período\n")
            opcaoRelatorio = input()

            if opcaoRelatorio == 'a':
                print(servidorGerenciadorEstoque.relatorioProdutosEstoque())

            if opcaoRelatorio == 'b':
                print(servidorGerenciadorEstoque.relatorioRegistros())

            if opcaoRelatorio == 'c':
                print(servidorGerenciadorEstoque.relatorioProdutosAcabaram())

            if opcaoRelatorio == 'd':
                dataInicio = input("\nQual a data de início do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ")
                dataFim = input("Qual a data de fim do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ")
                print(servidorGerenciadorEstoque.relatorioFluxoMovimentacao(dataInicio, dataFim))
"""
            if opcaoRelatorio == 'e':
                dataInicio = input("\nQual a data de início do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ")
                dataFim = input("Qual a data de fim do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ")
                servidorGerenciadorEstoque.relatorioProdutosSemSaida(clienteInstancia.nome, dataInicio, dataFim)
"""
                
            
