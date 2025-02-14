import unittest

from pmkoalas.models.pnfrag import parse_net_fragments
from pmkoalas.models.petrinets.export import export_net_to_pnml
from pmkoalas.models.petrinets.read import parse_pnml_into_wpn

from os.path import join
from tempfile import TemporaryDirectory



class TestNetExport(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()
    
    def test_export_net_to_wpn(self):
        NET = parse_net_fragments(
            "foobar",
            "I -> [a] -> p1 -> [b] -> F",
            "I -> [tau] -> p1 -> [b] -> F",
            "I -> {c 2.0} -> p1 -> [tau] -> F",
        )
        with TemporaryDirectory() as tmpdirname:
            # check export
            fname = join(tmpdirname, "test.pnml")
            export_net_to_pnml(NET,fname)
            net = parse_pnml_into_wpn(fname)
            self.assertEqual(NET.places, net.places)
            self.assertEqual(NET.transitions, net.transitions)
            self.assertEqual(NET.arcs, net.arcs)
            self.assertEqual(NET.name, net.name)
            self.assertEqual(NET,net)
            onet = parse_pnml_into_wpn(fname,use_localnode_id=True)
            fname = join(tmpdirname, "test_localnode_id.pnml")
            export_net_to_pnml(onet,fname)
            re_onet = parse_pnml_into_wpn(fname,use_localnode_id=True)
            self.assertEqual(onet,re_onet)