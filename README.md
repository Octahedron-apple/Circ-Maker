# Circ-Maker

**Circ-Maker** is a Python-based framework and DSL (Domain Specific Language) for generating fully functional, non-colliding Logisim-Evolution `.circ` files from simple code.

> **Built with Test-Driven Development (TDD) 🚀**
> We didn't just write this; we engineered it. By adhering to rigorous TDD principles, we designed a suite of automated Logisim truth-table compilation tests *before* finalizing the logic! Our automated CI tests instantly catch complex routing short-circuits (like the ones we successfully patched in our channel router), guaranteeing that the logic you write is strictly the logic you get. 

## How it Works: The DSL

Input is provided via **DSL files** (e.g., `my_circuit.circdef`). Because our engine parses these as restricted Python code injected with our builder context, you get to write pure logical equations using natural Python bitwise operators (`&`, `|`, `^`, `~`) without any boilerplate!

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
We provide a reproducible `nix-shell` environment that includes all dependencies (including Logisim-Evolution for headless testing).
```bash
nix-shell
```

### 2. Generating a Circuit
Currently, you can use our DSL runner to parse a definition file and output a `.circ` file. 

Create a script or use the runner directly in Python:
```python
from circ_maker.runner import run_dsl_file

run_dsl_file("adder.circdef", output_filename="adder.circ")
```
This produces a fully routed `adder.circ` file that you can immediately open in the Logisim-Evolution GUI.

### 3. Running the Test Suite
Because we value TDD, you can verify your routing and logic at any time. Our test suite actually boots Logisim-Evolution headlessly in the background to verify the truth tables of the generated XML files!
```bash
nix-shell --run "PYTHONPATH=src python3 -m pytest tests/"
```