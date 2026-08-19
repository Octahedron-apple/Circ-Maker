# Usage and Syntax

## How it Works: The DSL

Input is provided via **DSL files** (e.g., `my_circuit.circdef`). Because our engine parses these as restricted Python code injected with our builder context, you get to write pure logical equations using natural Python bitwise operators (`&`, `|`, `^`, `~`) without any boilerplate!

### DSL Syntax & Operators

Our DSL is essentially Python, but overloaded to create logic gates:

- **Inputs/Outputs:** Use `circ.add_input("Name")` and `circ.add_output("Name", signal)`.
- **AND Gate (`&`):** e.g., `Out = A & B`
- **OR Gate (`|`):** e.g., `Out = A | B`
- **XOR Gate (`^`):** e.g., `Out = A ^ B`
- **NOT Gate (`~`):** e.g., `Out = ~A`

Because it's embedded in Python, you can freely use variables, parenthesis for grouping (like `(A & B) | C`), and loops to generate arrays of gates!

### Example DSL File (`adder.circdef`):

```python
# The 'circ' builder object is automatically provided to this file!
A = circ.add_input("A")
B = circ.add_input("B")
Cin = circ.add_input("Cin")

AxorB = A ^ B
Sum = AxorB ^ Cin
Cout = (A & B) | (Cin & AxorB)

circ.add_output("Sum", Sum)
circ.add_output("Cout", Cout)
```

## Basic Instructions

### 1. Setup Environment
A reproducible `nix-shell` environment is provided, which includes all dependencies (including Logisim-Evolution for headless testing).
```bash
nix-shell
```

### 2. Generating a Circuit via CLI
Once installed, you can use the built-in CLI command to parse a definition file and output a `.circ` file. 

```bash
# This will automatically generate 'adder.circ' in the same directory
circ-maker adder.circdef
```

You can also specify a custom output path:
```bash
circ-maker adder.circdef -o custom_output.circ
```

Alternatively, if you prefer generating circuits directly from within a Python script:
```python
from circ_maker.runner import run_dsl_file

run_dsl_file("adder.circdef", output_filename="adder.circ")
```
This produces a fully routed `.circ` file that you can immediately open in the Logisim-Evolution GUI.

### 3. Running the Test Suite
To uphold TDD principles, the test suite automatically boots Logisim-Evolution headlessly in the background to verify the truth tables of the generated XML files. This allows for constant validation of routing and logic behavior.
```bash
nix-shell --run "PYTHONPATH=src python3 -m pytest tests/"
```
