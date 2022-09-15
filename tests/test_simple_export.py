import unittest
from os import path 
from tempfile import TemporaryDirectory

from koalas.read import read_xes_simple
from koalas.export import export_to_xes_simple

import xmlschema

SSMALL = path.join(".","tests","small_01.xes")
WSMALL = path.join(".","tests","small_02.xes")
OSMALL = path.join(".","tests","small_03.xes")

class DTLogTest(unittest.TestCase):

    def test_successful_export(self):
        try:
            log = read_xes_simple(SSMALL, debug=False) 
        except:
            self.fail("Failed to parse log")

        fdir = TemporaryDirectory()
        try:
            filepath = path.join(fdir.name, "test_log")
            export_to_xes_simple(filepath, log,debug=False) 
        except:
            self.fail("Failed to export log")
        finally:
            fdir.cleanup()

    def test_equals_export_import(self):
        try:
            log = read_xes_simple(SSMALL, debug=False) 
        except:
            self.fail("Failed to parse log")

        fdir = TemporaryDirectory()
        try:
            filepath = path.join(fdir.name, "test_log")
            export_to_xes_simple(filepath, log, debug=False) 
        except:
            fdir.cleanup()
            self.fail("Failed to export log")
            return
        
        log2 = read_xes_simple(filepath,debug=False)
        self.assertEqual(log, log2)

        fdir.cleanup()

    def test_xml_valid(self):
        try:
            log = read_xes_simple(SSMALL, debug=False) 
        except:
            self.fail("Failed to parse log")

        fdir = TemporaryDirectory()
        try:
            filepath = path.join(fdir.name, "test_log")
            export_to_xes_simple(filepath, log, debug=False) 
        except:
            fdir.cleanup()
            self.fail("Failed to export log")
            return

        schema = xmlschema.XMLSchema(path.join(".","tests","xes-ieee-1849-2016.xsd"), namespace="http://www.xes-standard.org/")
        schema.validate(filepath)



