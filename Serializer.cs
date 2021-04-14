using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace OpticsSerializer
{
    public class SpectralSerializer
    {
        public static string SerializeModel(Rootobject model)
        {
            // in System.Core.text.Json: JsonSerializer.Serialize(model);
            // in Newtonsoft.Json: JsonConvert.SerializeObject(model);
            return JsonConvert.SerializeObject(model);
        }

        public class Rootobject 
        {
            public Rootobject(List<Datapoint> dataPoints, Optical.MeasurementType type, Optical.ScatterDetectionDefinition scatterDefinition)
            {             
                Component newComponent = new Component("");
                newComponent.optical.Add(new Optical("", "", "", dataPoints));
                components = new List<Component>();
                components.Add(newComponent);
            }

            public Rootobject(string componentId, string issuedBy, string uniqueId, string explanation_enUS, 
                List<Datapoint> dataPoints, Optical.MeasurementType type, Optical.ScatterDetectionDefinition scatterDefinition)
            {
                Component newComponent = new Component(componentId);
                newComponent.optical.Add(new Optical(issuedBy, uniqueId, explanation_enUS, dataPoints));
                components = new List<Component>();
                components.Add(newComponent);
            }
            
            public List<Component> components { get; set; }
        }

        public class Component
        {
            public Component()
            {
                optical = new List<Optical>();
            }
            public Component(string id)
            {
                optical = new List<Optical>();
                this.id = id;
            }
            public string id { get; set; }
            public List<Optical> optical { get; set; }
        }

        public class Optical
        {
            public Optical()
            {
                id = new Id();
                explanation = new Explanation();
                dataPoints = new List<Datapoint>();
            }
            public Optical(string issuedBy, string uniqueId, string explanation_enUS, List<Datapoint> dataPoints)
            {
                this.id = new Id();
                this.id.issuedBy = issuedBy;
                this.id.uniqueId = uniqueId;
                this.explanation = new Explanation();
                this.explanation.enUS = explanation_enUS;
                this.dataPoints = dataPoints;
            }

            public Id id { get; set; }

            public Explanation explanation { get; set; }

            public List<Datapoint> dataPoints { get; set; }

            public void addDataPoint(Datapoint point)
            {
                dataPoints.Add(point);
            }

            public enum MeasurementType
            {
                transmittance,
                reflectance
            }

            public enum ScatterDetectionDefinition
            {
                diffuse,
                hemispherical,
                nearnormal
            }

        }

        public class Id
        {
            public string uniqueId { get; set; }
            public string issuedBy { get; set; }
        }

        public class Explanation
        {
            public string enUS { get; set; }
        }

        public class Datapoint
        {
            public Datapoint(double wavelength, double value, Optical.MeasurementType type, Optical.ScatterDetectionDefinition direction)
            {
                this.incidence = new Incidence(wavelength);
                this.emergence = new Emergence(type, direction);
                this.results = new Results(value);
            }

            public Incidence incidence { get; set; }
            public Emergence emergence { get; set; }
            public Results results { get; set; }
        }

        public class Incidence
        {
            public Incidence(double wavelength)
            {
                direction = new List<List<string>>();
                wavelengths = new Wavelengths(wavelength);
            }

            public List<List<string>> direction { get; set; }

            public Wavelengths wavelengths { get; set; }
        }

        public class Wavelengths
        {
            public double wavelength { get; set; }
            public Wavelengths(double wavelength)
            {
                this.wavelength = wavelength;
            }
        }

        public class Emergence
        {
            public Emergence(Optical.MeasurementType type, Optical.ScatterDetectionDefinition direction)
            {
                List<string> directionlist = new List<string>();
                directionlist.Add(Enum.GetName(typeof(Optical.MeasurementType), type));
                directionlist.Add(Enum.GetName(typeof(Optical.ScatterDetectionDefinition), direction));

                this.direction = new List<List<string>>();
                this.direction.Add(directionlist);
            }                        

            public List<List<string>> direction { get; set; }
        }

        public class Results
        {
            public double value { get; set; }
            public Results(double value)
            {
                this.value = value;
            }
        }

        public class Origin
        {
            public Method method { get; set; }
        }

        public class Method
        {
            public string id { get; set; }
            public Reference reference { get; set; }
        }

        public class Reference
        {
            public Standard standard { get; set; }
        }

        public class Standard
        {
            public string[] standardizerIds { get; set; }
            public Numeration numeration { get; set; }
        }

        public class Numeration
        {
            public int mainNumber { get; set; }
        }
    }

}
