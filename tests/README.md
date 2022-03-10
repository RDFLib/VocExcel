# Tests and Example Excel and RDF files

## What to Expect
This folder contains quite a few examples of simple and complex vocabularies and different versions of template. 

The most recent vocpub template model is 0.4.1 so for current use, it's recommnded to look at the simple valid and complex valid 041 examples. These contain excel sheets with complete vocabularies for reference. 

For multiple languages, refer to the 030 languages valid examples which shows how to have multiple inputs with other languages.

The valid Excel and RDF files here should convert without errors. The invalid ones should give the following errors:

### Excel to RDF:
* **eg-invalid.xlsx**
    * _Error: ConceptScheme processing error: 1 validation error for ConceptScheme title none is not an allowed value (type=type_error.none.not_allowed)_
    * the vocabulary is missing a title!
* **eg-invalid2.xlsx**
    * _Error: Concept processing error, row 17, error: 1 validation error for Concept uri URL invalid, extra characters found after valid URL: ' xxx' (type=value_error.url.extra; extra= xxx)_
    * the Concept on line 17 has an invalid URI!
* **040_complexexample_invalid.xlsx**
    * In this case, this file has cells containing invalid data. There are numbers instead of URI's in the children and close match cells
    * children
      Item 1 failed with messages HTTP IRIs must start with 'http' or 'https' (type=assertion_error)
      close_match
      Item 1 failed with messages HTTP IRIs must start with 'http' or 'https' and Item 2 failed with messages HTTP IRIs must start with 'http' or 'https' and Item 3 failed with messages HTTP IRIs must start with '
      http' or 'https' and Item 4 failed with messages HTTP IRIs must start with 'http' or 'https' (type=assertion_error)

The RDF to Excel conversion function is being re-implemented so these don't work just for the moment.

### RDF to Excel
* **eg-invalid.ttl**
    * _Error: The file you supplied is not valid according to the vocpub profile_ and then a bunch of messages about why it's invalid
* **eg-invalid2.ttl**
    * _Error: Error while uploading_ or similar. The file is valid RDF but the file extension indicates the Turtle format but it's actually in the XML format
