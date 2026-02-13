import json  # https://docs.python.org/3/library/json.html
import jsonschema  # https://python-jsonschema.readthedocs.io/en/stable/validate/
import rdflib  # https://rdflib.readthedocs.io/en/stable/gettingstarted.html
import rdflib.compare
import click  # https://click.palletsprojects.com/en/7.x/#documentation
import collections
import inspect
import logging
import abc
import enum
from typing import (
    Any,
    Iterable,
    Generic,
    TypeVar,
    TextIO,
    Union,
    List,
    Dict,
    Optional,
    Callable,
    Mapping,
    cast,
)

# Inspired by http://code.activestate.com/recipes/412603-stack-based-indentation-of-formatted-logging/
# See also http://code.activestate.com/recipes/411791-automatic-indentation-of-output-based-on-frame-sta/
class _IndentLoggingFormatter(logging.Formatter):
    """Makes the named placeholders ``indent`` and ``function`` usable in
    format strings, where ``indent`` is an even number of spaces, two for
    each entry on the call stack, and ``function`` is the name of the top most
    function on the call stack.

    For all other named placeholders see
    https://docs.python.org/3/library/logging.html#logrecord-attributes

    Examples:
        >>> logger = logging.getLogger()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(_IndentLoggingFormatter("[%(levelname)s]%(indent)s%(function)s:%(message)s"))
        >>> logger.addHandler(handler)
        >>> logger.warning("Attention!")
    """

    def __init__(self, format: Optional[str] = None, date_format: Optional[str] = None):
        logging.Formatter.__init__(self, format, date_format)
        self._baseline = len(inspect.stack())

    def format(self, record: logging.LogRecord) -> str:
        """Extends the log record by ``indent`` and ``function`` and passes it
        to ``logging.Formatter.format``.
        """
        stack = inspect.stack()
        # TODO Subtype `LocRecord` adding the instance variables `indent` and `function` and remove the three `type: ignore` comments below.
        record.indent = "  " * (len(stack) - self._baseline)  # type: ignore
        record.function = stack[8][3]  # type: ignore
        result = super().format(record)
        del record.indent  # type: ignore
        del record.function  # type: ignore
        return result


Json = Union[int, float, str, bool, None, List["Json"], Dict[str, "Json"]]  # type: ignore
"""JSON type inspired by
https://github.com/python/typing/issues/182

Because ``mypy`` does not support recursive types, values of this type are not
properly type checked. That's why there is the magic comment ``type: ignore``.
"""

JsonSchema = Union[bool, Dict[str, Json]]  # type: ignore
"""JSON Schema type approximation.

Because ``mypy`` does neither support recursive nor dependent types, we cannot
define a proper JSON Schema type.
"""


