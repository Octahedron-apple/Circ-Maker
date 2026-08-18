from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom


# =====================================================================
# 1. DSL & Signal Graph Representation
# =====================================================================
class Signal:

    def __init__(self, name=None, driver=None):
        self.name = name
        self.driver = driver  # Gate producing this signal (None for input pins)
        self.loc = None  # (x, y) driver pin location
        self.layer = 0

    def __and__(self, other):
        return Gate("AND Gate", [self, to_signal(other)])

    def __or__(self, other):
        return Gate("OR Gate", [self, to_signal(other)])

    def __xor__(self, other):
        return Gate("XOR Gate", [self, to_signal(other)])

    def __invert__(self):
        return Gate("NOT Gate", [self])


def to_signal(obj):
    return obj if isinstance(obj, Signal) else Signal(name=str(obj))


class Gate(Signal):

    def __init__(self, gate_type, inputs):
        super().__init__(driver=self)
        self.gate_type = gate_type
        self.inputs = inputs
        self.layer = 0


# =====================================================================
# 2. Strict Non-Colliding Circuit Builder
# =====================================================================
class CircuitBuilder:

    def __init__(self, name="main"):
        self.name = name
        self.inputs = {}
        self.outputs = {}

    def add_input(self, name):
        s = Signal(name=name)
        self.inputs[name] = s
        return s

    def add_output(self, name, signal):
        self.outputs[name] = signal

    def compile(self, filename="circuit.circ"):
        # -------------------------------------------------------------
        # Step A: Topological Sort & Depth Calculation
        # -------------------------------------------------------------
        all_gates = []
        visited = set()

        def collect(sig):
            if sig.driver and sig.driver not in visited:
                visited.add(sig.driver)
                all_gates.append(sig.driver)
                for inp in sig.driver.inputs:
                    collect(inp)

        for sig in self.outputs.values():
            collect(sig)

        for sig in self.inputs.values():
            sig.layer = 0

        for _ in range(len(all_gates) + 2):
            for g in all_gates:
                in_layers = [getattr(inp, "layer", 0) for inp in g.inputs]
                g.layer = max(in_layers) + 1 if in_layers else 1

        max_layer = max((g.layer for g in all_gates), default=1)

        # -------------------------------------------------------------
        # Step B: Strict Grid Placement (Unique Y Tracks)
        # -------------------------------------------------------------
        X_START = 120
        COL_STEP = 240

        # 1. Place Inputs in Column 0 on distinct Y tracks
        for idx, (name, sig) in enumerate(self.inputs.items()):
            sig.loc = (X_START, 100 + idx * 60)

        # 2. Place Gates: Column = Layer, each gate gets a unique Y row
        layer_groups = defaultdict(list)
        for g in all_gates:
            layer_groups[g.layer].append(g)

        gate_y_start = 100 + len(self.inputs) * 60 + 40
        current_row = 0
        for layer_num in range(1, max_layer + 1):
            col_x = X_START + layer_num * COL_STEP
            row_in_col = 0
            for g in layer_groups[layer_num]:
                g.loc = (col_x, gate_y_start + current_row * 120)
                g.col_row_idx = row_in_col
                current_row += 1
                row_in_col += 1

        # 3. Place Outputs in the final column
        out_col_x = X_START + (max_layer + 1) * COL_STEP
        output_pin_locs = {}
        for idx, (name, sig) in enumerate(self.outputs.items()):
            # Align output pin with the driver's Y
            out_y = sig.driver.loc[1] if sig.driver else (100 + idx * 80)
            output_pin_locs[name] = (out_col_x, out_y)

        # -------------------------------------------------------------
        # Step C: Channel Routing with Dedicated Offsets
        # -------------------------------------------------------------
        wires = set()

        def add_wire(p1, p2):
            if p1 != p2:
                wires.add((min(p1, p2), max(p1, p2)))

        # 1. Route Gate Inputs via dedicated vertical tracks
        for g in all_gates:
            gx, gy = g.loc
            pin_x = gx - 30 if g.gate_type == "NOT Gate" else gx - 50

            for pin_idx, inp_sig in enumerate(g.inputs):
                if g.gate_type == "NOT Gate":
                    pin_y = gy
                else:
                    pin_y = gy - 20 if pin_idx == 0 else gy + 20

                src_loc = inp_sig.loc if inp_sig.loc else inp_sig.driver.loc

                # Dedicated channel track placed to the left of the gate pin column.
                # We stagger by col_row_idx so gates in the same column don't short-circuit!
                track_x = pin_x - 30 - getattr(g, 'col_row_idx', 0) * 40 - (pin_idx * 20)

                # Route: Source -> Horizontal to Track -> Vertical drop -> Horizontal stub to Pin
                add_wire(src_loc, (track_x, src_loc[1]))
                add_wire((track_x, src_loc[1]), (track_x, pin_y))
                add_wire((track_x, pin_y), (pin_x, pin_y))

        # 2. Route Outputs to Output Pins
        for name, sig in self.outputs.items():
            src_loc = sig.driver.loc if sig.driver else sig.loc
            out_loc = output_pin_locs[name]

            if src_loc[1] == out_loc[1]:
                add_wire(src_loc, out_loc)
            else:
                mid_x = out_loc[0] - 40
                add_wire(src_loc, (mid_x, src_loc[1]))
                add_wire((mid_x, src_loc[1]), (mid_x, out_loc[1]))
                add_wire((mid_x, out_loc[1]), out_loc)

        # -------------------------------------------------------------
        # Step D: Logisim-evolution XML Serialization
        # -------------------------------------------------------------
        project = ET.Element("project", source="4.1.0", version="1.0")

        libs = [
            ("#Wiring", "0"),
            ("#Gates", "1"),
            ("#Plexers", "2"),
            ("#Arithmetic", "3"),
            ("#FPArithmetic", "4"),
            ("#Memory", "5"),
            ("#I/O", "6"),
            ("#TTL", "7"),
            ("#TCL", "8"),
            ("#Base", "9"),
        ]
        for desc, name in libs:
            lib_elem = ET.SubElement(project, "lib", desc=desc, name=name)
            if desc == "#Wiring":
                tool = ET.SubElement(lib_elem, "tool", name="Pin")
                ET.SubElement(tool, "a", name="appearance", val="classic")

        ET.SubElement(project, "main", name=self.name)

        options = ET.SubElement(project, "options")
        ET.SubElement(options, "a", name="gateUndefined", val="ignore")
        ET.SubElement(options, "a", name="simlimit", val="1000")
        ET.SubElement(options, "a", name="simrand", val="0")

        mappings = ET.SubElement(project, "mappings")
        ET.SubElement(
            mappings, "tool", lib="9", map="Button2", name="Poke Tool"
        )
        ET.SubElement(
            mappings, "tool", lib="9", map="Button3", name="Menu Tool"
        )
        ET.SubElement(
            mappings, "tool", lib="9", map="Ctrl Button1", name="Menu Tool"
        )

        toolbar = ET.SubElement(project, "toolbar")
        for t in ["Poke Tool", "Edit Tool", "Wiring Tool", "Text Tool"]:
            ET.SubElement(toolbar, "tool", lib="9", name=t)
        ET.SubElement(toolbar, "sep")
        ET.SubElement(toolbar, "tool", lib="0", name="Pin")
        pin_out = ET.SubElement(toolbar, "tool", lib="0", name="Pin")
        ET.SubElement(pin_out, "a", name="facing", val="west")
        ET.SubElement(pin_out, "a", name="type", val="output")
        ET.SubElement(toolbar, "sep")
        for g_name in ["NOT Gate", "AND Gate", "OR Gate", "XOR Gate"]:
            ET.SubElement(toolbar, "tool", lib="1", name=g_name)

        circuit = ET.SubElement(project, "circuit", name=self.name)
        for key, val in [
            ("appearance", "logisim_evolution"),
            ("circuit", self.name),
            ("circuitnamedboxfixedsize", "true"),
            ("simulationFrequency", "1.0"),
        ]:
            ET.SubElement(circuit, "a", name=key, val=val)

        # Primary Input Pins
        for name, sig in self.inputs.items():
            comp = ET.SubElement(
                circuit,
                "comp",
                lib="0",
                loc=f"({sig.loc[0]},{sig.loc[1]})",
                name="Pin",
            )
            ET.SubElement(comp, "a", name="appearance", val="NewPins")
            ET.SubElement(comp, "a", name="label", val=name)

        # Primary Output Pins
        for name, out_pos in output_pin_locs.items():
            comp = ET.SubElement(
                circuit,
                "comp",
                lib="0",
                loc=f"({out_pos[0]},{out_pos[1]})",
                name="Pin",
            )
            ET.SubElement(comp, "a", name="appearance", val="NewPins")
            ET.SubElement(comp, "a", name="facing", val="west")
            ET.SubElement(comp, "a", name="type", val="output")
            ET.SubElement(comp, "a", name="label", val=name)

        # Gates
        for g in all_gates:
            comp = ET.SubElement(
                circuit,
                "comp",
                lib="1",
                loc=f"({g.loc[0]},{g.loc[1]})",
                name=g.gate_type,
            )
            if g.gate_type != "NOT Gate":
                ET.SubElement(comp, "a", name="inputs", val=str(len(g.inputs)))

        # Deduplicated Wires
        for (x1, y1), (x2, y2) in sorted(wires):
            ET.SubElement(
                circuit,
                "wire",
                {"from": f"({x1},{y1})", "to": f"({x2},{y2})"},
            )

        # Save XML
        xml_str = minidom.parseString(
            ET.tostring(project, encoding="utf-8")
        ).toprettyxml(indent="  ")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(f"Collision-free circuit generated: {filename}")
