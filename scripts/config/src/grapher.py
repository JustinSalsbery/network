
from io import TextIOWrapper

from src.components import _components, Iface, _ServiceType, _Service, _IfaceConfig


# supported colors: https://graphviz.org/doc/info/colors.html
COLOR_MAP = {
    "default": "gainsboro",

    _ServiceType.client.name: "bisque",
    _ServiceType.tgen.name: "tan",
    _ServiceType.dhcp.name: "aquamarine",
    _ServiceType.dns.name: "paleturquoise",
    _ServiceType.http.name: "lightskyblue",
    _ServiceType.router.name: "palegreen",
    _ServiceType.lb.name: "plum",
    _ServiceType.tor.name: "coral",
}

FILE_NAME = "config-graph"


class Grapher():
    def __init__(self, color: bool, extra: bool):
        """
        @params:
            - color: Enable or disable coloring nodes by service type.
            - extra: Enable or disable extra information.
        """

        try:
            self._comps = _components.copy()  # remove ifaces without affecting external
            self._ifaces = self._comps.pop("iface")
        except Exception as _:
            print("Warning: No interfaces found. Stopping...")
            return

        with open("shared/config-graph.gv", "w") as file:
            file.write("\n")  # new line
            file.write(f"# neato -Tjpeg {FILE_NAME}.gv -o {FILE_NAME}.jpeg\n")
            file.write("strict graph Network_Configuration {\n")
            file.write("\tfontname=\"Helvetica,Arial,sans-serif\"\n")
            file.write("\tnode [ fontname=\"Helvetica,Arial,sans-serif\" ]\n")
            file.write("\tedge [ fontname=\"Helvetica,Arial,sans-serif\" ]\n")

            file.write("\n")  # new line
            file.write("\tlabel=\"Network Configuration\"\n")
            file.write("\tlabelloc=\"t\"  # place graph label at top\n")
            
            file.write("\n")  # new line
            file.write("\t# scale increases the size when there is overlap\n")
            file.write("\t# dpi increases sharpness\n")
            file.write("\tgraph [ splines=line overlap=scale dpi=150 ]\n")

            file.write("\n")  # new line
            file.write("\t# NODES\n")
            self._write_nodes(file, color, extra)

            file.write("\n")  # new line
            file.write("\t# CONNECTIONS\n")
            self._write_connections(file, extra)

            file.write("}\n")

    def _write_nodes(self, file: TextIOWrapper, color: bool, extra: bool):
        """
        @params:
            - file: File to write to.
            - color: Enable or disable coloring nodes by service type.
            - extra: Enable or disable extra information.
        """

        file.write("\t# COMPONENTS\n")

        for comps in self._comps.values():
            for service in comps:  # comps is a list
                assert isinstance(service, _Service)

                name = service._name

                color_fill = COLOR_MAP["default"]
                if color and service._type.name in COLOR_MAP:
                    color_fill = COLOR_MAP[service._type.name]

                file.write(f"\t\"{name}\" [ ")
                if extra:
                    file.write(f"label=\"{name}")

                    for iface in service._iface_configs:
                        assert isinstance(iface, _IfaceConfig)
                        file.write(f"\\n{iface._ip._str}")

                    file.write("\" ")

                file.write(f"style=\"filled\" fillcolor=\"{color_fill}\" ]\n")
        
        file.write("\n")  # new line
        file.write("\t# IFACES\n")
        for iface in self._ifaces:
            assert isinstance(iface, Iface)

            name = iface._name
            file.write(f"\t\"{name}\" [ ")

            if extra:
                file.write("shape=box ")
            else:
                file.write(f"label=\"\" shape=none height=0 width=0 ")

            file.write("]\n")

    def _write_connections(self, file: TextIOWrapper, extra: bool):
        """
        @params:
            - file: File to write to.
            - extra: Enable or disable extra information.
        """

        for comps in self._comps.values():
            for service in comps:
                assert isinstance(service, _Service)

                name_service = service._name
                for iface in service._iface_configs:
                    assert isinstance(iface, _IfaceConfig)

                    name_iface = iface._iface._name
                    file.write(f"\t\"{name_service}\" -- \"{name_iface}\" [ ]\n")
                    