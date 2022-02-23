try:
    from vocexcel import convert
except:
    import sys

    sys.path.append("..")
    from vocexcel import convert

from pathlib import Path
from rdflib import Graph


def peter_example():
    convert.excel_to_rdf(
        Path(__file__).parent.parent / "baddata.xlsx",
        output_type="file",
    )




if __name__ == "__main__":
    peter_example()