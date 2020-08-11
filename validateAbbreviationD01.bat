REM validation of the example abbreviation.json

echo TestD01

ajv validate -s ./schemas/dbe.json -d ./examples/dbe/metadata/abbreviation.json -r ./schemas/calorimetric.json -r ./schemas/calorimetricData.json -r ./schemas/common.json -r ./schemas/component.json -r ./schemas/gaps.json -r ./schemas/geometry.json -r ./schemas/hygrothermal.json -r ./schemas/identifier.json -r ./schemas/layer.json -r ./schemas/material.json -r ./schemas/method.json -r ./schemas/number.json -r ./schemas/optical.json -r ./schemas/opticalData.json -r ./schemas/photovoltaic.json -r ./schemas/stakeholder.json -r ./schemas/string.json -r ./schemas/unit.json

PING localhost -n 10 >NUL