import os
from circ_maker.builder import CircuitBuilder

def run_dsl_file(filepath, output_filename=None):
    """
    Reads an external Python-based DSL file and executes it.
    The file is expected to define a circuit using CircuitBuilder.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"DSL file not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # We can inject CircuitBuilder into the global namespace of the script
    # so they don't even need to import it!
    exec_globals = {
        "__builtins__": __builtins__,
        "CircuitBuilder": CircuitBuilder,
    }
    
    # Execute the DSL script
    exec(code, exec_globals)
    
    # Optionally, if the user didn't compile manually in the script,
    # we can try to find a 'circ' object in globals and compile it.
    if output_filename and "circ" in exec_globals:
        exec_globals["circ"].compile(output_filename)