def convert(json_schema: Json, *, name: str, verbose: bool = False) -> rdflib.Graph:
    """Convert JSON Schema to equivalent Web Ontology.

    Note that graphs can be serialized with ``rdflib.Graph.serialize`` and
    compared with ``rdflib.compare.isomorphic`` and
    ``rdflib.compare.graph_diff``. Sometimes ``rdflib.compare.isomorphic`` and
    ``rdflib.compare.graph_diff`` report that two graphs are not isomorphic
    although the triples that are said to be only in the left graph by
    ``rdflib.compare.graph_diff`` are identical to the triples that are said to
    be only in the right graph.

    Arguments:
        json_schema: The JSON Schema to convert.
        name: Name of the root JSON Schema. Must be a valid prefixed name as
            defined on https://www.w3.org/TR/turtle/#sec-iri
        verbose: Whether to print debugging output to the console.

    Returns:
        The Web Ontology.

    Raises:
        jsonschema.exceptions.SchemaError: If the JSON Schema is invalid.

    Examples:
        Boolean JSON Schemas are mapped to empty graphs, see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.4.3.2

        >>> graph = convert(True, name='x')
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='')
        ... )
        True

        >>> graph = convert(False, name='x')
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='')
        ... )
        True

        Empty JSON Schemas are mapped to empty graphs, confer
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.4.3.5

        >>> graph = convert({}, name='x')
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='')
        ... )
        True

        A namespace is added for the canonical URI of a JSON Schema, see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.8.2.2

        >>> graph = convert({'$id': 'https://greenpeace.org#'}, name='x')
        >>> ('', rdflib.term.URIRef('https://greenpeace.org#')) in graph.namespaces()
        True

        Each scalar type except ``null`` is mapped to its corresponding XML
        Schema Definition type, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.1
        and
        https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://amnesty.org#',
        ...         'type': 'boolean',
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://amnesty.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:boolean .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://oxfam.org#',
        ...         'type': 'number',
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://oxfam.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://wwf.org#',
        ...         'type': 'integer',
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://wwf.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:int .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://350.org#',
        ...         'type': 'string',
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://350.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string .
        ...     ''')
        ... )
        True

        Validation keywords for scalar types are mapped to data-type
        restrictions, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1
        For numeric types, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.2

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://weforum.org#',
        ...         'type': 'number',
        ...         'exclusiveMinimum': -42,
        ...         'exclusiveMaximum': 42,
        ...     },
        ...     name='x'
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://weforum.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double ;
        ...             owl:withRestrictions ( [ xsd:maxExclusive 4.2e+01 ] [ xsd:minExclusive -4.2e+01 ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://weforum.org#',
        ...         'type': 'integer',
        ...         'minimum': 0,
        ...         'maximum': 7,
        ...     },
        ...     name='x'
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://weforum.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:int ;
        ...             owl:withRestrictions ( [ xsd:maxInclusive 7e+00 ] [ xsd:minInclusive 0e+00 ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        For string types, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.3

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://gcint.org#',
        ...         'type': 'string',
        ...         'maxLength': 265,
        ...         'minLength': 32,
        ...         'pattern': 'a+'
        ...     },
        ...     name='x'
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://gcint.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:maxLength 2.65e+02 ] [ xsd:minLength 3.2e+01 ] [ xsd:pattern "a+"^^xsd:string ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        Defined string formats are mapped to restrictions or corresponding XML
        Schema Definition types, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3
        and
        https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes

        For dates, times, and durations see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.1

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'date-time',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:dateTime .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'date',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:date .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'time',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:time .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'duration',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:duration .
        ...     ''')
        ... )
        True

        For email addresses see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.2

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'email',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "[\\\\\\\\w!#$%&\\'*+/=?`{|}~^-]+(?:\\\\\\\\.[\\\\\\\\w!#$%&\\'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\\\\\\\\.)+[A-Z]{2,6}"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'idn-email',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "[\\\\\\\\w!#$%&\\'*+/=?`{|}~^-]+(?:\\\\\\\\.[\\\\\\\\w!#$%&\\'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\\\\\\\\.)+[A-Z]{2,6}"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        For hostnames see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.3

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'hostname',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "([a-z0-9]+(-[a-z0-9]+)*\\\\\\\\.)+[a-z]{2,}"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'idn-hostname',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "\\\\\\\\b((xn--)?[a-z0-9]+(-[a-z0-9]+)*\\\\\\\\.)+[a-z]{2,}\\\\\\\\b"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        For IP addresses see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.4

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'ipv4',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\\\\\\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'ipv6',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        For resource identifiers see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.5

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'uri',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:anyURI .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'uri-reference',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:anyURI .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'iri',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:anyURI .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'iri-reference',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:anyURI .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'uuid',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string ;
        ...             owl:withRestrictions ( [ xsd:pattern "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"^^xsd:string ] ) .
        ...     ''')
        ... )
        True

        For URI templates see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.6

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'uri-template',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string .
        ...     ''')
        ... )
        True

        For JSON pointers see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.7

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'json-pointer',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'relative-json-pointer',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string .
        ...     ''')
        ... )
        True

        For regular expressions see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.8

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://this-is-my-earth.org#',
        ...         'type': 'string',
        ...         'format': 'regex',
        ...     },
        ...     name='x'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://this-is-my-earth.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a rdfs:Datatype ;
        ...             owl:onDatatype xsd:string .
        ...     ''')
        ... )
        True

        Objects are mapped to classes with corresponding optional properties,
        see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.9.3.2.1

        >>> graph = convert({'$id': 'https://www.worldlandtrust.org#', 'type': 'object'}, name='x')
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://www.worldlandtrust.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...
        ...         :x a owl:Class .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': { 'type': 'number' },
        ...             'y': { 'type': 'integer' },
        ...             'name': { 'type': 'string' },
        ...             'registered': { 'type': 'boolean' },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point_name a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:string .
        ...
        ...         :point_registered a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:boolean .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:double .
        ...
        ...         :point_y a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:int .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_registered ],
        ...                 [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ],
        ...                 [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_name ],
        ...                 [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_y ] .
        ...     ''')
        ... )
        True

        Properties can be made required, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.5

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'type': 'number',
        ...             },
        ...             'y': {
        ...                 'type': 'number',
        ...             },
        ...         },
        ...         'required': ['x', 'y'],
        ...     },
        ...     name='point',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:double .
        ...
        ...         :point_y a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:double .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:cardinality 1 ;
        ...                     owl:onProperty :point_x ],
        ...                 [ a owl:Restriction ;
        ...                     owl:cardinality 1 ;
        ...                     owl:onProperty :point_y ] .
        ...     ''')
        ... )
        True

        Nullable properties are optional (even if required).

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'type': ['number', 'null'],
        ...             },
        ...         },
        ...         'required': ['x'],
        ...     },
        ...     name='point',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range xsd:double .
        ...     ''')
        ... )
        True

        Property value restrictions are mapped to data sub-types with
        restrictions.

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'type': 'number',
        ...                 'exclusiveMinimum': -42,
        ...                 'exclusiveMaximum': 42,
        ...             },
        ...             'y': {
        ...                 'type': 'integer',
        ...                 'minimum': 0,
        ...                 'maximum': 7,
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double ;
        ...             owl:withRestrictions ( [ xsd:maxExclusive 4.2e+01 ] [ xsd:minExclusive -4.2e+01 ] ) .
        ...
        ...         :point_y a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_y_range .
        ...
        ...         :point_y_range a rdfs:Datatype ;
        ...             owl:onDatatype xsd:int ;
        ...             owl:withRestrictions ( [ xsd:maxInclusive 7e+00 ] [ xsd:minInclusive 0e+00 ] ) .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ],
        ...                 [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_y ] .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        The union of multiple types is itself a type, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.1

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://oxfam.org#',
        ...         'type': ['number', 'string', 'boolean'],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://oxfam.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:unionOf ( xsd:double xsd:string xsd:boolean ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://oxfam.org#',
        ...         'type': ['number', 'object'],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://oxfam.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:unionOf ( xsd:double [ a owl:Class ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'type': ['integer', 'string'],
        ...                 'exclusiveMinimum': -42,
        ...                 'minLength': 7,
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:unionOf ( [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:int ;
        ...                         owl:withRestrictions ( [ xsd:minExclusive -4.2e+01 ] ) ] [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:string ;
        ...                         owl:withRestrictions ( [ xsd:minLength 7e+00 ] ) ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        Validation keywords only restrict the types to which they are
        applicable, see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.7.6.1
        (this semantic is also expressed by the wording 'If the instance is
        a number ...' of the validation keyword maximum, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.2.2
        and similar of other such keywords).

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': ['number', 'string'],
        ...         'maximum': 3,
        ...         'minLength': 7,
        ...         'required': ['x'],
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             owl:unionOf ( [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:double ;
        ...                         owl:withRestrictions ( [ xsd:maxInclusive 3e+00 ] ) ] [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:string ;
        ...                         owl:withRestrictions ( [ xsd:minLength 7e+00 ] ) ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': ['number', 'object'],
        ...         'properties': {
        ...             'x': {
        ...                 'type': 'number',
        ...                 'exclusiveMinimum': -42,
        ...                 'exclusiveMaximum': 42,
        ...             },
        ...             'y': {
        ...                 'type': 'integer',
        ...             },
        ...         },
        ...         'required': ['x'],
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             owl:unionOf ( xsd:double _:anonymous_point_object ) .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain _:anonymous_point_object ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double ;
        ...             owl:withRestrictions ( [ xsd:maxExclusive 4.2e+01 ] [ xsd:minExclusive -4.2e+01 ] ) .
        ...
        ...         :point_y a owl:ObjectProperty ;
        ...             rdfs:domain _:anonymous_point_object ;
        ...             rdfs:range xsd:int .
        ...
        ...         _:anonymous_point_y_restriction a owl:Restriction ;
        ...             owl:maxCardinality 1 ;
        ...             owl:onProperty :point_y .
        ...
        ...         _:anonymous_point_x_restriction a owl:Restriction ;
        ...             owl:cardinality 1 ;
        ...             owl:onProperty :point_x .
        ...
        ...         _:anonymous_point_object a owl:Class ;
        ...             rdfs:subClassOf _:anonymous_point_y_restriction,
        ...                 _:anonymous_point_x_restriction .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        Possible values can be enumerated, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.2

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://nabu.de#',
        ...         'enum': [2, 3, 5, 7, 11, 13],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://nabu.de#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:oneOf ( 2 3 5 7 11 13 ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'enum': [0, 1, 2, 3, 4, 5],
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:oneOf ( 0 1 2 3 4 5 ) .
        ...     ''')
        ... )
        True

        Possible values can be restricted to exactly one value, a constant, see
        https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.3

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://fzs.org#',
        ...         'const': 1024,
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://fzs.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:oneOf ( 1024 ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'const': 42,
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:oneOf ( 42 ) .
        ...     ''')
        ... )
        True

        Definitions can be referenced, see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.8.2.5

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://foei.org#',
        ...         '$ref': '#/definitions/n',
        ...         'definitions': {
        ...             'n': { 'type': 'number' }
        ...         },
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://foei.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             rdfs:subClassOf :x_n .
        ...
        ...         :x_n a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://footprintnetwork.org#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 '$ref': '#/definitions/coordinate',
        ...             },
        ...         },
        ...         'definitions': {
        ...             'coordinate': {
        ...                 'type': 'number',
        ...             },
        ...         },
        ...     },
        ...     name='point'
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://footprintnetwork.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xml: <http://www.w3.org/XML/1998/namespace> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_coordinate a rdfs:Datatype ;
        ...             owl:onDatatype xsd:double .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_coordinate .
        ...     ''')
        ... )
        True

        Subschemas with boolean logic, namely, ``allOf``, ``anyOf``, ``oneOf``, and
        ``not`` are mapped to ``intersectionOf``, ``unionOf``, ``disjointUnionOf``, and
        ``complementOf``, see
        https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.9.2.1

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://goodplanet.org#',
        ...         'allOf': [
        ...             { 'type': 'integer' },
        ...             { 'const': 0 },
        ...         ],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://goodplanet.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:intersectionOf ( xsd:int [ a owl:Class ;
        ...                         owl:oneOf ( 0 ) ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://goodplanet.org#',
        ...         'anyOf': [
        ...             { 'type': 'string' },
        ...             { 'enum': [0, 1] },
        ...         ],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://goodplanet.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:unionOf ( xsd:string [ a owl:Class ;
        ...                         owl:oneOf ( 0 1 ) ] ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://goodplanet.org#',
        ...         'oneOf': [
        ...             { 'type': 'boolean' },
        ...             { 'type': 'string' },
        ...         ],
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://goodplanet.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:disjointUnionOf ( xsd:boolean xsd:string ) .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://goodplanet.org#',
        ...         'not': { 'type': 'boolean' },
        ...     },
        ...     name='x',
        ... )
        >>> rdflib.compare.isomorphic(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://goodplanet.org#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :x a owl:Class ;
        ...             owl:complementOf xsd:boolean .
        ...     ''')
        ... )
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'allOf': [
        ...                     {
        ...                         'type': ['integer', 'string']
        ...                     },
        ...                     {
        ...                         'enum': [0, 2, 4, 6, 'a', 'b']
        ...                     },
        ...                     {
        ...                         'type': 'string',
        ...                         'maxLength': 7,
        ...                     },
        ...                 ],
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:intersectionOf ( [ a owl:Class ;
        ...                         owl:unionOf ( xsd:int xsd:string ) ] [ a owl:Class ;
        ...                         owl:oneOf ( 0 2 4 6 "a" "b" ) ] [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:string ;
        ...                         owl:withRestrictions ( [ xsd:maxLength 7e+00 ] ) ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'anyOf': [
        ...                     {
        ...                         'type': ['integer', 'string']
        ...                     },
        ...                     {
        ...                         'enum': [0, 2, 4, 6, 'a', 'b']
        ...                     },
        ...                     {
        ...                         'type': 'string',
        ...                         'maxLength': 7,
        ...                     },
        ...                 ],
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:unionOf ( [ a owl:Class ;
        ...                         owl:unionOf ( xsd:int xsd:string ) ] [ a owl:Class ;
        ...                         owl:oneOf ( 0 2 4 6 "a" "b" ) ] [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:string ;
        ...                         owl:withRestrictions ( [ xsd:maxLength 7e+00 ] ) ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'oneOf': [
        ...                     {
        ...                         'type': ['integer', 'string']
        ...                     },
        ...                     {
        ...                         'enum': [0, 2, 4, 6, 'a', 'b']
        ...                     },
        ...                     {
        ...                         'type': 'string',
        ...                         'maxLength': 7,
        ...                     },
        ...                 ],
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:disjointUnionOf ( [ a owl:Class ;
        ...                         owl:unionOf ( xsd:int xsd:string ) ] [ a owl:Class ;
        ...                         owl:oneOf ( 0 2 4 6 "a" "b" ) ] [ a rdfs:Datatype ;
        ...                         owl:onDatatype xsd:string ;
        ...                         owl:withRestrictions ( [ xsd:maxLength 7e+00 ] ) ] ) .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True

        >>> graph = convert(
        ...     {
        ...         '$id': 'https://point.com#',
        ...         'type': 'object',
        ...         'properties': {
        ...             'x': {
        ...                 'not': {
        ...                     'oneOf': [
        ...                         {
        ...                             'type': ['integer', 'string']
        ...                         },
        ...                         {
        ...                             'enum': [0, 2, 4, 6, 'a', 'b']
        ...                         },
        ...                         {
        ...                             'type': 'string',
        ...                             'maxLength': 7,
        ...                         },
        ...                     ],
        ...                 },
        ...             },
        ...         },
        ...     },
        ...     name='point',
        ... )
        >>> in_both, in_left, in_right = rdflib.compare.graph_diff(graph,
        ...     rdflib.Graph().parse(format='turtle', data='''
        ...         @prefix : <https://point.com#> .
        ...         @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ...         @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ...         @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        ...
        ...         :point a owl:Class ;
        ...             rdfs:subClassOf [ a owl:Restriction ;
        ...                     owl:maxCardinality 1 ;
        ...                     owl:onProperty :point_x ] .
        ...
        ...         :point_x a owl:ObjectProperty ;
        ...             rdfs:domain :point ;
        ...             rdfs:range :point_x_range .
        ...
        ...         :point_x_range a owl:Class ;
        ...             owl:complementOf [ a owl:Class ;
        ...                     owl:disjointUnionOf ( [ a owl:Class ;
        ...                                 owl:unionOf ( xsd:int xsd:string ) ] [ a owl:Class ;
        ...                                 owl:oneOf ( 0 2 4 6 "a" "b" ) ] [ a rdfs:Datatype ;
        ...                                 owl:onDatatype xsd:string ;
        ...                                 owl:withRestrictions ( [ xsd:maxLength 7e+00 ] ) ] ) ] .
        ...     ''')
        ... )
        >>> in_left.serialize(format='turtle') == in_right.serialize(format='turtle')
        True
    """
    # sno/\\n/\\\\n\\\r/
    return _SchemaConverter(json_schema, name=name, verbose=verbose).convert()


