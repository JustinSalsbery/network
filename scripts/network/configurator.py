
from io import TextIOWrapper

from components import *


class Configuration():
    def __init__(self):
        self.__networks: list[Network] = []
        # self.__services: list[Service]

    def create_network(self, subnet: str):
        network = Network(self.__networks, subnet)
        self.__networks.append(network)

    # def append_service(self, service: Service):
    #     self.__services.append(service)

    def get_networks(self) -> list[Network]:
        return self.__networks
    
    # def get_services(self) -> list[Service]:
    #     return self.__services
    
    # def write_conf(self):
    #     pass


if __name__ == "__main__":
    conf = Configuration()
    conf.create_network("169.254.0.0/24")
    conf.create_network("169.254.0.0/24")
    print(conf.get_networks()[0])

    server = Server()
