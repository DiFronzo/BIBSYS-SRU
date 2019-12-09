# BIBSYS-SRU
A module for requesting and parsing SRU data from BIBSYS.

# Example - Single Zone Request
```
from bibsys.sru import control

# Build SRU request
bib_query = control.make_url(zone="bibsys", query=f"Tommy Tee")

# Make SRU request
bib_query_resp = control.search(bib_query)

# Create SRU response objects
bib = control.parse(bib_query_resp, zone="bibsys", printOut="yes")
```

# How to Parse Output
The SRU client will return an SRU object that can be called to get various information about the search result.

# How to Parse Search Results

## sru_object.numberOfRecords
Returns the number of records found.

## sru_object.ok
Is either TRUE (no errors encountered) or FALSE (some errors encountered)

## sru_object.errors
Returns any errors encountered.

## sru_object.xml
Returns XML representation of SRU response.

## sru_object.dict
Returns a dictionary of the SRU response.

## sru_object.list
Returns a list of dictionarys that is structured.

