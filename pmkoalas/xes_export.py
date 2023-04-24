"""
This module has the arttributes and tags for xml documents for exporting.
"""
from typing import List
from xml.etree.ElementTree import Element 
from datetime import datetime

XES_LOG_TAG = "log"
XES_LOG_ATTRS = {
    'xes.version' : "1.0",
    'xes.features' : "nested-attributes",
    'xmlns': "http://www.xes-standard.org/"
}

# XES log sub elements
XES_EXTENSION_TAG = 'extension'
XES_EXT_CONCEPT_NAME = "concept"
XES_EXT_CONCEPT_PREFIX = "concept"
XES_EXT_CONCEPT_URI = "http://www.xes-standard.org/concept.xesext"
class XesLogExtension(Element):
    """
    Creates an xml element, for stating xes extensions used in a log.

    Parameters
    ----------
    name: `str`
    \t name of extensions
    prefix: `str`
    \t prefix used for all attributes related to extension
    uri: `str`
    \t web address for extension's xml structure
    """

    def __init__(self, name:str, prefix:str, uri:str ) -> None:
        super().__init__(
            XES_EXTENSION_TAG,
            {
                'name' : name,
                'prefix' : prefix,
                'uri' : uri
            },
            **{}
        )

XES_CLASSIFIER_TAG = "classifier"
class XesLogClassifier(Element):
    """
    Creates an xml element, for stating xes classifiers used in a log.

    Parameters
    ----------
    name: `str`
    \t name of extensions
    keys: `List[str]`
    \t the list of attributes that this classifier uses
    """

    def __init__(self, name:str, keys:List[str] ) -> None:
        super().__init__(
            XES_CLASSIFIER_TAG,
            {
                'name' : name,
                'keys' : " ".join(keys),
            },
            **{}
        )

# XES keys
XES_CONCEPT = "concept:name"
XES_TIME = "time:timestamp"

# XES sub elements
XES_STRING_TAG = 'string'
XES_INT_TAG = "int"
XES_TIME_TAG = "date"
XES_FLOAT_TAG = "float"
XES_BOOLEAN_TAG = "boolean"
class XesString(Element):
    """
    Creates an xml element, using the string representation in XES.

    Parameters
    ----------
    key: `str`
    \t The key of the attribute to be added to parent
    value: `str`
    \t The value for this key.
    """

    def __init__(self, key:str, value:str) -> None:
        super().__init__(
            XES_STRING_TAG, 
            {
                'key' : key,
                'value' : str(value)
            }, 
            **{}
        )

class XesInt(Element):
    """
    Creates an xml element, using the int representation in XES.

    Parameters
    ----------
    key: `str`
    \t The key of the attribute to be added to parent
    value: `str`
    \t The value for this key.
    """

    def __init__(self, key:str, value:int) -> None:
        super().__init__(
            XES_INT_TAG, 
            {
                'key' : key,
                'value' : str(value)
            }, 
            **{}
        )

class XesTime(Element):
    """
    Creates an xml element, using the date representation in XES.

    Parameters
    ----------
    key: `str`
    \t The key of the attribute to be added to parent
    value: `str`
    \t The value for this key.
    """

    def __init__(self, key:str, value:datetime) -> None:
        super().__init__(
            XES_TIME_TAG, 
            {
                'key' : key,
                'value' : value.isoformat()
            }, 
            **{}
        )

class XesFloat(Element):
    """
    Creates an xml element, using the float (up to eight decimals) representation in XES.

    Parameters
    ----------
    key: `str`
    \t The key of the attribute to be added to parent
    value: `str`
    \t The value for this key.
    """

    def __init__(self, key:str, value:float) -> None:
        super().__init__(
            XES_FLOAT_TAG, 
            {
                'key' : key,
                'value' : f"{value:.8f}"
            }, 
            **{}
        )

class XesBoolean(Element):
    """
    Creates an xml element, using the float (up to eight decimals) representation in XES.

    Parameters
    ----------
    key: `str`
    \t The key of the attribute to be added to parent
    value: `str`
    \t The value for this key.
    """

    def __init__(self, key:str, value:bool) -> None:
        super().__init__(
            XES_BOOLEAN_TAG, 
            {
                'key' : key,
                'value' : 'true' if value else 'false'
            }, 
            **{}
        )

# XES trace element
XES_TRACE_TAG = "trace"
class XesTrace(Element):
    """
    Creates an empty trace xml parent.

    Parameters
    ----------
    concept: `str`
    \t the concept:name value for this trace
    """

    def __init__(self, concept:str) -> None:
        super().__init__(XES_TRACE_TAG, {}, **{})
        # add concept:name
        self.append(XesString(XES_CONCEPT, concept))

# XES event element 
XES_EVENT_TAG = "event"
class XesEvent(Element):
    """
    Creates an empty event xml parent.
    """

    def __init__(self,) -> None:
        super().__init__(XES_EVENT_TAG, {}, **{})