class _Identification(enum.Enum):
    """Specifies how and whether some part of a JSON Schema shall be
    identifiable after conversion to a Web Ontology.

    ```_Identification.NEW_NAME``` means that a new named identifier shall be
    used, ```_Identification.SOME_NAME``` means that some named identifier shall
    be (re)used, and ```_Identification.ANONYMOUS``` means that the part does
    not have to be identifiable by name.
    """

    NEW_NAME = 'NEW_NAME'
    SOME_NAME = 'SOME_NAME'
    ANONYMOUS = 'ANONYMOUS'


class _Converter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def convert_subschema(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        """Converts the given JSON sub-Schema reached by the given path to
        a Web Ontology by adding corresponding triples to ``_Converter.graph``
        and returns its identifier.

        If the conversion result shall be identifiable by name, the
        ``_Converter.namespace`` together with the given path are used to
        generate a fresh named identifier. If the result shall be identifiable
        by some name, then, if possible, an already named identifier is reused
        and, if not, a fresh named identifier is generated as above. And, if
        the result can be anonymous, then, if possible, no new identifier is
        created at all, and if impossible, a fresh blank node is used.

        Args:
            path: Essentially the list of keys traversed to reach the JSON
                sub-Schema.
            subschema: The JSON sub-Schema.
            identification: How the conversion result shall be identifiable.

        Returns:
            The identifier of the conversion result.
        """
        pass

    @property
    @abc.abstractmethod
    def graph(self) -> rdflib.Graph:
        """The graph that is going to be the conversion result."""
        pass

    @property
    @abc.abstractmethod
    def namespace(self) -> rdflib.Namespace:
        """The namespace of the generated ontology."""
        pass

    @property
    @abc.abstractmethod
    def logger(self) -> logging.Logger:
        """The logger to use to log information about the conversion process."""
        pass


class _SchemaConverter(_Converter):
    def __init__(self, json_schema: Json, *, name: str, verbose: bool = False) -> None:
        jsonschema.Draft7Validator.check_schema(
            json_schema
        )  # TODO Use the possibly existing key $schema of `json_schema` to determine the validator. See https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.8.1.1
        self._json_schema = json_schema
        self._name = name
        self._logger = _SchemaConverter._make_logger(verbose)
        self._subschema_converter = _SubschemaConverter(self)
        self._graph = None
        self._namespace = None

    @staticmethod
    def _make_logger(verbose: bool) -> logging.Logger:
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        handler.setFormatter(
            _IndentLoggingFormatter("%(indent)s%(message)s")
        )  # For further attributes see https://docs.python.org/3/library/logging.html#logrecord-attributes
        logger.addHandler(handler)
        if verbose:
            logger.setLevel(logging.DEBUG)
        return logger

    def convert(self) -> rdflib.Graph:
        """Converts the JSON Schema given during construction of this instance to
        a Web Ontology and returns the conversion result as graph.

        Returns:
            The conversion result.
        """
        self.logger.debug("Converting JSON Schema")
        self._graph = rdflib.Graph()
        if isinstance(
            self._json_schema, collections.abc.Mapping
        ):  # See https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python#comment96539974_25232010
            # TODO Draft 2019-09 uses `$defs` and forbids nesting, see https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.8.2.5
            # TODO Schema identification is more complicated, see https://json-schema.org/draft/2019-09/json-schema-core.html#idExamples
            self._namespace = rdflib.Namespace(self._json_schema.get("$id", ""))
            self.graph.bind(
                "", self.namespace, override=False
            )  # TODO I'd like to use @base instead, but how with rdflib? See https://www.w3.org/TR/turtle/#relative-iri
            self.graph.bind("owl", rdflib.OWL, override=False)
            if self._subschema_converter.applicable(self._json_schema):
                self._subschema_converter.convert(
                    path=[self._name], subschema=self._json_schema, identification=_Identification.NEW_NAME
                )
        return self.graph

    def convert_subschema(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        """See ``_Converter.convert_subschema``"""
        return self._subschema_converter.convert(
            path=path, subschema=subschema, identification=identification
        )

    @property
    def graph(self) -> rdflib.Graph:
        """See ``_Converter.graph``"""
        return self._graph

    @property
    def namespace(self) -> rdflib.Namespace:
        """See ``_Converter.namespace``"""
        return self._namespace

    @property
    def logger(self) -> logging.Logger:
        """See ``_Converter.logger``"""
        return self._logger


class _ChildConverter(_Converter, metaclass=abc.ABCMeta):
    def __init__(self, parent_converter: _Converter) -> None:
        self._parent_converter = parent_converter

    def convert_subschema(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        """Invokes ``_Converter.convert_subschema`` on its parent converter."""
        return self._parent_converter.convert_subschema(
            path=path, subschema=subschema, identification=identification
        )

    @property
    def graph(self) -> rdflib.Graph:
        """Invokes ``_Converter.graph`` on its parent converter."""
        return self._parent_converter.graph

    @property
    def namespace(self) -> rdflib.Namespace:
        """Invokes ``_Converter.namepsace`` on its parent converter."""
        return self._parent_converter.namespace

    @property
    def logger(self) -> logging.Logger:
        """Invokes ``_Converter.logger`` on its parent converter."""
        return self._parent_converter.logger

    def _make_identifier(
        self, path: List[str], *, identification: _Identification
    ) -> rdflib.term.Identifier:
        # For a list of allowed characters see
        # https://stackoverflow.com/questions/2849756/list-of-valid-characters-for-the-fragment-identifier-in-an-url/2849800#2849800
        # I chose `_` because it works well with prefixed names, see
        # https://www.w3.org/TR/turtle/#sec-iri
        # However, because `_` is allowed in JSON keys, using `_` here may
        # produce naming conflicts. This is not a problem for schemas that
        # only use camel-case key names.
        # TODO Find a solution that works in all cases. The character `/` is allowed, should not cause conflicts with JSON but does not work well with prefixed names.
        # Best Practice Recipes for Publishing RDF Vocabularies: https://www.w3.org/TR/swbp-vocab-pub/
        if identification == _Identification.ANONYMOUS:
            return rdflib.BNode()
        return self.namespace["_".join(path)]

    def _make_collection(
        self, items: Iterable[rdflib.term.Identifier]
    ) -> rdflib.term.Identifier:
        b_node = rdflib.BNode()
        rdflib.collection.Collection(self.graph, b_node, items)
        return b_node


class _SubschemaConverterBase(_ChildConverter, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def applicable(self, subschema: JsonSchema) -> bool:
        """Whether this converter is applicable to the given JSON sub-Schema.
        """
        pass

    @abc.abstractmethod
    def convert(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        """Converts the given JSON sub-Schema reached by the given path to
        a Web Ontology by adding corresponding triples to ``_Converter.graph``
        and returns its identifier.

        If the conversion result shall be identifiable by name, the
        ``_Converter.namespace`` together with the given path are used to
        generate a fresh named identifier. If the result shall be identifiable
        by some name, then, if possible, an already named identifier is reused
        and, if not, a fresh named identifier is generated as above. And, if
        the result can be anonymous, then, if possible, no new identifier is
        created at all, and if impossible, a fresh blank node is used.

        Args:
            path: Essentially the list of keys traversed to reach the JSON
                sub-Schema.
            subschema: The JSON sub-Schema.
            identification: How the conversion result shall be identifiable.

        Returns:
            The identifier of the conversion result.

        Raises:
            AssertionError: If this converter is not applicable to the given JSON
                sub-Schema.
        """
        pass


class _ObjectSubschemaConverterBase(_SubschemaConverterBase, metaclass=abc.ABCMeta):
    def applicable(self, subschema: JsonSchema) -> bool:
        """Whether the given JSON sub-Schema is a JSON object and
        ``_ObjectSubschemaConverterBase.applicable_to_object_subschema`` holds.

        See ``_SubschemaConverterBase.applicable``.
        """
        return isinstance(subschema, dict) and self.applicable_to_object_subschema(
            subschema
        )

    @abc.abstractmethod
    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        """Whether this converter is applicable to the given object JSON
        sub-Schema.
        """
        pass

    def convert(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        """Converts the given JSON sub-Schema by asserting
        ``_ObjectSubschemaConverterBase.applicable`` before invoking
        ``_ObjectSubschemaConverterBase.convert_object_subschema``.

        See ``_SubschemaConverterBase.convert``.
        """
        self.logger.debug("Converting JSON sub-Schema '{}'".format(path))
        assert self.applicable(subschema)
        return self.convert_object_subschema(
            path=path, subschema=cast(Dict[str, Json], subschema), identification=identification
        )

    @abc.abstractmethod
    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        """Converts the given object JSON sub-Schema reached by the given path
        to a Web Ontology by adding corresponding triples to ``_Converter.graph``
        and returns its identifier.

        If the conversion result shall be identifiable by name, the
        ``_Converter.namespace`` together with the given path are used to
        generate a fresh named identifier. If the result shall be identifiable
        by some name, then, if possible, an already named identifier is reused
        and, if not, a fresh named identifier is generated as above. And, if
        the result can be anonymous, then, if possible, no new identifier is
        created at all, and if impossible, a fresh blank node is used.

        Args:
            path: Essentially the list of keys traversed to reach the JSON
                sub-Schema.
            subschema: The JSON sub-Schema.
            identification: How the conversion result shall be identifiable.

        Returns:
            The identifier of the conversion result.
        """
        pass


class _SubschemaConverter(_SubschemaConverterBase):
    def __init__(self, schema_converter: _SchemaConverter) -> None:
        super().__init__(schema_converter)
        self._converters = (
            _ReferenceSubschemaConverter(self),
            _BooleanLogicSubschemaConverter(self),
            _TypeSubschemaConverter(self),
            _EnumerationSubschemaConverter(self),
            _ConstantSubschemaConverter(self),
        )

    def applicable(self, subschema: JsonSchema) -> bool:
        return isinstance(subschema, bool) or any(
            converter.applicable(subschema) for converter in self._converters
        )

    def convert(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        assert self.applicable(subschema)
        self.logger.debug("Converting JSON sub-Schema '{}'".format(path))
        if isinstance(subschema, bool):
            return self._convert_boolean_subschema(
                path=path, subschema=subschema, identification=identification
            )
        return self._convert_object_subschema(
            path=path, subschema=subschema, identification=identification
        )

    def _convert_boolean_subschema(
        self, *, path: List[str], subschema: bool, identification: _Identification
    ) -> rdflib.term.Identifier:
        if not subschema and identification != _Identification.NEW_NAME:
            return rdflib.OWL.Nothing
        identifier = self._make_identifier(path=path, identification=identification)
        if not subschema:
            self.graph.add((identifier, rdflib.RDFS.subClassOf, rdflib.OWL.Nothing))
        return identifier

    def _convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        if "definitions" in subschema:
            # TODO Not extending the path here with `definitions` can lead to conflicts with, for example, properties of objects
            self._convert_definitions(
                path=path, definitions=cast(Dict[str, Json], subschema["definitions"])
            )
        applicable_converters = [
            converter
            for converter in self._converters
            if converter.applicable(subschema)
        ]
        subidentification = identification if len(applicable_converters) <= 1 else _Identification.ANONYMOUS
        subidentifiers = [
            converter.convert(
                path=path,
                subschema=subschema,
                identification=subidentification,
            )
            for converter in applicable_converters
        ]
        if len(subidentifiers) == 1:
            return subidentifiers[0]
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.RDFS.Class))
        self.graph.add(
            (
                identifier,
                rdflib.OWL.intersectionOf,
                self._make_collection(subidentifiers),
            )
        )
        return identifier

    def _convert_definitions(
        self, *, path: List[str], definitions: Dict[str, Json]
    ) -> None:
        self.logger.debug("Converting definitions {}".format(path))
        for key, value in definitions.items():
            if isinstance(value, dict):
                # TODO Find a more robust way to decide whether `value` is itself
                #      a definition or a container of definitions.
                if "type" in value or "$ref" in value or "oneOf" in value:
                    self.convert(path=path + [key], subschema=value, identification=_Identification.NEW_NAME)
                else:
                    self._convert_definitions(path=path + [key], definitions=value)
            elif key != "title":
                raise NotImplementedError("Not implemented")


class _ReferenceSubschemaConverter(_ObjectSubschemaConverterBase):
    KEY = "$ref"

    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return _ReferenceSubschemaConverter.KEY in subschema

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        parent = self._convert_reference(
            cast(str, subschema[_ReferenceSubschemaConverter.KEY]),
            schema_name=path[0],  # TODO This is error-prone.
        )
        if identification != _Identification.NEW_NAME:
            return parent
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        self.graph.add((identifier, rdflib.RDFS.subClassOf, parent))
        return identifier

    def _convert_reference(self, reference: str, *, schema_name: str) -> rdflib.URIRef:
        if reference.startswith("#/definitions/"):
            return self._make_identifier(
                [schema_name] + reference[14:].split("/"), identification=_Identification.NEW_NAME
            )
        raise NotImplementedError("Not implemented")


# https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.2
class _EnumerationSubschemaConverter(_ObjectSubschemaConverterBase):
    KEY = "enum"

    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return _EnumerationSubschemaConverter.KEY in subschema

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        values = (
            rdflib.Literal(value)
            for value in cast(List[Json], subschema[_EnumerationSubschemaConverter.KEY])
        )
        self.graph.add((identifier, rdflib.OWL.oneOf, self._make_collection(values)))
        return identifier


# https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.3
class _ConstantSubschemaConverter(_ObjectSubschemaConverterBase):
    KEY = "const"

    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return _ConstantSubschemaConverter.KEY in subschema

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        # TODO Can constants be represented more concisely?
        value = rdflib.Literal(subschema[_ConstantSubschemaConverter.KEY])
        self.graph.add((identifier, rdflib.OWL.oneOf, self._make_collection([value])))
        return identifier


# https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.9.2.1
class _BooleanLogicSubschemaConverter(_ObjectSubschemaConverterBase):
    # Note that the order of elements in sets is not preserved, in other words, sets are unstable, see https://docs.python.org/3/tutorial/datastructures.html#sets
    KEYS = {"allOf", "anyOf", "oneOf", "not"}

    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return any(key in subschema for key in _BooleanLogicSubschemaConverter.KEYS)

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        if "allOf" in subschema:
            return self._convert_x_of_subschema(
                path=path,
                subschema=cast(List[Json], subschema["allOf"]),
                x_of_predicate=rdflib.OWL.intersectionOf,
                identification=identification,
            )
        if "anyOf" in subschema:
            return self._convert_x_of_subschema(
                path=path,
                subschema=cast(List[Json], subschema["anyOf"]),
                x_of_predicate=rdflib.OWL.unionOf,
                identification=identification,
            )
        if "oneOf" in subschema:
            return self._convert_x_of_subschema(
                path=path,
                subschema=cast(List[Json], subschema["oneOf"]),
                x_of_predicate=rdflib.OWL.disjointUnionOf,
                identification=identification,
            )
        if "not" in subschema:
            return self._convert_not_subschema(
                path=path,
                subschema=cast(JsonSchema, subschema["not"]),
                identification=identification,
            )
        raise ValueError

    def _convert_x_of_subschema(
        self,
        *,
        path: List[str],
        subschema: List[Json],
        x_of_predicate: rdflib.term.Identifier,
        identification: _Identification,
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        x_of_identifiers = [
            self.convert_subschema(
                path=path + [str(i)],
                subschema=cast(JsonSchema, x_of_subschema),
                identification=_Identification.ANONYMOUS,
            )
            for i, x_of_subschema in enumerate(subschema)
        ]
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        self.graph.add(
            (identifier, x_of_predicate, self._make_collection(x_of_identifiers))
        )
        return identifier

    def _convert_not_subschema(
        self, *, path: List[str], subschema: JsonSchema, identification: _Identification
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        self.graph.add(
            (
                identifier,
                rdflib.OWL.complementOf,
                self.convert_subschema(
                    path=path + ["0"], subschema=subschema, identification=_Identification.ANONYMOUS,
                ),
            )
        )
        return identifier


# https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.1
class _TypeSubschemaConverter(_ObjectSubschemaConverterBase):
    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)
        self._converters = {
            _ArrayTypeSubschemaConverter.TYPE: _ArrayTypeSubschemaConverter(self),
            _BooleanTypeSubschemaConverter.TYPE: _BooleanTypeSubschemaConverter(self),
            _IntegerTypeSubschemaConverter.TYPE: _IntegerTypeSubschemaConverter(self),
            _NumberTypeSubschemaConverter.TYPE: _NumberTypeSubschemaConverter(self),
            _ObjectTypeSubschemaConverter.TYPE: _ObjectTypeSubschemaConverter(self),
            _StringTypeSubschemaConverter.TYPE: _StringTypeSubschemaConverter(self),
        }

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return "type" in subschema and any(
            converter.applicable(subschema) for converter in self._converters.values()
        )

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        types = self._extract_non_null_types(
            cast(Union[str, List[str]], subschema["type"])
        )
        if len(types) == 1:
            return self._one_type_convert(
                path=path, type=types[0], subschema=subschema, identification=identification
            )
        return self._none_or_multiple_types_convert(
            path=path, types=types, subschema=subschema, identification=identification
        )

    def _extract_non_null_types(
        self, type_or_types: Union[str, List[str]]
    ) -> List[str]:
        types = type_or_types if isinstance(type_or_types, list) else [type_or_types]
        return [type for type in types if type != "null"]

    def _none_or_multiple_types_convert(
        self,
        *,
        path: List[str],
        types: List[str],
        subschema: Dict[str, Json],
        identification: _Identification,
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        subidentifiers = (
            self._one_type_convert(
                path=path, type=type, subschema=subschema, identification=_Identification.ANONYMOUS
            )
            for type in types
        )
        if subidentifiers:
            self.graph.add(
                (identifier, rdflib.OWL.unionOf, self._make_collection(subidentifiers))
            )
        return identifier

    def _one_type_convert(
        self, *, path: List[str], type: str, subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        # JSON Schema primitive types: https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.4.2.1
        # OWL 2 built-in types: https://www.w3.org/TR/2012/REC-owl2-quick-reference-20121211/#Built-in_Datatypes
        return self._converters[type].convert(
            path=path, subschema=subschema, identification=identification
        )


ValueTypeVar = TypeVar("ValueTypeVar")


class _ValidationKeywordConverter(_ChildConverter, Generic[ValueTypeVar]):
    def __init__(
        self,
        parent_converter: _Converter,
        *,
        restriction_predicate: rdflib.term.Identifier,
        object_type: rdflib.term.Identifier,
        value_converter: Optional[Callable[[ValueTypeVar], ValueTypeVar]] = None,
    ) -> None:
        super().__init__(parent_converter)
        self._restriction_predicate = restriction_predicate
        self._object_type = object_type
        self._value_converter = value_converter

    def convert(self, value: ValueTypeVar) -> rdflib.term.Identifier:
        self.logger.debug("Converting value '{}'".format(value))
        restriction_object = rdflib.BNode()
        converted_value = (
            value if self._value_converter is None else self._value_converter(value)
        )
        self.graph.add(
            (
                restriction_object,
                self._restriction_predicate,
                rdflib.Literal(converted_value, datatype=self._object_type),
            )
        )
        return restriction_object


# See https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.1
class _TypeSubschemaConverterBase(_ObjectSubschemaConverterBase, metaclass=abc.ABCMeta):
    def __init__(
        self, object_subschema_converter: _ObjectSubschemaConverterBase, *, type: str
    ) -> None:
        super().__init__(object_subschema_converter)
        self._type = type

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return "type" in subschema and (
            (isinstance(subschema["type"], str) and subschema["type"] == self._type)
            or (isinstance(subschema["type"], list) and self._type in subschema["type"])
        )


class _ScalarTypeSubschemaConverterBase(
    _TypeSubschemaConverterBase, metaclass=abc.ABCMeta
):
    def __init__(
        self,
        object_subschema_converter: _ObjectSubschemaConverterBase,
        *,
        type: str,
        data_type: rdflib.term.Identifier,
        pattern: Optional[str] = None,
        validation_keyword_converters: Mapping[str, _ValidationKeywordConverter[Any]],
    ) -> None:
        super().__init__(object_subschema_converter, type=type)
        self._data_type = data_type
        self._pattern = pattern
        self._validation_keyword_converters = validation_keyword_converters
        if self._pattern:
            self._pattern_converter = _ValidationKeywordConverter(
                self,
                restriction_predicate=rdflib.XSD.pattern,
                object_type=rdflib.XSD.string,
            )  #  type: _ValidationKeywordConverter[str]

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        if identification == _Identification.NEW_NAME or any(
            k in subschema for k in self._validation_keyword_converters.keys()
        ):
            data_subtype = self._make_data_subtype(
                path=path, super_type=self._data_type, identification=identification
            )
            self._restrict_data_subtype(data_subtype, subschema=subschema)
            return data_subtype
        return self._data_type

    def _make_data_subtype(
        self, *, path: List[str], super_type: rdflib.term.Identifier, identification: _Identification
    ) -> rdflib.term.Identifier:
        data_subtype = self._make_identifier(path, identification=identification)
        self.graph.add((data_subtype, rdflib.RDF.type, rdflib.RDFS.Datatype))
        self.graph.add((data_subtype, rdflib.OWL.onDatatype, super_type))
        return data_subtype

    def _restrict_data_subtype(
        self, data_subtype: rdflib.term.Identifier, *, subschema: Dict[str, Json]
    ) -> None:
        restrictions = []
        if self._pattern:
            restrictions.append(self._pattern_converter.convert(self._pattern))
        for keyword, converter in self._validation_keyword_converters.items():
            if keyword in subschema:
                restrictions.append(converter.convert(subschema[keyword]))
        if restrictions:
            self.graph.add(
                (
                    data_subtype,
                    rdflib.OWL.withRestrictions,
                    self._make_collection(restrictions),
                )
            )


# See https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.1.1
class _BooleanTypeSubschemaConverter(_ScalarTypeSubschemaConverterBase):
    TYPE = "boolean"

    def __init__(self, type_subschema_converter: _TypeSubschemaConverter) -> None:
        super().__init__(
            type_subschema_converter,
            type=_BooleanTypeSubschemaConverter.TYPE,
            data_type=rdflib.XSD.boolean,
            validation_keyword_converters={},
        )


# See https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.2
class _NumericTypeSubschemaConverter(
    _ScalarTypeSubschemaConverterBase, metaclass=abc.ABCMeta
):
    def __init__(
        self,
        type_subschema_converter: _TypeSubschemaConverter,
        *,
        type: str,
        data_type: rdflib.term.Identifier,
    ) -> None:
        super().__init__(
            type_subschema_converter,
            type=type,
            data_type=data_type,
            validation_keyword_converters={
                # TODO 'multipleOf': ,
                "maximum": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.maxInclusive,
                    object_type=rdflib.XSD.double,
                ),
                "exclusiveMaximum": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.maxExclusive,
                    object_type=rdflib.XSD.double,
                ),
                "minimum": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.minInclusive,
                    object_type=rdflib.XSD.double,
                ),
                "exclusiveMinimum": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.minExclusive,
                    object_type=rdflib.XSD.double,
                ),
            },
        )


class _NumberTypeSubschemaConverter(_NumericTypeSubschemaConverter):
    TYPE = "number"

    def __init__(self, type_subschema_converter: _TypeSubschemaConverter) -> None:
        super().__init__(
            type_subschema_converter,
            type=_NumberTypeSubschemaConverter.TYPE,
            data_type=rdflib.XSD.double,
        )


class _IntegerTypeSubschemaConverter(_NumericTypeSubschemaConverter):
    TYPE = "integer"

    def __init__(self, type_subschema_converter: _TypeSubschemaConverter) -> None:
        super().__init__(
            type_subschema_converter,
            type=_IntegerTypeSubschemaConverter.TYPE,
            data_type=rdflib.XSD.int,
        )


class _StringTypeSubschemaConverter(_ObjectSubschemaConverterBase):
    TYPE = "string"

    def __init__(self, subschema_converter: _SubschemaConverterBase) -> None:
        super().__init__(subschema_converter)
        # TODO For the formats mapped to strings restricted by regular expressions I could not find a corresponding type. Are there really no such? Also the regular expressions may be incorrect.
        # For patterns we use string literals of the form `r'''...'''` so that we do not need to espace characters like `\`, `'` and `"`. For details see https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals
        self._converters = {
            None: _FixFormatStringTypeSubschemaConverter(
                self, format=None, data_type=rdflib.XSD.string
            ),
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.1
            "date-time": _FixFormatStringTypeSubschemaConverter(
                self, format="date-time", data_type=rdflib.XSD.dateTime
            ),
            "date": _FixFormatStringTypeSubschemaConverter(
                self, format="date", data_type=rdflib.XSD.date
            ),
            "time": _FixFormatStringTypeSubschemaConverter(
                self, format="time", data_type=rdflib.XSD.time
            ),
            "duration": _FixFormatStringTypeSubschemaConverter(
                self, format="duration", data_type=rdflib.XSD.duration
            ),
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.2
            # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s01.html
            # TODO As said on https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s01.html, the patterns for email addresses used below are only an approximation.
            "email": _FixFormatStringTypeSubschemaConverter(
                self,
                format="email",
                data_type=rdflib.XSD.string,
                pattern=r"""[\w!#$%&'*+/=?`{|}~^-]+(?:\.[\w!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}""",
            ),
            "idn-email": _FixFormatStringTypeSubschemaConverter(
                self,
                format="idn-email",
                data_type=rdflib.XSD.string,
                pattern=r"""[\w!#$%&'*+/=?`{|}~^-]+(?:\.[\w!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}""",
            ),
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.3
            # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s15.html
            "hostname": _FixFormatStringTypeSubschemaConverter(
                self,
                format="hostname",
                data_type=rdflib.XSD.string,
                pattern=r"""([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}""",
            ),
            "idn-hostname": _FixFormatStringTypeSubschemaConverter(
                self,
                format="idn-hostname",
                data_type=rdflib.XSD.string,
                pattern=r"""\b((xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\b""",
            ),
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.4
            "ipv4": _FixFormatStringTypeSubschemaConverter(
                self,
                format="ipv4",
                data_type=rdflib.XSD.string,
                pattern=r"""(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)""",
            ),  # https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
            "ipv6": _FixFormatStringTypeSubschemaConverter(
                self,
                format="ipv6",
                data_type=rdflib.XSD.string,
                pattern=r"""(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}""",
            ),  # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s17.html
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.5
            # https://www.w3.org/TR/xmlschema11-2/#anyURI
            # TODO As explained on https://www.w3.org/TR/xmlschema11-2/#anyURI, xsd:anyURI represents IRI and IRI references, so is not an exact match of the JSON Schema types other than iri-reference.
            "uri": _FixFormatStringTypeSubschemaConverter(
                self, format="uri", data_type=rdflib.XSD.anyURI
            ),
            "uri-reference": _FixFormatStringTypeSubschemaConverter(
                self, format="uri-reference", data_type=rdflib.XSD.anyURI
            ),
            "iri": _FixFormatStringTypeSubschemaConverter(
                self, format="iri", data_type=rdflib.XSD.anyURI
            ),
            "iri-reference": _FixFormatStringTypeSubschemaConverter(
                self, format="iri-reference", data_type=rdflib.XSD.anyURI
            ),
            "uuid": _FixFormatStringTypeSubschemaConverter(
                self,
                format="uuid",
                data_type=rdflib.XSD.string,
                pattern=r"""[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}""",
            ),
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.6
            "uri-template": _FixFormatStringTypeSubschemaConverter(
                self, format="uri-template", data_type=rdflib.XSD.string
            ),  # TODO Is there a type for URI templates or a commonly used regular expression?
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.7
            "json-pointer": _FixFormatStringTypeSubschemaConverter(
                self, format="json-pointer", data_type=rdflib.XSD.string
            ),  # TODO Is there a type for JSON pointers or a commonly used regular expression?
            "relative-json-pointer": _FixFormatStringTypeSubschemaConverter(
                self, format="relative-json-pointer", data_type=rdflib.XSD.string
            ),  # TODO Is there a type for relative JSON pointers or a commonly used regular expression?
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.7.3.8
            "regex": _FixFormatStringTypeSubschemaConverter(
                self, format="regex", data_type=rdflib.XSD.string
            ),  # TODO Is there a type for regular expressions or a commonly used regular expression for regular expressions?
        }

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return subschema.get(
            "format", None
        ) in self._converters.keys() and self._converters[
            cast(Optional[str], subschema.get("format", None))
        ].applicable(
            subschema
        )

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        return self._converters[
            cast(Optional[str], subschema.get("format", None))
        ].convert(path=path, subschema=subschema, identification=identification)


# See https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.3
class _FixFormatStringTypeSubschemaConverter(
    _ScalarTypeSubschemaConverterBase, metaclass=abc.ABCMeta
):
    def __init__(
        self,
        string_type_subschema_converter: _StringTypeSubschemaConverter,
        *,
        format: Optional[str],
        data_type: rdflib.term.Identifier,
        pattern: Optional[str] = None,
    ) -> None:
        super().__init__(
            string_type_subschema_converter,
            type=_StringTypeSubschemaConverter.TYPE,
            data_type=data_type,
            pattern=pattern,
            validation_keyword_converters={
                "maxLength": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.maxLength,
                    object_type=rdflib.XSD.double,
                ),
                "minLength": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.minLength,
                    object_type=rdflib.XSD.double,
                ),
                "pattern": _ValidationKeywordConverter(
                    self,
                    restriction_predicate=rdflib.XSD.pattern,
                    object_type=rdflib.XSD.string,
                ),  # TODO Ist this the correct object type? Do we need to transform the regular expression? Json Schema uses the ECMA 262 standard, see https://json-schema.org/draft/2019-09/json-schema-validation.html#pattern
            },
        )
        self._format = format

    def applicable_to_object_subschema(self, subschema: Dict[str, Json]) -> bool:
        return (
            super().applicable_to_object_subschema(subschema)
            and subschema.get("format", None) == self._format
        )


# https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.4
class _ArrayTypeSubschemaConverter(_TypeSubschemaConverterBase):
    TYPE = "array"

    def __init__(self, type_subschema_converter: _TypeSubschemaConverter) -> None:
        super().__init__(
            type_subschema_converter, type=_ArrayTypeSubschemaConverter.TYPE
        )

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        # TODO Use https://www.w3.org/Submission/SWRL/#8.7 or
        #      https://protege.stanford.edu/conference/2006/submissions/abstracts/7.1_Drummond_listsInProtegeOWL.pdf
        #      to represent lists. These are also mentioned in the paper
        #      `Translating JSON Schema logics into OWL axioms for unified data
        #      validation on a digital manufacturing platform` by Hyunmin
        #      Cheonga who says he also uses `SWRL` to represent JSON Schema's
        #      `if/then/else`.
        #      See also the slides https://protege.stanford.edu/conference/2006/submissions/slides/7.1_Drummond.pdf
        #      and http://www.cs.man.ac.uk/~drummond/publications/OWLListsPaper/owl-lists-iswc.pdf
        #      and https://stackoverflow.com/questions/58379557/mapping-an-array-in-json-schema-to-owl
        #      and https://mailman.stanford.edu/pipermail/protege-owl/2009-November/012542.html
        return self._make_identifier(path, identification=identification)


# https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.5
class _ObjectTypeSubschemaConverter(_TypeSubschemaConverterBase):
    TYPE = "object"

    def __init__(self, type_subschema_converter: _TypeSubschemaConverter) -> None:
        super().__init__(
            type_subschema_converter, type=_ObjectTypeSubschemaConverter.TYPE
        )

    def convert_object_subschema(
        self, *, path: List[str], subschema: Dict[str, Json], identification: _Identification
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=identification)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.Class))
        # https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.9.3.2.1
        if "properties" in subschema:
            properties = cast(Dict[str, JsonSchema], subschema["properties"])
            property_name_to_identifier = self._convert_properties(
                identifier=identifier, path=path, properties=properties
            )
            # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.5
            # TODO Convert `maxProperties` and `minProperties`
            self._restrict_property_cardinalities(
                identifier=identifier,
                subschema=subschema,
                properties=properties,
                property_name_to_identifier=property_name_to_identifier,
            )
        # TODO `patternProperties`, `additionalProperties`, `unevaluatedProperties`, and `propertyNames`, see https://json-schema.org/draft/2019-09/json-schema-core.html#rfc.section.9.3.2.2 and succeeding sections
        return identifier

    def _convert_properties(
        self,
        *,
        identifier: rdflib.term.Identifier,
        path: List[str],
        properties: Dict[str, JsonSchema],
    ) -> Dict[str, rdflib.term.Identifier]:
        property_name_to_identifier = {}
        for name, value in properties.items():
            property_name_to_identifier[name] = self._convert_property(
                object_identifier=identifier, path=path + [name], property=value
            )
        return property_name_to_identifier

    def _convert_property(
        self,
        *,
        object_identifier: rdflib.term.Identifier,
        path: List[str],
        property: JsonSchema,
    ) -> rdflib.term.Identifier:
        identifier = self._make_identifier(path, identification=_Identification.NEW_NAME)
        self.graph.add((identifier, rdflib.RDF.type, rdflib.OWL.ObjectProperty))
        self.graph.add((identifier, rdflib.RDFS.domain, object_identifier,))
        # TODO Blindly appending `range` to the path may lead to naming conflicts.
        range = self.convert_subschema(
            path=path + ['range'], subschema=property, identification=_Identification.SOME_NAME
        )
        self.graph.add((identifier, rdflib.RDFS.range, range))
        return identifier

    def _restrict_property_cardinalities(
        self,
        *,
        identifier: rdflib.term.Identifier,
        subschema: Dict[str, Json],
        properties: Dict[str, JsonSchema],
        property_name_to_identifier: Dict[str, rdflib.term.Identifier],
    ) -> None:
        property_name_to_min_cardinality = {
            name: 0 for name in property_name_to_identifier.keys()
        }
        if "required" in subschema:
            for name in cast(List[str], subschema["required"]):
                property_name_to_min_cardinality[name] = 1
        # TODO `dependentRequired` https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6.5.4
        # Make properties that may be `null` optional even if they are
        # required.
        for name in property_name_to_min_cardinality.keys():
            property = properties[name]
            if isinstance(property, dict):
                object_property = cast(Dict[str, JsonSchema], property)
                if (
                    "type" in property
                    and isinstance(property["type"], list)
                    and "null" in property["type"]
                ):
                    property_name_to_min_cardinality[name] = 0
        # Add restriction triples.
        for name, property_identifier in property_name_to_identifier.items():
            restriction = self._make_restriction(
                on_property=property_identifier, of_object=identifier
            )
            if property_name_to_min_cardinality[name] == 0:
                self.graph.add(
                    (restriction, rdflib.OWL.maxCardinality, rdflib.Literal(1),)
                )
            else:
                self.graph.add(
                    (restriction, rdflib.OWL.cardinality, rdflib.Literal(1),)
                )

    def _make_restriction(
        self, *, on_property: rdflib.term.Identifier, of_object: rdflib.term.Identifier
    ) -> rdflib.term.Identifier:
        restriction = rdflib.BNode()
        self.graph.add((restriction, rdflib.RDF.type, rdflib.OWL.Restriction))
        self.graph.add((restriction, rdflib.OWL.onProperty, on_property))
        self.graph.add((of_object, rdflib.RDFS.subClassOf, restriction,))
        return restriction


