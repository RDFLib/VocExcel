# Tests
## And example Excel and RDF files

The valid Excel and RDF files here should convert without errors. The invalid ones should give the following errors:

### Excel to RDF:
* **eg-invalid.xlsx**
    * _Error: ConceptScheme processing error: 1 validation error for ConceptScheme title none is not an allowed value (type=type_error.none.not_allowed)_
    * the vocabulary is missing a title!
* **eg-invalid2.xlsx**
    * _Error: Concept processing error, row 17, error: 1 validation error for Concept uri URL invalid, extra characters found after valid URL: ' xxx' (type=value_error.url.extra; extra= xxx)_
    * the Concept on line 17 has an invalid URI!

### RDF to Excel
* **eg-invalid.ttl**
    * _Error: The file you supplied is not valid according to the vocpub profile_ and then a bunch of messages about why it's invalid
* **eg-invalid2.ttl**
    * _Error: Error while uploading_ or similar. The file is valid RDF but the file extension indicates the Turtle format but it's actually in the XML format