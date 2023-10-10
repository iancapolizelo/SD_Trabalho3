from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler


from Pyro5.api import Daemon, locate_ns
from gerenciadorEstoque import gerenciadorEstoque


if __name__ == '__main__':
    with Daemon() as daemon:

        estoque = gerenciadorEstoque()

        with locate_ns() as ns:
            uri = daemon.register(estoque)
            ns.register("Gerenciador de Estoque", uri)

        # enter the service loop.
        scheduler = BackgroundScheduler()
        scheduler.start()
        print("Servidor do Gerenciador de Estoque aberto")
        daemon.requestLoop()
