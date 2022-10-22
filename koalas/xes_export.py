"""
This module has the arttributes and tags for xml documents for exporting.
"""
from typing import List
from xml.etree.ElementTree import Element 

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

# XES sub elements
XES_STRING_TAG = 'string'
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
                'value' : value
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