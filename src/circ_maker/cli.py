import sys
import argparse
from circ_maker.runner import run_dsl_file

def main():
    parser = argparse.ArgumentParser(
        description="Circ-Maker CLI - Generate Logisim-Evolution circuits from Python DSL."
    )
    parser.add_argument(
        "input",
        help="Path to the input .circdef DSL file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Optional path for the output .circ file. Defaults to replacing .circdef with .circ",
        default=None
    )
    
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    
    if output_file is None:
        if input_file.endswith(".circdef"):
            output_file = input_file[:-8] + ".circ"
        else:
            output_file = input_file + ".circ"
            
    try:
        run_dsl_file(input_file, output_filename=output_file)
    except Exception as e:
        print(f"Error compiling circuit: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
