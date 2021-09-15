from vocexcel import convert

convert.rdf_to_excel("tests/eg-valid.ttl", error_level=1, message_level=1)
# convert.excel_to_rdf("tests/eg-invalid.xlsx")

# convert.rdf_to_excel("tests/eg-valid.ttl", error_level=3, message_level=2, log_file="file.log")

# message_list = []

# with open("file.log", "r") as f:
#     message_list = f.read().split("\n\n")

# info_list = []
# warning_list = []
# error_list = []

# for msg in message_list:
#     if msg.startswith("INFO: "):
#         info_list.append(msg)
#     elif msg.startswith("WARNING: "):
#         warning_list.append(msg)
#     elif msg.startswith("VIOLATION: "):
#         error_list.append(msg)

# print(info_list)
# print(warning_list)
# print(error_list)