from vocexcel import convert

# convert.rdf_to_excel("vocab-invalid.ttl")
print(convert.excel_to_rdf("eg-valid.xlsx", output_type="string", output_format="xml"))
