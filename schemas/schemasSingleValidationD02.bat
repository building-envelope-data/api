REM single validation of dbe

PING localhost -n 3 >NUL

ajv compile -s dbe.json -r calorimetric.json -r common.json -r component.json -r gaps.json -r geometry.json -r hygrothermal.json -r identifier.json -r layer.json -r material.json -r method.json -r number.json -r optical.json -r photovoltaic.json -r stakeholder.json -r string.json -r unit.json > validationResults.txt

PING localhost -n 3 >NUL

D:\Users\cmaurer\Desktop\200418_HomeOffice\SCOPE\dbe-data-schema-for-building-envelopes\schemas>ajv compile -s dsb.json -r dbe.json -r calorimetric.json -r common.json -r component.json -r gaps.json -r geometry.json -r hygrothermal.json -r identifier.json -r layer.json -r material.json -r method.json -r number.json -r optical.json -r photovoltaic.json -r stakeholder.json -r string.json -r unit.json -r building.json
schema dsb.json is valid

PING localhost -n 10 >NUL