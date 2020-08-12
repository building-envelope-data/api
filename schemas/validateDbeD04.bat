REM validation of dbe

echo TestD04

ajv compile -s dbe.json -r calorimetric.json -r calorimetricData.json -r common.json -r component.json -r gaps.json -r geometry.json -r hygrothermal.json -r hygrothermalData.json -r identifier.json -r layer.json -r material.json -r method.json -r number.json -r optical.json -r opticalData.json -r photovoltaic.json -r photovoltaicData.json -r stakeholder.json -r string.json -r unit.json

PING localhost -n 10 >NUL