import os
import subprocess
import xml.etree.ElementTree as ET
import pytest

# TODO: Import your actual generator function here once implemented.
# For example: from circ_maker import generate_circ
# We use a dummy function here so the tests can be structured.
def generate_circ_dummy(output_path, dummy_content=""):
    """
    Mock function representing your Circ-Maker program generating a file.
    Replace calls to this function in the tests with your actual generator.
    """
    with open(output_path, "w") as f:
        f.write(dummy_content)


@pytest.fixture
def tmp_circ_file(tmp_path):
    """Fixture to provide a temporary file path for the .circ file."""
    return tmp_path / "test_circuit.circ"


def test_truth_table_compilation(tmp_circ_file):
    """
    Test 1: Generates a circuit and runs logisim-evolution headless
    to extract and verify the truth table.
    """
    # 1. Generate your circuit
    # TODO: Replace with your actual generator call that produces a known logic circuit (e.g., AND gate)
    # generate_circ(tmp_circ_file, config="and_gate")
    
    # We create a dummy AND gate XML here just to show what the test expects for a valid run
    valid_and_gate_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project source="3.8.0" version="1.0">
  <circuit name="main">
    <comp lib="0" loc="(100,100)" name="Pin">
      <a name="appearance" val="classic"/>
      <a name="label" val="A"/>
    </comp>
    <comp lib="0" loc="(100,140)" name="Pin">
      <a name="appearance" val="classic"/>
      <a name="label" val="B"/>
    </comp>
    <comp lib="1" loc="(200,120)" name="AND Gate"/>
    <comp lib="0" loc="(250,120)" name="Pin">
      <a name="appearance" val="classic"/>
      <a name="facing" val="west"/>
      <a name="label" val="OUT"/>
      <a name="output" val="true"/>
    </comp>
    <wire from="(100,100)" to="(150,100)"/>
    <wire from="(100,140)" to="(150,140)"/>
    <wire from="(200,120)" to="(250,120)"/>
  </circuit>
</project>
"""
    generate_circ_dummy(tmp_circ_file, dummy_content=valid_and_gate_xml)

    # 2. Run Logisim-Evolution via subprocess to extract the truth table
    # Requires logisim-evolution to be in PATH (handled by nix-shell)
    try:
        result = subprocess.run(
            ["logisim-evolution", "-tty", "table", str(tmp_circ_file)],
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        pytest.skip("logisim-evolution not found in PATH. Are you inside nix-shell?")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"logisim-evolution failed with error: {e.stderr}")

    # 3. Verify the truth table output
    # logisim output format typically looks like:
    # A B | OUT
    # 0 0 | 0
    # 0 1 | 0
    # 1 0 | 0
    # 1 1 | 1
    output = result.stdout.strip()
    
    assert "0 0 | 0" in output
    assert "0 1 | 0" in output
    assert "1 0 | 0" in output
    assert "1 1 | 1" in output


def test_xml_schema_validation(tmp_circ_file):
    """
    Test 2: Verifies that the generated .circ file is valid XML and contains
    the required boilerplate tags for Logisim Evolution.
    """
    # 1. Generate circuit
    # TODO: generate_circ(tmp_circ_file, ...)
    valid_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project source="3.8.0" version="1.0">
  <circuit name="main">
    <comp lib="0" loc="(100,100)" name="Pin"/>
  </circuit>
</project>"""
    generate_circ_dummy(tmp_circ_file, dummy_content=valid_xml)
    
    # 2. Parse XML
    try:
        tree = ET.parse(tmp_circ_file)
        root = tree.getroot()
    except ET.ParseError as e:
        pytest.fail(f"Generated file is not valid XML: {e}")

    # 3. Validate structure
    assert root.tag == "project", "Root element must be <project>"
    
    # Check for <circuit> tags
    circuits = root.findall("circuit")
    assert len(circuits) > 0, "At least one <circuit> must be present"
    
    # Check for basic components in the main circuit
    main_circuit = None
    for circ in circuits:
        if circ.attrib.get("name") == "main":
            main_circuit = circ
            break
            
    assert main_circuit is not None, "A circuit named 'main' must exist"


def test_deterministic_generation(tmp_path):
    """
    Test 3: Generates the exact same circuit configuration twice and asserts
    that the output files are byte-for-byte identical.
    """
    file1 = tmp_path / "circuit1.circ"
    file2 = tmp_path / "circuit2.circ"
    
    # 1. Generate the same circuit twice
    # TODO: Replace with actual generator calls
    # generate_circ(file1, config="my_complex_circuit")
    # generate_circ(file2, config="my_complex_circuit")
    
    # Using dummy for demonstration
    generate_circ_dummy(file1, dummy_content="<project></project>")
    generate_circ_dummy(file2, dummy_content="<project></project>")

    # 2. Compare files
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        content1 = f1.read()
        content2 = f2.read()
        
    assert content1 == content2, "Generator output is not deterministic (files differ)"
