REM validation of dsb

echo TestD04

ajv compile -s dsb.json -r dbe.json -r calorimetric.json -r calorimetricData.json -r common.json -r component.json -r gaps.json -r geometry.json -r hygrothermal.json -r identifier.json -r layer.json -r material.json -r method.json -r number.json -r optical.json -r opticalData -r photovoltaic.json -r stakeholder.json -r string.json -r unit.json -r building.json 

PING localhost -n 10 >NUL