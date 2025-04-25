
from io import TextIOWrapper

from src.components import _comps, Iface, _ServiceType, _Service, _IfaceConfig


# supported colors: https://graphviz.org/doc/info/colors.html
COLOR_MAP = {
    _ServiceType.client.name: "red",
    _ServiceType.tgen.name: "brown",
    _ServiceType.dhcp.name: "blue",
    _ServiceType.dns.name: "purple",
    _ServiceType.server.name: "deepskyblue",
    _ServiceType.router.name: "green",
    _ServiceType.lb.name: "coral",
}


class Grapher():
    def __init__(self, color: bool):
        """
        @params:
            - color: Enable or disable coloring nodes by service type.
        """

        try:
            self.__comps = _comps.copy()  # remove ifaces without affecting external
            self.__ifaces = self.__comps.pop("iface")
        except Exception as _:
            print("notice: No interfaces found. Skipping.")
            return

        with open("shared/config-graph.gv", "w") as file:
            file.write("\n")  # new line
            file.write("# neato -Tjpeg input.gv -o output.jpeg\n")
            file.write("strict graph Network_Configuration {\n")
            file.write("\tfontname=\"Helvetica,Arial,sans-serif\"\n")
            file.write("\tnode [ fontname=\"Helvetica,Arial,sans-serif\" ]\n")
            file.write("\tedge [ fontname=\"Helvetica,Arial,sans-serif\" ]\n")
            file.write("\n")  # new line

            # dpi increases sharpness; scale increases size
            file.write("\tgraph [ splines=line overlap=scale dpi=150 ]\n")
            file.write("\tlabel=\"Network Configuration\"\n")
            file.write("\tlabelloc=\"t\"\n")

            file.write("\n")  # new line
            file.write("\t# NODES\n")
            self.__write_nodes(file, color)

            file.write("\n")  # new line
            file.write("\t# CONNECTIONS\n")
            self.__write_connections(file)

            file.write("}\n")

    def __write_nodes(self, file: TextIOWrapper, color: bool):
        """
        @params:
            - file: File to write to.
            - color: Enable or disable coloring nodes by service type.
        """

        file.write("\t# COMPONENTS\n")

        for comps in self.__comps.values():
            for service in comps:  # comps is a list
                assert isinstance(service, _Service)

                name = service._name

                color = "black"
                if color and service._type.name in COLOR_MAP:
                    color = COLOR_MAP[service._type.name]

                file.write(f"\t\"{name}\" [ color=\"{color}\" fontcolor=\"{color}\" ]\n")
        
        file.write("\n")  # new line
        file.write("\t# IFACES\n")
        for iface in self.__ifaces:
            assert(type(iface) == Iface)

            name = iface._name
            cidr = iface._cidr._str

            file.write(f"\t\"{name}\" [ label=\"{name}\\n{cidr}\" ]\n")

    def __write_connections(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        for comps in self.__comps.values():
            for service in comps:
                assert isinstance(service, _Service)

                name_service = service._name

                for config in service._iface_configs:
                    assert(type(config) == _IfaceConfig)

                    name_iface = config._iface._name
                    ip = config._ip._str
                    rate = config._rate  #mbps

                    file.write(f"\t\"{name_service}\" -- \"{name_iface}\" [ label=\"{ip}\\n{rate}mbps\" ]\n")
