import Pyro5.api
import logging
import threading
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


class cliente():
    nome = ""
    uriCliente = ""

    def __init__(self):
        print("Bem vindo ao Gerenciador de Estoque!\n\n")
        self.nome = input("Informe seu nome de registro no servidor: ")

    def pedeCriar(self, uriCliente):
        self.uriCliente = uriCliente


class CallbackHandler(object):
    @Pyro5.api.expose
    @Pyro5.api.callback
    def notificacao(self, acontecimento):
        print(acontecimento)


if __name__ == '__main__':
    
    clienteInstancia = cliente()
    daemon = Pyro5.api.Daemon()
    uriCliente = daemon.register(clienteInstancia)
    clienteInstancia.pedeCriar(uriCliente)
    callback = CallbackHandler()
    daemon.register(callback)

    servidorNomes = Pyro5.api.locate_ns()
    uriMercadoLeiloes = servidorNomes.lookup("Mercado de Leiloes")
    servidorMercadoLeiloes = Pyro5.api.Proxy(uriMercadoLeiloes)
    servidorMercadoLeiloes.registrarCliente(
        clienteInstancia.nome, clienteInstancia.uriCliente)
    while (1):
        print("As opções do servidor são:\n")
        print("1 - Criar leilão\n")
        print("2 - Listar leilões\n")
        print("3 - Dar lance em um leilão\n")
        opcao = input()
        if opcao == '1':
            nomeProduto = input("Qual o nome do produto?")
            descriçãoProduto = input("Qual a descrição do produto?")
            preçoBase = input("Qual o preço mínimo ?")
            limiteTempo = int(input(
                "Em quantos segundos deve expirar?"))
            servidorMercadoLeiloes.criarLeilao(
                nomeProduto, descriçãoProduto, preçoBase, limiteTempo, clienteInstancia.uriCliente, clienteInstancia.nome)
        if opcao == '2':
            lista = servidorMercadoLeiloes.listarLeiloes()
            for name in lista:
                print("  %s " % (name))
        if opcao == '3':
            nomeProduto = input("Qual o nome do produto em leilão?")
            valorLance = input("Qual o valor do seu lance?")
            resultadoLance = servidorMercadoLeiloes.darLance(
                valorLance, nomeProduto, clienteInstancia.uriCliente, clienteInstancia.nome)
            if (resultadoLance == 1):
                print("Lance Aceito")
            if (resultadoLance == 0):
                print("Lance Negado")
            if (resultadoLance == 2):
                print("Não existe Leilao com esse nome")