@click.command()
@click.option("--verbose", is_flag=True, default=False, help="Verbose mode.")
@click.option(
    "--rdf-format",
    type=click.Choice(
        ["xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads"]
    ),
    default="turtle",
    help="RDF-output serialization format.",
)  # The list of formats was taken from https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html?highlight=serialize#rdflib.graph.Graph.serialize
@click.option(
    "--name",
    required=True,
    type=str,
    help="Name of the root JSON Schema. Must be a valid prefixed name as defined on https://www.w3.org/TR/turtle/#sec-iri",
)
@click.argument("input", type=click.File("rt"))
@click.argument("output", type=click.File("wb"))
def _command_line_interface(
    verbose: bool, rdf_format: str, name: str, input: TextIO, output: TextIO
) -> None:
    """Convert JSON Schema to equivalent Web Ontology.

    Examples:

        Show help message and exit.

        >>> python json_schema_to_ontology.py --help

        Read from standard input and write to standard output.

        >>> echo true | python json_schema_to_ontology.py --name x - -

        Read from `my.schema.json` and write to `my.ontology.ttl`.

        >>> python json_schema_to_ontology.py --name x my.schema.json my.ontology.ttl
    """
    output.write(
        convert(json.loads(input.read()), name=name, verbose=verbose).serialize(
            format=rdf_format
        )
    )


if __name__ == "__main__":
    _command_line_interface()  # pylint: disable=no-value-for-parameter
