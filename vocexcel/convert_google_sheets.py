import gspread
from gspread import Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from typing import Tuple, List
import pygsheets

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

try:
    import models
    from utils import split_and_tidy, ConversionError, load_workbook
except:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import split_and_tidy, ConversionError, load_workbook

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

concept_sheet = client.open("Google Sheets test VocExcel-template_043").worksheet('Concepts*')
concept_scheme_sheet = client.open("Google Sheets test VocExcel-template_043").worksheet('Concept Scheme*')
additional_concept_sheet = client.open("Google Sheets test VocExcel-template_043").worksheet('Additional Concept '
                                                                                             'Features')
collections_sheet = client.open("Google Sheets test VocExcel-template_043").worksheet('Collections')
prefix_sheet = client.open("Google Sheets test VocExcel-template_043").worksheet('Prefix Sheet')




def extract_concept_scheme(sheet: Worksheet):
    cs = models.ConceptScheme(
        uri=sheet.cell(2, 2).value,
        title=sheet.cell(3, 2).value,
        description=sheet.cell(4, 2).value,
        created=sheet.cell(5, 2).value,
        modified=sheet.cell(6, 2).value,
        creator=sheet.cell(7, 2).value,
        publisher=sheet.cell(8, 2).value,
        version=sheet.cell(9, 2).value,
        provenance=sheet.cell(10, 2).value,
        custodian=sheet.cell(11, 2).value,
        pid=sheet.cell(12, 2).value,
    )
    return cs

def extract_concept(csheet: gspread.Worksheet, acsheet: gspread.Worksheet):
    all_concept_sheet_values = csheet.get_values()
    additional_concept_sheet_values = acsheet.get_values()
    concepts = []
    counter = 0
    row = 3
    column = 1
    for rows in all_concept_sheet_values:
        if rows[0] == "Concepts" or rows[0] == "Concept IRI*":
            pass
        else:
            try:
                c = models.Concept(
                    uri=rows[0],
                    pref_label=rows[1],
                    pl_language_code=split_and_tidy(rows[2]),
                    definition=rows[3],
                    def_language_code=split_and_tidy(rows[4]),
                    alt_labels=split_and_tidy(rows[5]),
                    children=split_and_tidy(rows[6]),
                    provenance=rows[7],
                    home_vocab_uri=rows[8])
                row += 1
                concepts.append(c)
            except ValidationError as e:
                raise ConversionError(
                    f" Concept Processing error likely at sheet {csheet}, row {row}, and has error {e}"
                )
    # Additional Concept Sheet
    for values in additional_concept_sheet_values:
        if values[0] == "None" or values[0] == "Concept Extras" or values[0] == "Concept IRI":
            pass
        else:
            try:
                ac = models.Concept(
                    related_match=split_and_tidy(values[1]),
                    close_match=split_and_tidy(values[2]),
                    exact_match=split_and_tidy(values[3]),
                    narrow_match=split_and_tidy(values[4]),
                    broad_match=split_and_tidy(values[5])
                )
                concepts[counter] += ac
                counter += 1
            except ValidationError as e:
                raise ConversionError(
                    f" Additional Concept Processing error likely at sheet {acsheet}, row{row}, and has error {e}"
                )
    return concepts




    # uri: str
    # title: str
    # description: str
    # created: datetime.date
    # modified: datetime.date = None
    # creator: str
    # publisher: str
    # provenance: str
    # version: str = None
    # custodian: str = None
    # pid: str = None  .cell(5, 2)
if __name__ == '__main__':
    print(extract_concept(concept_sheet, additional_concept_sheet))




