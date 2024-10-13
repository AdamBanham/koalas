import unittest
from copy import deepcopy

from pmkoalas.simple import Trace,EventLog
from pmkoalas.discovery.alpha_miner import AlphaMinerPlusInstance
from pmkoalas.discovery.alpha_miner import AlphaRelation,AlphaPair
from pmkoalas.discovery.alpha_miner import AlphaPlace,AlphaFlowRelation
from pmkoalas.discovery.alpha_miner import AlphaTransition
from pmkoalas.discovery.alpha_miner import AlphaSinkPlace,AlphaStartPlace
from pmkoalas.models.petrinet import Place,Transition,Arc,LabelledPetriNet
from pmkoalas.dtlog import convert

# simple log tests
LOG = convert( 
            "a b d",
            "a c d",
            "a b",
            "a c",
            "a b d e b d",
            "a c d e c d"
        )
START_ACTS = set(["a"])
END_ACTS = set(["d", "b", "c"])
ACTS = set(["a", "b", "c", "d", "e"])
MATRIX = { 
    "a" : {
        "a" : AlphaRelation("a","a",[]),
        "b" : AlphaRelation("a","b",[("a","b")]),
        "c" : AlphaRelation("a","c",[("a","c")]),
        "d" : AlphaRelation("a","d",[]),
        "e" : AlphaRelation("a","e",[])
    },
    "b" : {
        "a" : AlphaRelation("b","a",[("a","b")]),
        "b" : AlphaRelation("b","b",[]),
        "c" : AlphaRelation("b","c",[]),
        "d" : AlphaRelation("b","d",[("b","d")]),
        "e" : AlphaRelation("b","e",[("e","b")])
    },
    "c" : {
        "a" : AlphaRelation("c","a",[("a","c")]),
        "b" : AlphaRelation("c","b",[]),
        "c" : AlphaRelation("c","c",[]),
        "d" : AlphaRelation("c","d",[("c","d")]),
        "e" : AlphaRelation("c","e",[("e","c")])
    },
    "d" : {
        "a" : AlphaRelation("d","a",[]),
        "b" : AlphaRelation("d","b",[("b","d")]),
        "c" : AlphaRelation("d","c",[("c","d")]),
        "d" : AlphaRelation("d","d",[]),
        "e" : AlphaRelation("d","e",[("d","e")])
    },
    "e" : {
        "a" : AlphaRelation("e","a",[]),
        "b" : AlphaRelation("e","b",[("e","b")]),
        "c" : AlphaRelation("e","c",[("e","c")]),
        "d" : AlphaRelation("e","d",[("d","e")]),
        "e" : AlphaRelation("e","e",[])
    }
}

# following p173 and L5 in Process Mining (2016;2ND ED)
BOOK_LOG = convert( 
    "a b e f",
    "a b e f",
    "a b e c d b f",
    "a b e c d b f",
    "a b e c d b f",
    "a b c e d b f",
    "a b c e d b f",
    "a b c d e b f",
    "a b c d e b f",
    "a b c d e b f",
    "a b c d e b f",
    "a e b c d b f",
    "a e b c d b f",
    "a e b c d b f",
)
BOOK_TL = set(["a", "b", "c", "d", "e", "f"])
BOOK_TL_OUT = set([ AlphaTransition(t) for t in BOOK_TL])
BOOK_TI = set(["a"])
BOOK_TO = set(["f"])
BOOK_XL = set([ 
    AlphaPair(set(["a"]),set(["b"])),
    AlphaPair(set(["a"]), set(["e"])),
    AlphaPair(set(["b"]), set(["c"])),
    AlphaPair(set(["b"]), set(["f"])),
    AlphaPair(set(["c"]), set(["d"])),
    AlphaPair(set(["d"]), set(["b"])),
    AlphaPair(set(["e"]), set(["f"])),
    AlphaPair(set(["a","d"]), set(["b"])),
    AlphaPair(set(["b"]), set(["c","f"])),
])
BOOK_YL = [
    AlphaPair(set(["a"]), set(["e"])),
    AlphaPair(set(["c"]), set(["d"])),
    AlphaPair(set(["e"]), set(["f"])),
    AlphaPair(set(["a","d"]), set(["b"])),
    AlphaPair(set(["b"]), set(["c","f"])),
]
BOOK_PL = [ 
    AlphaPlace(BOOK_YL[0].__str__(), BOOK_YL[0].left, BOOK_YL[0].right),
    AlphaPlace(BOOK_YL[1].__str__(), BOOK_YL[1].left, BOOK_YL[1].right),
    AlphaPlace(BOOK_YL[2].__str__(), BOOK_YL[2].left, BOOK_YL[2].right),
    AlphaPlace(BOOK_YL[3].__str__(), BOOK_YL[3].left, BOOK_YL[3].right),
    AlphaPlace(BOOK_YL[4].__str__(), BOOK_YL[4].left, BOOK_YL[4].right),
    AlphaStartPlace(),
    AlphaSinkPlace(),
]
BOOK_FL = set([ 
    AlphaFlowRelation("1", AlphaTransition("a"), BOOK_PL[0]),
    AlphaFlowRelation("2", BOOK_PL[0], AlphaTransition("e")),
    AlphaFlowRelation("3", AlphaTransition("c"), BOOK_PL[1]),
    AlphaFlowRelation("4", BOOK_PL[1], AlphaTransition("d")),
    AlphaFlowRelation("5", AlphaTransition("e"), BOOK_PL[2]),
    AlphaFlowRelation("6", BOOK_PL[2], AlphaTransition("f")),
    AlphaFlowRelation("7", AlphaTransition("a"), BOOK_PL[3]),
    AlphaFlowRelation("8", AlphaTransition("d"), BOOK_PL[3]),
    AlphaFlowRelation("9", BOOK_PL[3], AlphaTransition("b")),
    AlphaFlowRelation("10", AlphaTransition("b"), BOOK_PL[4]),
    AlphaFlowRelation("11", BOOK_PL[4], AlphaTransition("c")),
    AlphaFlowRelation("12", BOOK_PL[4], AlphaTransition("f")),
    AlphaFlowRelation("13", BOOK_PL[5], AlphaTransition("a")),
    AlphaFlowRelation("14", AlphaTransition("f"), BOOK_PL[6]),    
])
BOOK_YL = set(BOOK_YL)
BOOK_PL = set(BOOK_PL)
BOOK_LPN_PL = set([
    Place(p.name) 
    for p
    in BOOK_PL
])
BOOK_LPN_TL = set([
    Transition(t)
    for t in BOOK_TL
])
place_nodes = dict( 
    (p.name, p)
    for p in BOOK_LPN_PL
)
transition_nodes = dict(
    (t.name, t)
    for t in BOOK_LPN_TL
)
BOOK_LPN_FL = set([
    Arc(place_nodes[f.src.name], transition_nodes[f.tar.name])
    if isinstance(f.src, AlphaPlace) else
    Arc(transition_nodes[f.src.name], place_nodes[f.tar.name])
    for f in BOOK_FL
])

alpha_plus_log_1 = log_a = convert(
    "a b",
    "a c f",
    "a c d b",
    "a c d c d b",
    "a c d c d c f",
    "e f",
    "e d b",
    "e d c d b",
    "e d c f"
)
alpha_plus_lpn_1 = LabelledPetriNet(
    places=[
            Place("P_initial",pid="e24a7736-a912-4a3f-9eae-eee069655b56"),
            Place("P_({'a', 'd'},{'b', 'c'})",pid="9b3d3f91-69f0-4706-b776-2ec017a0212a"),
            Place("P_sink",pid="b70330d4-53ee-4db8-9c4d-16d045b7e77f"),
            Place("P_({'c', 'e'},{'d', 'f'})",pid="36fdb6b7-2d5b-4802-ab11-aeeb95e3dad4"),
    ],
    transitions=[
            Transition("f",tid="6bc0ba57-46c3-4cfd-8c65-9d17eb48a7cd",weight=1.0,silent=False),
            Transition("b",tid="3ec3e270-35fb-4a9d-bb00-9a523498c23e",weight=1.0,silent=False),
            Transition("c",tid="84598e1b-ba53-4ee4-8400-22abb2fc333f",weight=1.0,silent=False),
            Transition("d",tid="ea1b3360-4045-4a59-b147-804d747416e3",weight=1.0,silent=False),
            Transition("a",tid="3bab0469-ef26-4adc-a6f4-f9cd4dd69a29",weight=1.0,silent=False),
            Transition("e",tid="6af4d9fe-deda-4020-ad5e-bfb88ce23d3b",weight=1.0,silent=False),
    ],
    arcs=[
            Arc(from_node=Place("P_({'c', 'e'},{'d', 'f'})",pid="36fdb6b7-2d5b-4802-ab11-aeeb95e3dad4"),to_node=Transition("d",tid="ea1b3360-4045-4a59-b147-804d747416e3",weight=1.0,silent=False)),
            Arc(from_node=Transition("e",tid="6af4d9fe-deda-4020-ad5e-bfb88ce23d3b",weight=1.0,silent=False),to_node=Place("P_({'c', 'e'},{'d', 'f'})",pid="36fdb6b7-2d5b-4802-ab11-aeeb95e3dad4")),
            Arc(from_node=Transition("b",tid="3ec3e270-35fb-4a9d-bb00-9a523498c23e",weight=1.0,silent=False),to_node=Place("P_sink",pid="b70330d4-53ee-4db8-9c4d-16d045b7e77f")),
            Arc(from_node=Transition("c",tid="84598e1b-ba53-4ee4-8400-22abb2fc333f",weight=1.0,silent=False),to_node=Place("P_({'c', 'e'},{'d', 'f'})",pid="36fdb6b7-2d5b-4802-ab11-aeeb95e3dad4")),
            Arc(from_node=Place("P_({'a', 'd'},{'b', 'c'})",pid="9b3d3f91-69f0-4706-b776-2ec017a0212a"),to_node=Transition("c",tid="84598e1b-ba53-4ee4-8400-22abb2fc333f",weight=1.0,silent=False)),
            Arc(from_node=Place("P_initial",pid="e24a7736-a912-4a3f-9eae-eee069655b56"),to_node=Transition("e",tid="6af4d9fe-deda-4020-ad5e-bfb88ce23d3b",weight=1.0,silent=False)),
            Arc(from_node=Transition("f",tid="6bc0ba57-46c3-4cfd-8c65-9d17eb48a7cd",weight=1.0,silent=False),to_node=Place("P_sink",pid="b70330d4-53ee-4db8-9c4d-16d045b7e77f")),
            Arc(from_node=Transition("a",tid="3bab0469-ef26-4adc-a6f4-f9cd4dd69a29",weight=1.0,silent=False),to_node=Place("P_({'a', 'd'},{'b', 'c'})",pid="9b3d3f91-69f0-4706-b776-2ec017a0212a")),
            Arc(from_node=Transition("d",tid="ea1b3360-4045-4a59-b147-804d747416e3",weight=1.0,silent=False),to_node=Place("P_({'a', 'd'},{'b', 'c'})",pid="9b3d3f91-69f0-4706-b776-2ec017a0212a")),
            Arc(from_node=Place("P_({'c', 'e'},{'d', 'f'})",pid="36fdb6b7-2d5b-4802-ab11-aeeb95e3dad4"),to_node=Transition("f",tid="6bc0ba57-46c3-4cfd-8c65-9d17eb48a7cd",weight=1.0,silent=False)),
            Arc(from_node=Place("P_initial",pid="e24a7736-a912-4a3f-9eae-eee069655b56"),to_node=Transition("a",tid="3bab0469-ef26-4adc-a6f4-f9cd4dd69a29",weight=1.0,silent=False)),
            Arc(from_node=Place("P_({'a', 'd'},{'b', 'c'})",pid="9b3d3f91-69f0-4706-b776-2ec017a0212a"),to_node=Transition("b",tid="3ec3e270-35fb-4a9d-bb00-9a523498c23e",weight=1.0,silent=False)),
    ],
    name='Petri net'
)
alpha_plus_log_2 = convert(
    "a b d",
    "a b c b d",
    "a b c b c b d",
)
alpha_plus_lpn_2 = LabelledPetriNet(
        places=[
                Place("P_({'a', 'c'},{'b'})",pid="efe9d0f8-757a-4483-985b-0df527d0404e"),
                Place("P_({'b'},{'c', 'd'})",pid="fb89b421-d116-4a15-9c40-70f0d83b4153"),
                Place("P_initial",pid="b2c6b279-18c8-4cf8-8ac6-9e06c2bb0fd8"),
                Place("P_sink",pid="c6afa143-dad7-40ce-a15e-5cf7dba08529"),
        ],
        transitions=[
                Transition("d",tid="c4d8d2e3-942b-4472-b5a1-06e900b1dd41",weight=1.0,silent=False),
                Transition("a",tid="12a0a456-9aa8-48cd-a609-5cf5442d3a1f",weight=1.0,silent=False),
                Transition("c",tid="38eaecb9-2e9f-4c44-915c-59fe6288509f",weight=1.0,silent=False),
                Transition("b",tid="e68c86b5-49e3-4bde-85e3-59c18e1dc314",weight=1.0,silent=False),
        ],
        arcs=[
                Arc(from_node=Place("P_({'b'},{'c', 'd'})",pid="fb89b421-d116-4a15-9c40-70f0d83b4153"),to_node=Transition("d",tid="c4d8d2e3-942b-4472-b5a1-06e900b1dd41",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'a', 'c'},{'b'})",pid="efe9d0f8-757a-4483-985b-0df527d0404e"),to_node=Transition("b",tid="e68c86b5-49e3-4bde-85e3-59c18e1dc314",weight=1.0,silent=False)),
                Arc(from_node=Transition("d",tid="c4d8d2e3-942b-4472-b5a1-06e900b1dd41",weight=1.0,silent=False),to_node=Place("P_sink",pid="c6afa143-dad7-40ce-a15e-5cf7dba08529")),
                Arc(from_node=Transition("b",tid="e68c86b5-49e3-4bde-85e3-59c18e1dc314",weight=1.0,silent=False),to_node=Place("P_({'b'},{'c', 'd'})",pid="fb89b421-d116-4a15-9c40-70f0d83b4153")),
                Arc(from_node=Transition("a",tid="12a0a456-9aa8-48cd-a609-5cf5442d3a1f",weight=1.0,silent=False),to_node=Place("P_({'a', 'c'},{'b'})",pid="efe9d0f8-757a-4483-985b-0df527d0404e")),
                Arc(from_node=Transition("c",tid="38eaecb9-2e9f-4c44-915c-59fe6288509f",weight=1.0,silent=False),to_node=Place("P_({'a', 'c'},{'b'})",pid="efe9d0f8-757a-4483-985b-0df527d0404e")),
                Arc(from_node=Place("P_initial",pid="b2c6b279-18c8-4cf8-8ac6-9e06c2bb0fd8"),to_node=Transition("a",tid="12a0a456-9aa8-48cd-a609-5cf5442d3a1f",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'b'},{'c', 'd'})",pid="fb89b421-d116-4a15-9c40-70f0d83b4153"),to_node=Transition("c",tid="38eaecb9-2e9f-4c44-915c-59fe6288509f",weight=1.0,silent=False)),
        ],
        name='Petri net'
)
alpha_plus_log_3 = convert(
    "a b d",
    "a b c b d",
    "a b c b c b d",
    "a b b d",
    "a b b b d",
    "a b b c d",
    "a b b c c d",
    "a c c b b d",
    "a c b c b d"
)
alpha_plus_lpn_3 = LabelledPetriNet(
        places=[
                Place("P_initial",pid="58be6669-72ef-4a49-90ed-c006d6afa600"),
                Place("P_sink",pid="b62de061-6bf9-4cd3-8929-77821e042ea4"),
                Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1"),
        ],
        transitions=[
                Transition("a",tid="6b056e17-ea79-462d-ba02-f7698766588c",weight=1.0,silent=False),
                Transition("b",tid="5552c955-359e-47b0-8fac-78a91e279e64",weight=1.0,silent=False),
                Transition("c",tid="ad86bd4d-cc2e-47a0-95b1-d866d54dd6df",weight=1.0,silent=False),
                Transition("d",tid="8241ba0f-cd6c-4f9d-a9f9-318b761b1b3a",weight=1.0,silent=False),
        ],
        arcs=[
                Arc(from_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1"),to_node=Transition("c",tid="ad86bd4d-cc2e-47a0-95b1-d866d54dd6df",weight=1.0,silent=False)),
                Arc(from_node=Transition("a",tid="6b056e17-ea79-462d-ba02-f7698766588c",weight=1.0,silent=False),to_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1")),
                Arc(from_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1"),to_node=Transition("d",tid="8241ba0f-cd6c-4f9d-a9f9-318b761b1b3a",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1"),to_node=Transition("b",tid="5552c955-359e-47b0-8fac-78a91e279e64",weight=1.0,silent=False)),
                Arc(from_node=Transition("b",tid="5552c955-359e-47b0-8fac-78a91e279e64",weight=1.0,silent=False),to_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1")),
                Arc(from_node=Place("P_initial",pid="58be6669-72ef-4a49-90ed-c006d6afa600"),to_node=Transition("a",tid="6b056e17-ea79-462d-ba02-f7698766588c",weight=1.0,silent=False)),
                Arc(from_node=Transition("d",tid="8241ba0f-cd6c-4f9d-a9f9-318b761b1b3a",weight=1.0,silent=False),to_node=Place("P_sink",pid="b62de061-6bf9-4cd3-8929-77821e042ea4")),
                Arc(from_node=Transition("c",tid="ad86bd4d-cc2e-47a0-95b1-d866d54dd6df",weight=1.0,silent=False),to_node=Place("P_({'a'},{'d'})",pid="53579d87-9431-4031-833b-a307a59da0a1")),
        ],
        name='Petri net'
)
alpha_plus_log_4 = EventLog(
        [Trace(['a','c','f','h'])] * 1+
        [Trace(['a','c','e','f','h'])] * 1+
        [Trace(['a','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','f','h'])] * 1+
        [Trace(['a','b','c','e','f','h'])] * 1+
        [Trace(['a','b','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','f','h'])] * 1+
        [Trace(['a','c','d','c','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','f','h'])] * 1+
        [Trace(['a','c','e','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','e','f','h'])] * 1+
        [Trace(['a','b','c','f','g','f','h'])] * 1+
        [Trace(['a','b','c','d','c','f','h'])] * 1+
        [Trace(['a','b','c','e','e','f','h'])] * 1+
        [Trace(['a','b','b','c','e','f','h'])] * 1+
        [Trace(['a','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','f','g','f','h'])] * 1+
        [Trace(['a','c','f','g','d','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','e','f','h'])] * 1+
        [Trace(['a','c','d','c','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','d','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','e','f','h'])] * 1+
        [Trace(['a','c','e','d','c','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','c','f','h'])] * 1+
        [Trace(['a','c','e','e','f','g','f','h'])] * 1+
        [Trace(['a','c','e','e','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','e','e','f','h'])] * 1+
        [Trace(['a','b','c','f','g','e','f','h'])] * 1+
        [Trace(['a','b','c','d','c','e','f','h'])] * 1+
        [Trace(['a','b','c','d','b','c','f','h'])] * 1+
        [Trace(['a','b','c','e','f','g','f','h'])] * 1+
        [Trace(['a','b','c','e','d','c','f','h'])] * 1+
        [Trace(['a','b','c','e','e','e','f','h'])] * 1+
        [Trace(['a','b','b','c','f','g','f','h'])] * 1+
        [Trace(['a','b','b','c','d','c','f','h'])] * 1+
        [Trace(['a','b','b','c','e','e','f','h'])] * 1+
        [Trace(['a','b','b','b','c','e','f','h'])] * 1+
        [Trace(['a','b','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','f','g','e','f','h'])] * 1+
        [Trace(['a','c','f','g','d','c','e','f','h'])] * 1+
        [Trace(['a','c','f','g','d','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','f','g','f','h'])] * 1+
        [Trace(['a','c','f','g','e','d','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','e','e','f','h'])] * 1+
        [Trace(['a','c','d','c','f','g','e','f','h'])] * 1+
        [Trace(['a','c','d','c','d','c','e','f','h'])] * 1+
        [Trace(['a','c','d','c','d','b','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','e','d','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','f','g','f','h'])] * 1+
        [Trace(['a','c','d','b','c','d','c','f','h'])] * 1+
        [Trace(['a','c','d','b','c','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','c','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','f','g','f','h'])] * 1+
        [Trace(['a','c','e','f','g','d','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','e','e','f','h'])] * 1+
        [Trace(['a','c','e','d','c','f','g','f','h'])] * 1+
        [Trace(['a','c','e','d','c','d','c','f','h'])] * 1+
        [Trace(['a','c','e','d','c','e','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','c','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','e','f','g','e','f','h'])] * 1+
        [Trace(['a','c','e','e','d','c','e','f','h'])] * 1+
        [Trace(['a','c','e','e','d','b','c','f','h'])] * 1+
        [Trace(['a','c','e','e','e','f','g','f','h'])] * 1+
        [Trace(['a','c','e','e','e','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','e','e','e','f','h'])] * 1+
        [Trace(['a','b','c','f','g','f','g','f','h'])] * 1+
        [Trace(['a','b','c','f','g','d','c','f','h'])] * 1+
        [Trace(['a','b','c','f','g','e','e','f','h'])] * 1+
        [Trace(['a','b','c','d','c','f','g','f','h'])] * 1+
        [Trace(['a','b','c','d','c','d','c','f','h'])] * 1+
        [Trace(['a','b','c','d','c','e','e','f','h'])] * 1+
        [Trace(['a','b','c','d','b','c','e','f','h'])] * 1+
        [Trace(['a','b','c','d','b','b','c','f','h'])] * 1+
        [Trace(['a','b','c','e','f','g','e','f','h'])] * 1+
        [Trace(['a','b','c','e','d','c','e','f','h'])] * 1+
        [Trace(['a','b','c','e','d','b','c','f','h'])] * 1+
        [Trace(['a','b','c','e','e','f','g','f','h'])] * 1+
        [Trace(['a','b','c','e','e','d','c','f','h'])] * 1+
        [Trace(['a','b','c','e','e','e','e','f','h'])] * 1+
        [Trace(['a','b','b','c','f','g','e','f','h'])] * 1+
        [Trace(['a','b','b','c','d','c','e','f','h'])] * 1+
        [Trace(['a','b','b','c','d','b','c','f','h'])] * 1+
        [Trace(['a','b','b','c','e','f','g','f','h'])] * 1+
        [Trace(['a','b','b','c','e','d','c','f','h'])] * 1+
        [Trace(['a','b','b','c','e','e','e','f','h'])] * 1+
        [Trace(['a','b','b','b','c','f','g','f','h'])] * 1+
        [Trace(['a','b','b','b','c','d','c','f','h'])] * 1+
        [Trace(['a','b','b','b','c','e','e','f','h'])] * 1+
        [Trace(['a','b','b','b','b','c','e','f','h'])] * 1+
        [Trace(['a','b','b','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','f','g','f','g','f','h'])] * 1+
        [Trace(['a','c','f','g','f','g','d','c','f','h'])] * 1+
        [Trace(['a','c','f','g','f','g','e','e','f','h'])] * 1+
        [Trace(['a','c','f','g','d','c','f','g','f','h'])] * 1+
        [Trace(['a','c','f','g','d','c','d','c','f','h'])] * 1+
        [Trace(['a','c','f','g','d','c','e','e','f','h'])] * 1+
        [Trace(['a','c','f','g','d','b','c','e','f','h'])] * 1+
        [Trace(['a','c','f','g','d','b','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','f','g','e','f','h'])] * 1+
        [Trace(['a','c','f','g','e','d','c','e','f','h'])] * 1+
        [Trace(['a','c','f','g','e','d','b','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','e','f','g','f','h'])] * 1+
        [Trace(['a','c','f','g','e','e','d','c','f','h'])] * 1+
        [Trace(['a','c','f','g','e','e','e','e','f','h'])] * 1+
        [Trace(['a','c','d','c','f','g','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','f','g','d','c','f','h'])] * 1+
        [Trace(['a','c','d','c','f','g','e','e','f','h'])] * 1+
        [Trace(['a','c','d','c','d','c','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','d','c','d','c','f','h'])] * 1+
        [Trace(['a','c','d','c','d','c','e','e','f','h'])] * 1+
        [Trace(['a','c','d','c','d','b','c','e','f','h'])] * 1+
        [Trace(['a','c','d','c','d','b','b','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','f','g','e','f','h'])] * 1+
        [Trace(['a','c','d','c','e','d','c','e','f','h'])] * 1+
        [Trace(['a','c','d','c','e','d','b','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','e','f','g','f','h'])] * 1+
        [Trace(['a','c','d','c','e','e','d','c','f','h'])] * 1+
        [Trace(['a','c','d','c','e','e','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','f','g','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','d','c','e','f','h'])] * 1+
        [Trace(['a','c','d','b','c','d','b','c','f','h'])] * 1+
        [Trace(['a','c','d','b','c','e','f','g','f','h'])] * 1+
        [Trace(['a','c','d','b','c','e','d','c','f','h'])] * 1+
        [Trace(['a','c','d','b','c','e','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','c','f','g','f','h'])] * 1+
        [Trace(['a','c','d','b','b','c','d','c','f','h'])] * 1+
        [Trace(['a','c','d','b','b','c','e','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','b','c','e','f','h'])] * 1+
        [Trace(['a','c','d','b','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','f','g','e','f','h'])] * 1+
        [Trace(['a','c','e','f','g','d','c','e','f','h'])] * 1+
        [Trace(['a','c','e','f','g','d','b','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','e','f','g','f','h'])] * 1+
        [Trace(['a','c','e','f','g','e','d','c','f','h'])] * 1+
        [Trace(['a','c','e','f','g','e','e','e','f','h'])] * 1+
        [Trace(['a','c','e','d','c','f','g','e','f','h'])] * 1+
        [Trace(['a','c','e','d','c','d','c','e','f','h'])] * 1+
        [Trace(['a','c','e','d','c','d','b','c','f','h'])] * 1+
        [Trace(['a','c','e','d','c','e','f','g','f','h'])] * 1+
        [Trace(['a','c','e','d','c','e','d','c','f','h'])] * 1+
        [Trace(['a','c','e','d','c','e','e','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','c','f','g','f','h'])] * 1+
        [Trace(['a','c','e','d','b','c','d','c','f','h'])] * 1+
        [Trace(['a','c','e','d','b','c','e','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','b','c','e','f','h'])] * 1+
        [Trace(['a','c','e','d','b','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','e','f','g','f','g','f','h'])] * 1+
        [Trace(['a','c','e','e','f','g','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','f','g','e','e','f','h'])] * 1+
        [Trace(['a','c','e','e','d','c','f','g','f','h'])] * 1+
        [Trace(['a','c','e','e','d','c','d','c','f','h'])] * 1+
        [Trace(['a','c','e','e','d','c','e','e','f','h'])] * 1+
        [Trace(['a','c','e','e','d','b','c','e','f','h'])] * 1+
        [Trace(['a','c','e','e','d','b','b','c','f','h'])] * 1+
        [Trace(['a','c','e','e','e','f','g','e','f','h'])] * 1+
        [Trace(['a','c','e','e','e','d','c','e','f','h'])] * 1+
        [Trace(['a','c','e','e','e','d','b','c','f','h'])] * 1
)
alpha_plus_lpn_4 = LabelledPetriNet(
        places=[
                Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0"),      
                Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a"),
                Place("P_({'f'},{'g', 'h'})",pid="3ce5ed1e-c6cb-4c63-aa0c-a16b1f467f76"),
                Place("P_sink",pid="958f7ae7-6525-4c5d-87dd-5cb991e2fc8d"),
                Place("P_initial",pid="45452dc7-3d9d-4cca-a585-cf26ddd02526"),
        ],
        transitions=[
                Transition("e",tid="ffe1fce2-e81a-4f6c-b4b9-817b9fe558fe",weight=1.0,silent=False), 
                Transition("d",tid="233e8e3f-af75-44ca-8a91-c0457840ea72",weight=1.0,silent=False), 
                Transition("a",tid="67f34c5e-1cba-475f-8c0a-d2429d5ecb4f",weight=1.0,silent=False), 
                Transition("b",tid="2020a137-1dae-4534-b4aa-38a48c5ae238",weight=1.0,silent=False), 
                Transition("c",tid="9cc9da20-78ce-4a7f-b9d7-35ce7c7fcc41",weight=1.0,silent=False), 
                Transition("g",tid="d4d2b513-90bb-4651-9607-37beb3a73af9",weight=1.0,silent=False), 
                Transition("h",tid="6832baf4-c712-416c-9327-f19c8f736419",weight=1.0,silent=False), 
                Transition("f",tid="ffbfd3e5-a05e-4b90-82ea-f938f47ba85c",weight=1.0,silent=False), 
        ],
        arcs=[
                Arc(from_node=Transition("f",tid="ffbfd3e5-a05e-4b90-82ea-f938f47ba85c",weight=1.0,silent=False),to_node=Place("P_({'f'},{'g', 'h'})",pid="3ce5ed1e-c6cb-4c63-aa0c-a16b1f467f76")),     
                Arc(from_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0"),to_node=Transition("d",tid="233e8e3f-af75-44ca-8a91-c0457840ea72",weight=1.0,silent=False)),
                Arc(from_node=Transition("h",tid="6832baf4-c712-416c-9327-f19c8f736419",weight=1.0,silent=False),to_node=Place("P_sink",pid="958f7ae7-6525-4c5d-87dd-5cb991e2fc8d")),
                Arc(from_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0"),to_node=Transition("e",tid="ffe1fce2-e81a-4f6c-b4b9-817b9fe558fe",weight=1.0,silent=False)),
                Arc(from_node=Transition("e",tid="ffe1fce2-e81a-4f6c-b4b9-817b9fe558fe",weight=1.0,silent=False),to_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0")),
                Arc(from_node=Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a"),to_node=Transition("b",tid="2020a137-1dae-4534-b4aa-38a48c5ae238",weight=1.0,silent=False)),     
                Arc(from_node=Transition("b",tid="2020a137-1dae-4534-b4aa-38a48c5ae238",weight=1.0,silent=False),to_node=Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a")),     
                Arc(from_node=Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a"),to_node=Transition("c",tid="9cc9da20-78ce-4a7f-b9d7-35ce7c7fcc41",weight=1.0,silent=False)),     
                Arc(from_node=Transition("g",tid="d4d2b513-90bb-4651-9607-37beb3a73af9",weight=1.0,silent=False),to_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0")),
                Arc(from_node=Place("P_initial",pid="45452dc7-3d9d-4cca-a585-cf26ddd02526"),to_node=Transition("a",tid="67f34c5e-1cba-475f-8c0a-d2429d5ecb4f",weight=1.0,silent=False)),
                Arc(from_node=Transition("a",tid="67f34c5e-1cba-475f-8c0a-d2429d5ecb4f",weight=1.0,silent=False),to_node=Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a")),     
                Arc(from_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0"),to_node=Transition("f",tid="ffbfd3e5-a05e-4b90-82ea-f938f47ba85c",weight=1.0,silent=False)),
                Arc(from_node=Transition("c",tid="9cc9da20-78ce-4a7f-b9d7-35ce7c7fcc41",weight=1.0,silent=False),to_node=Place("P_({'c', 'g'},{'d', 'f'})",pid="00bc70ae-8007-46c7-9442-f05f23d114d0")),
                Arc(from_node=Place("P_({'f'},{'g', 'h'})",pid="3ce5ed1e-c6cb-4c63-aa0c-a16b1f467f76"),to_node=Transition("g",tid="d4d2b513-90bb-4651-9607-37beb3a73af9",weight=1.0,silent=False)),     
                Arc(from_node=Transition("d",tid="233e8e3f-af75-44ca-8a91-c0457840ea72",weight=1.0,silent=False),to_node=Place("P_({'a', 'd'},{'c'})",pid="2782e2ef-3947-4b94-b61f-af462dfe4c6a")),     
                Arc(from_node=Place("P_({'f'},{'g', 'h'})",pid="3ce5ed1e-c6cb-4c63-aa0c-a16b1f467f76"),to_node=Transition("h",tid="6832baf4-c712-416c-9327-f19c8f736419",weight=1.0,silent=False)),     
        ],
        name='Petri net'
)
alpha_plus_log_5 = EventLog(
	[Trace(['a','b','f','i','d','h','j'])] * 1+
	[Trace(['a','b','f','d','i','h','j'])] * 1+
	[Trace(['a','b','f','d','h','i','j'])] * 1+
	[Trace(['a','b','d','f','i','h','j'])] * 1+
	[Trace(['a','b','d','f','h','i','j'])] * 1+
	[Trace(['a','b','d','h','f','i','j'])] * 1+
	[Trace(['a','d','h','b','f','i','j'])] * 1+
	[Trace(['a','d','b','f','i','h','j'])] * 1+
	[Trace(['a','d','b','f','h','i','j'])] * 1+
	[Trace(['a','d','b','h','f','i','j'])] * 1+
	[Trace(['a','b','f','i','d','z','h','j'])] * 2+
	[Trace(['a','b','f','d','i','z','h','j'])] * 2+
	[Trace(['a','b','f','d','z','i','h','j'])] * 2+
	[Trace(['a','b','f','d','z','h','i','j'])] * 2+
	[Trace(['a','b','d','z','f','i','h','j'])] * 2+
	[Trace(['a','b','d','z','f','h','i','j'])] * 2+
	[Trace(['a','b','d','z','h','f','i','j'])] * 2+
	[Trace(['a','b','d','f','i','z','h','j'])] * 2+
	[Trace(['a','b','d','f','z','i','h','j'])] * 2+
	[Trace(['a','b','d','f','z','h','i','j'])] * 2+
	[Trace(['a','d','z','h','b','f','i','j'])] * 2+
	[Trace(['a','d','z','b','f','i','h','j'])] * 2+
	[Trace(['a','d','z','b','f','h','i','j'])] * 2+
	[Trace(['a','d','z','b','h','f','i','j'])] * 2+
	[Trace(['a','d','b','z','f','i','h','j'])] * 2+
	[Trace(['a','d','b','z','f','h','i','j'])] * 2+
	[Trace(['a','d','b','z','h','f','i','j'])] * 2+
	[Trace(['a','d','b','f','i','z','h','j'])] * 2+
	[Trace(['a','d','b','f','z','i','h','j'])] * 2+
	[Trace(['a','d','b','f','z','h','i','j'])] * 2+
	[Trace(['a','b','f','i','d','z','z','h','j'])] * 4+
	[Trace(['a','b','f','d','i','z','z','h','j'])] * 4+
	[Trace(['a','b','f','d','e','f','i','h','j'])] * 1+
	[Trace(['a','b','f','d','e','f','h','i','j'])] * 1+
	[Trace(['a','b','f','d','e','h','f','i','j'])] * 1+
	[Trace(['a','b','f','d','z','i','z','h','j'])] * 4+
	[Trace(['a','b','f','d','z','z','i','h','j'])] * 4+
	[Trace(['a','b','f','d','z','z','h','i','j'])] * 4+
	[Trace(['a','b','f','d','h','e','f','i','j'])] * 1+
	[Trace(['a','b','f','e','f','i','d','h','j'])] * 1+
	[Trace(['a','b','f','e','f','d','i','h','j'])] * 1+
	[Trace(['a','b','f','e','f','d','h','i','j'])] * 1+
	[Trace(['a','b','f','e','d','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','d','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','d','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','f','i','d','h','j'])] * 1+
	[Trace(['a','b','c','b','f','d','i','h','j'])] * 1+
	[Trace(['a','b','c','b','f','d','h','i','j'])] * 1+
	[Trace(['a','b','c','b','d','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','d','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','d','h','f','i','j'])] * 1+
	[Trace(['a','b','c','d','h','b','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','f','i','h','j'])] * 1+
	[Trace(['a','b','c','d','b','f','h','i','j'])] * 1+
	[Trace(['a','b','c','d','b','h','f','i','j'])] * 1+
	[Trace(['a','b','d','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','d','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','d','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','d','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','d','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','d','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','d','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','d','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','d','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','d','c','b','h','f','i','j'])] * 1+
	[Trace(['a','d','z','z','h','b','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','f','i','h','j'])] * 4+
	[Trace(['a','d','z','z','b','f','h','i','j'])] * 4+
	[Trace(['a','d','z','z','b','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','z','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','z','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','f','i','z','h','j'])] * 4+
	[Trace(['a','d','z','b','f','z','i','h','j'])] * 4+
	[Trace(['a','d','z','b','f','z','h','i','j'])] * 4+
	[Trace(['a','d','h','b','f','e','f','i','j'])] * 1+
	[Trace(['a','d','h','b','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','z','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','z','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','z','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','i','z','z','h','j'])] * 4+
	[Trace(['a','d','b','f','e','f','i','h','j'])] * 1+
	[Trace(['a','d','b','f','e','f','h','i','j'])] * 1+
	[Trace(['a','d','b','f','e','h','f','i','j'])] * 1+
	[Trace(['a','d','b','f','z','i','z','h','j'])] * 4+
	[Trace(['a','d','b','f','z','z','i','h','j'])] * 4+
	[Trace(['a','d','b','f','z','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','h','e','f','i','j'])] * 1+
	[Trace(['a','d','b','h','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','h','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','h','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','f','i','h','j'])] * 1+
	[Trace(['a','d','b','c','b','f','h','i','j'])] * 1+
	[Trace(['a','d','b','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','f','i','d','z','z','z','h','j'])] * 8+
	[Trace(['a','b','f','d','i','z','z','z','h','j'])] * 8+
	[Trace(['a','b','f','d','e','z','f','i','h','j'])] * 2+
	[Trace(['a','b','f','d','e','z','f','h','i','j'])] * 2+
	[Trace(['a','b','f','d','e','z','h','f','i','j'])] * 2+
	[Trace(['a','b','f','d','e','f','i','z','h','j'])] * 2+
	[Trace(['a','b','f','d','e','f','z','i','h','j'])] * 2+
	[Trace(['a','b','f','d','e','f','z','h','i','j'])] * 2+
	[Trace(['a','b','f','d','z','i','z','z','h','j'])] * 8+
	[Trace(['a','b','f','d','z','e','f','i','h','j'])] * 2+
	[Trace(['a','b','f','d','z','e','f','h','i','j'])] * 2+
	[Trace(['a','b','f','d','z','e','h','f','i','j'])] * 2+
	[Trace(['a','b','f','d','z','z','i','z','h','j'])] * 8+
	[Trace(['a','b','f','d','z','z','z','i','h','j'])] * 8+
	[Trace(['a','b','f','d','z','z','z','h','i','j'])] * 8+
	[Trace(['a','b','f','d','z','h','e','f','i','j'])] * 2+
	[Trace(['a','b','f','e','f','i','d','z','h','j'])] * 2+
	[Trace(['a','b','f','e','f','d','i','z','h','j'])] * 2+
	[Trace(['a','b','f','e','f','d','z','i','h','j'])] * 2+
	[Trace(['a','b','f','e','f','d','z','h','i','j'])] * 2+
	[Trace(['a','b','f','e','d','z','f','i','h','j'])] * 2+
	[Trace(['a','b','f','e','d','z','f','h','i','j'])] * 2+
	[Trace(['a','b','f','e','d','z','h','f','i','j'])] * 2+
	[Trace(['a','b','f','e','d','f','i','z','h','j'])] * 2+
	[Trace(['a','b','f','e','d','f','z','i','h','j'])] * 2+
	[Trace(['a','b','f','e','d','f','z','h','i','j'])] * 2+
	[Trace(['a','b','c','b','f','i','d','z','h','j'])] * 2+
	[Trace(['a','b','c','b','f','d','i','z','h','j'])] * 2+
	[Trace(['a','b','c','b','f','d','z','i','h','j'])] * 2+
	[Trace(['a','b','c','b','f','d','z','h','i','j'])] * 2+
	[Trace(['a','b','c','b','d','z','f','i','h','j'])] * 2+
	[Trace(['a','b','c','b','d','z','f','h','i','j'])] * 2+
	[Trace(['a','b','c','b','d','z','h','f','i','j'])] * 2+
	[Trace(['a','b','c','b','d','f','i','z','h','j'])] * 2+
	[Trace(['a','b','c','b','d','f','z','i','h','j'])] * 2+
	[Trace(['a','b','c','b','d','f','z','h','i','j'])] * 2+
	[Trace(['a','b','c','d','z','h','b','f','i','j'])] * 2+
	[Trace(['a','b','c','d','z','b','f','i','h','j'])] * 2+
	[Trace(['a','b','c','d','z','b','f','h','i','j'])] * 2+
	[Trace(['a','b','c','d','z','b','h','f','i','j'])] * 2+
	[Trace(['a','b','c','d','b','z','f','i','h','j'])] * 2+
	[Trace(['a','b','c','d','b','z','f','h','i','j'])] * 2+
	[Trace(['a','b','c','d','b','z','h','f','i','j'])] * 2+
	[Trace(['a','b','c','d','b','f','i','z','h','j'])] * 2+
	[Trace(['a','b','c','d','b','f','z','i','h','j'])] * 2+
	[Trace(['a','b','c','d','b','f','z','h','i','j'])] * 2+
	[Trace(['a','b','d','z','z','z','f','i','h','j'])] * 8+
	[Trace(['a','b','d','z','z','z','f','h','i','j'])] * 8+
	[Trace(['a','b','d','z','z','z','h','f','i','j'])] * 8+
	[Trace(['a','b','d','z','z','f','i','z','h','j'])] * 8+
	[Trace(['a','b','d','z','z','f','z','i','h','j'])] * 8+
	[Trace(['a','b','d','z','z','f','z','h','i','j'])] * 8+
	[Trace(['a','b','d','z','f','i','z','z','h','j'])] * 8+
	[Trace(['a','b','d','z','f','e','f','i','h','j'])] * 2+
	[Trace(['a','b','d','z','f','e','f','h','i','j'])] * 2+
	[Trace(['a','b','d','z','f','e','h','f','i','j'])] * 2+
	[Trace(['a','b','d','z','f','z','i','z','h','j'])] * 8+
	[Trace(['a','b','d','z','f','z','z','i','h','j'])] * 8+
	[Trace(['a','b','d','z','f','z','z','h','i','j'])] * 8+
	[Trace(['a','b','d','z','f','h','e','f','i','j'])] * 2+
	[Trace(['a','b','d','z','h','f','e','f','i','j'])] * 2+
	[Trace(['a','b','d','z','h','c','b','f','i','j'])] * 2+
	[Trace(['a','b','d','z','c','h','b','f','i','j'])] * 2+
	[Trace(['a','b','d','z','c','b','f','i','h','j'])] * 2+
	[Trace(['a','b','d','z','c','b','f','h','i','j'])] * 2+
	[Trace(['a','b','d','z','c','b','h','f','i','j'])] * 2+
	[Trace(['a','b','d','f','i','z','z','z','h','j'])] * 8+
	[Trace(['a','b','d','f','e','z','f','i','h','j'])] * 2+
	[Trace(['a','b','d','f','e','z','f','h','i','j'])] * 2+
	[Trace(['a','b','d','f','e','z','h','f','i','j'])] * 2+
	[Trace(['a','b','d','f','e','f','i','z','h','j'])] * 2+
	[Trace(['a','b','d','f','e','f','z','i','h','j'])] * 2+
	[Trace(['a','b','d','f','e','f','z','h','i','j'])] * 2+
	[Trace(['a','b','d','f','z','i','z','z','h','j'])] * 8+
	[Trace(['a','b','d','f','z','e','f','i','h','j'])] * 2+
	[Trace(['a','b','d','f','z','e','f','h','i','j'])] * 2+
	[Trace(['a','b','d','f','z','e','h','f','i','j'])] * 2+
	[Trace(['a','b','d','f','z','z','i','z','h','j'])] * 8+
	[Trace(['a','b','d','f','z','z','z','i','h','j'])] * 8+
	[Trace(['a','b','d','f','z','z','z','h','i','j'])] * 8+
	[Trace(['a','b','d','f','z','h','e','f','i','j'])] * 2+
	[Trace(['a','b','d','c','z','h','b','f','i','j'])] * 2+
	[Trace(['a','b','d','c','z','b','f','i','h','j'])] * 2+
	[Trace(['a','b','d','c','z','b','f','h','i','j'])] * 2+
	[Trace(['a','b','d','c','z','b','h','f','i','j'])] * 2+
	[Trace(['a','b','d','c','b','z','f','i','h','j'])] * 2+
	[Trace(['a','b','d','c','b','z','f','h','i','j'])] * 2+
	[Trace(['a','b','d','c','b','z','h','f','i','j'])] * 2+
	[Trace(['a','b','d','c','b','f','i','z','h','j'])] * 2+
	[Trace(['a','b','d','c','b','f','z','i','h','j'])] * 2+
	[Trace(['a','b','d','c','b','f','z','h','i','j'])] * 2+
	[Trace(['a','d','z','z','z','h','b','f','i','j'])] * 8+
	[Trace(['a','d','z','z','z','b','f','i','h','j'])] * 8+
	[Trace(['a','d','z','z','z','b','f','h','i','j'])] * 8+
	[Trace(['a','d','z','z','z','b','h','f','i','j'])] * 8+
	[Trace(['a','d','z','z','b','z','f','i','h','j'])] * 8+
	[Trace(['a','d','z','z','b','z','f','h','i','j'])] * 8+
	[Trace(['a','d','z','z','b','z','h','f','i','j'])] * 8+
	[Trace(['a','d','z','z','b','f','i','z','h','j'])] * 8+
	[Trace(['a','d','z','z','b','f','z','i','h','j'])] * 8+
	[Trace(['a','d','z','z','b','f','z','h','i','j'])] * 8+
	[Trace(['a','d','z','h','b','f','e','f','i','j'])] * 2+
	[Trace(['a','d','z','h','b','c','b','f','i','j'])] * 2+
	[Trace(['a','d','z','b','z','z','f','i','h','j'])] * 8+
	[Trace(['a','d','z','b','z','z','f','h','i','j'])] * 8+
	[Trace(['a','d','z','b','z','z','h','f','i','j'])] * 8+
	[Trace(['a','d','z','b','z','f','i','z','h','j'])] * 8+
	[Trace(['a','d','z','b','z','f','z','i','h','j'])] * 8+
	[Trace(['a','d','z','b','z','f','z','h','i','j'])] * 8+
	[Trace(['a','d','z','b','f','i','z','z','h','j'])] * 8+
	[Trace(['a','d','z','b','f','e','f','i','h','j'])] * 2+
	[Trace(['a','d','z','b','f','e','f','h','i','j'])] * 2+
	[Trace(['a','d','z','b','f','e','h','f','i','j'])] * 2+
	[Trace(['a','d','z','b','f','z','i','z','h','j'])] * 8+
	[Trace(['a','d','z','b','f','z','z','i','h','j'])] * 8+
	[Trace(['a','d','z','b','f','z','z','h','i','j'])] * 8+
	[Trace(['a','d','z','b','f','h','e','f','i','j'])] * 2+
	[Trace(['a','d','z','b','h','f','e','f','i','j'])] * 2+
	[Trace(['a','d','z','b','h','c','b','f','i','j'])] * 2+
	[Trace(['a','d','z','b','c','h','b','f','i','j'])] * 2+
	[Trace(['a','d','z','b','c','b','f','i','h','j'])] * 2+
	[Trace(['a','d','z','b','c','b','f','h','i','j'])] * 2+
	[Trace(['a','d','z','b','c','b','h','f','i','j'])] * 2+
	[Trace(['a','d','b','z','z','z','f','i','h','j'])] * 8+
	[Trace(['a','d','b','z','z','z','f','h','i','j'])] * 8+
	[Trace(['a','d','b','z','z','z','h','f','i','j'])] * 8+
	[Trace(['a','d','b','z','z','f','i','z','h','j'])] * 8+
	[Trace(['a','d','b','z','z','f','z','i','h','j'])] * 8+
	[Trace(['a','d','b','z','z','f','z','h','i','j'])] * 8+
	[Trace(['a','d','b','z','f','i','z','z','h','j'])] * 8+
	[Trace(['a','d','b','z','f','e','f','i','h','j'])] * 2+
	[Trace(['a','d','b','z','f','e','f','h','i','j'])] * 2+
	[Trace(['a','d','b','z','f','e','h','f','i','j'])] * 2+
	[Trace(['a','d','b','z','f','z','i','z','h','j'])] * 8+
	[Trace(['a','d','b','z','f','z','z','i','h','j'])] * 8+
	[Trace(['a','d','b','z','f','z','z','h','i','j'])] * 8+
	[Trace(['a','d','b','z','f','h','e','f','i','j'])] * 2+
	[Trace(['a','d','b','z','h','f','e','f','i','j'])] * 2+
	[Trace(['a','d','b','z','h','c','b','f','i','j'])] * 2+
	[Trace(['a','d','b','z','c','h','b','f','i','j'])] * 2+
	[Trace(['a','d','b','z','c','b','f','i','h','j'])] * 2+
	[Trace(['a','d','b','z','c','b','f','h','i','j'])] * 2+
	[Trace(['a','d','b','z','c','b','h','f','i','j'])] * 2+
	[Trace(['a','d','b','f','i','z','z','z','h','j'])] * 8+
	[Trace(['a','d','b','f','e','z','f','i','h','j'])] * 2+
	[Trace(['a','d','b','f','e','z','f','h','i','j'])] * 2+
	[Trace(['a','d','b','f','e','z','h','f','i','j'])] * 2+
	[Trace(['a','d','b','f','e','f','i','z','h','j'])] * 2+
	[Trace(['a','d','b','f','e','f','z','i','h','j'])] * 2+
	[Trace(['a','d','b','f','e','f','z','h','i','j'])] * 2+
	[Trace(['a','d','b','f','z','i','z','z','h','j'])] * 8+
	[Trace(['a','d','b','f','z','e','f','i','h','j'])] * 2+
	[Trace(['a','d','b','f','z','e','f','h','i','j'])] * 2+
	[Trace(['a','d','b','f','z','e','h','f','i','j'])] * 2+
	[Trace(['a','d','b','f','z','z','i','z','h','j'])] * 8+
	[Trace(['a','d','b','f','z','z','z','i','h','j'])] * 8+
	[Trace(['a','d','b','f','z','z','z','h','i','j'])] * 8+
	[Trace(['a','d','b','f','z','h','e','f','i','j'])] * 2+
	[Trace(['a','d','b','c','z','h','b','f','i','j'])] * 2+
	[Trace(['a','d','b','c','z','b','f','i','h','j'])] * 2+
	[Trace(['a','d','b','c','z','b','f','h','i','j'])] * 2+
	[Trace(['a','d','b','c','z','b','h','f','i','j'])] * 2+
	[Trace(['a','d','b','c','b','z','f','i','h','j'])] * 2+
	[Trace(['a','d','b','c','b','z','f','h','i','j'])] * 2+
	[Trace(['a','d','b','c','b','z','h','f','i','j'])] * 2+
	[Trace(['a','d','b','c','b','f','i','z','h','j'])] * 2+
	[Trace(['a','d','b','c','b','f','z','i','h','j'])] * 2+
	[Trace(['a','d','b','c','b','f','z','h','i','j'])] * 2+
	[Trace(['a','b','f','i','d','z','z','z','z','h','j'])] * 16+
	[Trace(['a','b','f','d','i','z','z','z','z','h','j'])] * 16+
	[Trace(['a','b','f','d','e','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','f','d','e','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','f','d','e','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','f','d','e','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','f','d','e','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','f','d','e','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','f','d','e','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','f','d','e','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','f','d','e','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','f','d','e','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','f','d','e','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','f','d','e','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','f','d','e','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','f','d','e','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','f','d','e','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','f','d','e','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','f','d','e','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','f','d','e','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','f','d','e','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','f','d','e','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','f','d','z','i','z','z','z','h','j'])] * 16+
	[Trace(['a','b','f','d','z','e','z','f','i','h','j'])] * 4+
	[Trace(['a','b','f','d','z','e','z','f','h','i','j'])] * 4+
	[Trace(['a','b','f','d','z','e','z','h','f','i','j'])] * 4+
	[Trace(['a','b','f','d','z','e','f','i','z','h','j'])] * 4+
	[Trace(['a','b','f','d','z','e','f','z','i','h','j'])] * 4+
	[Trace(['a','b','f','d','z','e','f','z','h','i','j'])] * 4+
	[Trace(['a','b','f','d','z','z','i','z','z','h','j'])] * 16+
	[Trace(['a','b','f','d','z','z','e','f','i','h','j'])] * 4+
	[Trace(['a','b','f','d','z','z','e','f','h','i','j'])] * 4+
	[Trace(['a','b','f','d','z','z','e','h','f','i','j'])] * 4+
	[Trace(['a','b','f','d','z','z','z','i','z','h','j'])] * 16+
	[Trace(['a','b','f','d','z','z','z','z','i','h','j'])] * 16+
	[Trace(['a','b','f','d','z','z','z','z','h','i','j'])] * 16+
	[Trace(['a','b','f','d','z','z','h','e','f','i','j'])] * 4+
	[Trace(['a','b','f','d','h','e','f','e','f','i','j'])] * 1+
	[Trace(['a','b','f','d','h','e','c','b','f','i','j'])] * 1+
	[Trace(['a','b','f','e','f','i','d','z','z','h','j'])] * 4+
	[Trace(['a','b','f','e','f','d','i','z','z','h','j'])] * 4+
	[Trace(['a','b','f','e','f','d','e','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','f','d','e','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','f','d','e','h','f','i','j'])] * 1+
	[Trace(['a','b','f','e','f','d','z','i','z','h','j'])] * 4+
	[Trace(['a','b','f','e','f','d','z','z','i','h','j'])] * 4+
	[Trace(['a','b','f','e','f','d','z','z','h','i','j'])] * 4+
	[Trace(['a','b','f','e','f','d','h','e','f','i','j'])] * 1+
	[Trace(['a','b','f','e','f','e','f','i','d','h','j'])] * 1+
	[Trace(['a','b','f','e','f','e','f','d','i','h','j'])] * 1+
	[Trace(['a','b','f','e','f','e','f','d','h','i','j'])] * 1+
	[Trace(['a','b','f','e','f','e','d','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','f','e','d','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','f','e','d','h','f','i','j'])] * 1+
	[Trace(['a','b','f','e','c','b','f','i','d','h','j'])] * 1+
	[Trace(['a','b','f','e','c','b','f','d','i','h','j'])] * 1+
	[Trace(['a','b','f','e','c','b','f','d','h','i','j'])] * 1+
	[Trace(['a','b','f','e','c','b','d','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','c','b','d','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','c','b','d','h','f','i','j'])] * 1+
	[Trace(['a','b','f','e','c','d','h','b','f','i','j'])] * 1+
	[Trace(['a','b','f','e','c','d','b','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','c','d','b','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','c','d','b','h','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','f','e','d','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','f','e','d','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','f','e','d','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','f','e','d','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','f','e','d','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','f','e','d','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','f','e','d','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','d','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','d','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','f','e','d','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','f','e','d','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','f','e','d','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','f','e','d','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','f','e','d','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','f','e','d','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','f','i','d','z','z','h','j'])] * 4+
	[Trace(['a','b','c','b','f','d','i','z','z','h','j'])] * 4+
	[Trace(['a','b','c','b','f','d','e','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','f','d','e','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','f','d','e','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','f','d','z','i','z','h','j'])] * 4+
	[Trace(['a','b','c','b','f','d','z','z','i','h','j'])] * 4+
	[Trace(['a','b','c','b','f','d','z','z','h','i','j'])] * 4+
	[Trace(['a','b','c','b','f','d','h','e','f','i','j'])] * 1+
	[Trace(['a','b','c','b','f','e','f','i','d','h','j'])] * 1+
	[Trace(['a','b','c','b','f','e','f','d','i','h','j'])] * 1+
	[Trace(['a','b','c','b','f','e','f','d','h','i','j'])] * 1+
	[Trace(['a','b','c','b','f','e','d','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','f','e','d','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','f','e','d','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','c','b','f','i','d','h','j'])] * 1+
	[Trace(['a','b','c','b','c','b','f','d','i','h','j'])] * 1+
	[Trace(['a','b','c','b','c','b','f','d','h','i','j'])] * 1+
	[Trace(['a','b','c','b','c','b','d','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','c','b','d','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','c','b','d','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','c','d','h','b','f','i','j'])] * 1+
	[Trace(['a','b','c','b','c','d','b','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','c','d','b','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','c','d','b','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','c','b','d','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','c','b','d','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','c','b','d','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','c','b','d','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','c','b','d','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','c','b','d','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','c','b','d','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','d','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','d','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','c','b','d','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','c','b','d','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','c','b','d','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','c','b','d','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','c','b','d','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','c','b','d','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','c','d','z','z','h','b','f','i','j'])] * 4+
	[Trace(['a','b','c','d','z','z','b','f','i','h','j'])] * 4+
	[Trace(['a','b','c','d','z','z','b','f','h','i','j'])] * 4+
	[Trace(['a','b','c','d','z','z','b','h','f','i','j'])] * 4+
	[Trace(['a','b','c','d','z','b','z','f','i','h','j'])] * 4+
	[Trace(['a','b','c','d','z','b','z','f','h','i','j'])] * 4+
	[Trace(['a','b','c','d','z','b','z','h','f','i','j'])] * 4+
	[Trace(['a','b','c','d','z','b','f','i','z','h','j'])] * 4+
	[Trace(['a','b','c','d','z','b','f','z','i','h','j'])] * 4+
	[Trace(['a','b','c','d','z','b','f','z','h','i','j'])] * 4+
	[Trace(['a','b','c','d','h','b','f','e','f','i','j'])] * 1+
	[Trace(['a','b','c','d','h','b','c','b','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','c','d','b','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','c','d','b','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','c','d','b','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','c','d','b','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','c','d','b','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','c','d','b','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','c','d','b','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','c','d','b','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','c','d','b','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','c','d','b','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','c','d','b','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','c','d','b','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','c','d','b','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','c','d','b','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','c','d','b','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','d','z','z','z','z','f','i','h','j'])] * 16+
	[Trace(['a','b','d','z','z','z','z','f','h','i','j'])] * 16+
	[Trace(['a','b','d','z','z','z','z','h','f','i','j'])] * 16+
	[Trace(['a','b','d','z','z','z','f','i','z','h','j'])] * 16+
	[Trace(['a','b','d','z','z','z','f','z','i','h','j'])] * 16+
	[Trace(['a','b','d','z','z','z','f','z','h','i','j'])] * 16+
	[Trace(['a','b','d','z','z','f','i','z','z','h','j'])] * 16+
	[Trace(['a','b','d','z','z','f','e','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','z','f','e','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','z','f','e','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','z','f','z','i','z','h','j'])] * 16+
	[Trace(['a','b','d','z','z','f','z','z','i','h','j'])] * 16+
	[Trace(['a','b','d','z','z','f','z','z','h','i','j'])] * 16+
	[Trace(['a','b','d','z','z','f','h','e','f','i','j'])] * 4+
	[Trace(['a','b','d','z','z','h','f','e','f','i','j'])] * 4+
	[Trace(['a','b','d','z','z','h','c','b','f','i','j'])] * 4+
	[Trace(['a','b','d','z','z','c','h','b','f','i','j'])] * 4+
	[Trace(['a','b','d','z','z','c','b','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','z','c','b','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','z','c','b','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','f','i','z','z','z','h','j'])] * 16+
	[Trace(['a','b','d','z','f','e','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','f','e','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','f','e','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','f','e','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','z','f','e','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','z','f','e','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','z','f','z','i','z','z','h','j'])] * 16+
	[Trace(['a','b','d','z','f','z','e','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','f','z','e','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','f','z','e','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','f','z','z','i','z','h','j'])] * 16+
	[Trace(['a','b','d','z','f','z','z','z','i','h','j'])] * 16+
	[Trace(['a','b','d','z','f','z','z','z','h','i','j'])] * 16+
	[Trace(['a','b','d','z','f','z','h','e','f','i','j'])] * 4+
	[Trace(['a','b','d','z','c','z','h','b','f','i','j'])] * 4+
	[Trace(['a','b','d','z','c','z','b','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','c','z','b','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','c','z','b','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','c','b','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','z','c','b','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','z','c','b','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','z','c','b','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','z','c','b','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','z','c','b','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','i','z','z','z','z','h','j'])] * 16+
	[Trace(['a','b','d','f','e','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','f','e','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','f','e','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','f','e','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','f','e','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','f','e','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','e','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','d','f','e','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','d','f','e','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','d','f','e','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','d','f','e','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','d','f','e','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','d','f','e','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','e','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','d','f','e','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','f','e','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','f','e','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','d','f','e','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','d','f','e','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','d','f','e','c','b','h','f','i','j'])] * 1+
	[Trace(['a','b','d','f','z','i','z','z','z','h','j'])] * 16+
	[Trace(['a','b','d','f','z','e','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','f','z','e','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','f','z','e','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','f','z','e','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','f','z','e','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','f','z','e','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','f','z','z','i','z','z','h','j'])] * 16+
	[Trace(['a','b','d','f','z','z','e','f','i','h','j'])] * 4+
	[Trace(['a','b','d','f','z','z','e','f','h','i','j'])] * 4+
	[Trace(['a','b','d','f','z','z','e','h','f','i','j'])] * 4+
	[Trace(['a','b','d','f','z','z','z','i','z','h','j'])] * 16+
	[Trace(['a','b','d','f','z','z','z','z','i','h','j'])] * 16+
	[Trace(['a','b','d','f','z','z','z','z','h','i','j'])] * 16+
	[Trace(['a','b','d','f','z','z','h','e','f','i','j'])] * 4+
	[Trace(['a','b','d','f','h','e','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','f','h','e','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','h','f','e','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','h','f','e','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','h','c','b','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','h','c','b','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','z','z','h','b','f','i','j'])] * 4+
	[Trace(['a','b','d','c','z','z','b','f','i','h','j'])] * 4+
	[Trace(['a','b','d','c','z','z','b','f','h','i','j'])] * 4+
	[Trace(['a','b','d','c','z','z','b','h','f','i','j'])] * 4+
	[Trace(['a','b','d','c','z','b','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','c','z','b','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','c','z','b','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','c','z','b','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','c','z','b','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','c','z','b','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','c','h','b','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','c','h','b','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','z','z','f','i','h','j'])] * 4+
	[Trace(['a','b','d','c','b','z','z','f','h','i','j'])] * 4+
	[Trace(['a','b','d','c','b','z','z','h','f','i','j'])] * 4+
	[Trace(['a','b','d','c','b','z','f','i','z','h','j'])] * 4+
	[Trace(['a','b','d','c','b','z','f','z','i','h','j'])] * 4+
	[Trace(['a','b','d','c','b','z','f','z','h','i','j'])] * 4+
	[Trace(['a','b','d','c','b','f','i','z','z','h','j'])] * 4+
	[Trace(['a','b','d','c','b','f','e','f','i','h','j'])] * 1+
	[Trace(['a','b','d','c','b','f','e','f','h','i','j'])] * 1+
	[Trace(['a','b','d','c','b','f','e','h','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','f','z','i','z','h','j'])] * 4+
	[Trace(['a','b','d','c','b','f','z','z','i','h','j'])] * 4+
	[Trace(['a','b','d','c','b','f','z','z','h','i','j'])] * 4+
	[Trace(['a','b','d','c','b','f','h','e','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','h','f','e','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','h','c','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','c','h','b','f','i','j'])] * 1+
	[Trace(['a','b','d','c','b','c','b','f','i','h','j'])] * 1+
	[Trace(['a','b','d','c','b','c','b','f','h','i','j'])] * 1+
	[Trace(['a','b','d','c','b','c','b','h','f','i','j'])] * 1+
	[Trace(['a','d','z','z','z','z','h','b','f','i','j'])] * 16+
	[Trace(['a','d','z','z','z','z','b','f','i','h','j'])] * 16+
	[Trace(['a','d','z','z','z','z','b','f','h','i','j'])] * 16+
	[Trace(['a','d','z','z','z','z','b','h','f','i','j'])] * 16+
	[Trace(['a','d','z','z','z','b','z','f','i','h','j'])] * 16+
	[Trace(['a','d','z','z','z','b','z','f','h','i','j'])] * 16+
	[Trace(['a','d','z','z','z','b','z','h','f','i','j'])] * 16+
	[Trace(['a','d','z','z','z','b','f','i','z','h','j'])] * 16+
	[Trace(['a','d','z','z','z','b','f','z','i','h','j'])] * 16+
	[Trace(['a','d','z','z','z','b','f','z','h','i','j'])] * 16+
	[Trace(['a','d','z','z','h','b','f','e','f','i','j'])] * 4+
	[Trace(['a','d','z','z','h','b','c','b','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','z','z','f','i','h','j'])] * 16+
	[Trace(['a','d','z','z','b','z','z','f','h','i','j'])] * 16+
	[Trace(['a','d','z','z','b','z','z','h','f','i','j'])] * 16+
	[Trace(['a','d','z','z','b','z','f','i','z','h','j'])] * 16+
	[Trace(['a','d','z','z','b','z','f','z','i','h','j'])] * 16+
	[Trace(['a','d','z','z','b','z','f','z','h','i','j'])] * 16+
	[Trace(['a','d','z','z','b','f','i','z','z','h','j'])] * 16+
	[Trace(['a','d','z','z','b','f','e','f','i','h','j'])] * 4+
	[Trace(['a','d','z','z','b','f','e','f','h','i','j'])] * 4+
	[Trace(['a','d','z','z','b','f','e','h','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','f','z','i','z','h','j'])] * 16+
	[Trace(['a','d','z','z','b','f','z','z','i','h','j'])] * 16+
	[Trace(['a','d','z','z','b','f','z','z','h','i','j'])] * 16+
	[Trace(['a','d','z','z','b','f','h','e','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','h','f','e','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','h','c','b','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','c','h','b','f','i','j'])] * 4+
	[Trace(['a','d','z','z','b','c','b','f','i','h','j'])] * 4+
	[Trace(['a','d','z','z','b','c','b','f','h','i','j'])] * 4+
	[Trace(['a','d','z','z','b','c','b','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','z','z','f','i','h','j'])] * 16+
	[Trace(['a','d','z','b','z','z','z','f','h','i','j'])] * 16+
	[Trace(['a','d','z','b','z','z','z','h','f','i','j'])] * 16+
	[Trace(['a','d','z','b','z','z','f','i','z','h','j'])] * 16+
	[Trace(['a','d','z','b','z','z','f','z','i','h','j'])] * 16+
	[Trace(['a','d','z','b','z','z','f','z','h','i','j'])] * 16+
	[Trace(['a','d','z','b','z','f','i','z','z','h','j'])] * 16+
	[Trace(['a','d','z','b','z','f','e','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','z','f','e','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','z','f','e','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','f','z','i','z','h','j'])] * 16+
	[Trace(['a','d','z','b','z','f','z','z','i','h','j'])] * 16+
	[Trace(['a','d','z','b','z','f','z','z','h','i','j'])] * 16+
	[Trace(['a','d','z','b','z','f','h','e','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','h','f','e','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','h','c','b','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','c','h','b','f','i','j'])] * 4+
	[Trace(['a','d','z','b','z','c','b','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','z','c','b','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','z','c','b','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','f','i','z','z','z','h','j'])] * 16+
	[Trace(['a','d','z','b','f','e','z','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','f','e','z','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','f','e','z','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','f','e','f','i','z','h','j'])] * 4+
	[Trace(['a','d','z','b','f','e','f','z','i','h','j'])] * 4+
	[Trace(['a','d','z','b','f','e','f','z','h','i','j'])] * 4+
	[Trace(['a','d','z','b','f','z','i','z','z','h','j'])] * 16+
	[Trace(['a','d','z','b','f','z','e','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','f','z','e','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','f','z','e','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','f','z','z','i','z','h','j'])] * 16+
	[Trace(['a','d','z','b','f','z','z','z','i','h','j'])] * 16+
	[Trace(['a','d','z','b','f','z','z','z','h','i','j'])] * 16+
	[Trace(['a','d','z','b','f','z','h','e','f','i','j'])] * 4+
	[Trace(['a','d','z','b','c','z','h','b','f','i','j'])] * 4+
	[Trace(['a','d','z','b','c','z','b','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','c','z','b','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','c','z','b','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','c','b','z','f','i','h','j'])] * 4+
	[Trace(['a','d','z','b','c','b','z','f','h','i','j'])] * 4+
	[Trace(['a','d','z','b','c','b','z','h','f','i','j'])] * 4+
	[Trace(['a','d','z','b','c','b','f','i','z','h','j'])] * 4+
	[Trace(['a','d','z','b','c','b','f','z','i','h','j'])] * 4+
	[Trace(['a','d','z','b','c','b','f','z','h','i','j'])] * 4+
	[Trace(['a','d','h','b','f','e','f','e','f','i','j'])] * 1+
	[Trace(['a','d','h','b','f','e','c','b','f','i','j'])] * 1+
	[Trace(['a','d','h','b','c','b','f','e','f','i','j'])] * 1+
	[Trace(['a','d','h','b','c','b','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','z','z','z','z','f','i','h','j'])] * 16+
	[Trace(['a','d','b','z','z','z','z','f','h','i','j'])] * 16+
	[Trace(['a','d','b','z','z','z','z','h','f','i','j'])] * 16+
	[Trace(['a','d','b','z','z','z','f','i','z','h','j'])] * 16+
	[Trace(['a','d','b','z','z','z','f','z','i','h','j'])] * 16+
	[Trace(['a','d','b','z','z','z','f','z','h','i','j'])] * 16+
	[Trace(['a','d','b','z','z','f','i','z','z','h','j'])] * 16+
	[Trace(['a','d','b','z','z','f','e','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','z','f','e','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','z','f','e','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','z','f','z','i','z','h','j'])] * 16+
	[Trace(['a','d','b','z','z','f','z','z','i','h','j'])] * 16+
	[Trace(['a','d','b','z','z','f','z','z','h','i','j'])] * 16+
	[Trace(['a','d','b','z','z','f','h','e','f','i','j'])] * 4+
	[Trace(['a','d','b','z','z','h','f','e','f','i','j'])] * 4+
	[Trace(['a','d','b','z','z','h','c','b','f','i','j'])] * 4+
	[Trace(['a','d','b','z','z','c','h','b','f','i','j'])] * 4+
	[Trace(['a','d','b','z','z','c','b','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','z','c','b','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','z','c','b','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','f','i','z','z','z','h','j'])] * 16+
	[Trace(['a','d','b','z','f','e','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','f','e','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','f','e','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','f','e','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','z','f','e','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','z','f','e','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','z','f','z','i','z','z','h','j'])] * 16+
	[Trace(['a','d','b','z','f','z','e','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','f','z','e','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','f','z','e','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','f','z','z','i','z','h','j'])] * 16+
	[Trace(['a','d','b','z','f','z','z','z','i','h','j'])] * 16+
	[Trace(['a','d','b','z','f','z','z','z','h','i','j'])] * 16+
	[Trace(['a','d','b','z','f','z','h','e','f','i','j'])] * 4+
	[Trace(['a','d','b','z','c','z','h','b','f','i','j'])] * 4+
	[Trace(['a','d','b','z','c','z','b','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','c','z','b','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','c','z','b','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','c','b','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','z','c','b','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','z','c','b','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','z','c','b','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','z','c','b','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','z','c','b','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','i','z','z','z','z','h','j'])] * 16+
	[Trace(['a','d','b','f','e','z','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','f','e','z','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','f','e','z','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','f','e','z','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','f','e','z','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','f','e','z','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','e','f','i','z','z','h','j'])] * 4+
	[Trace(['a','d','b','f','e','f','e','f','i','h','j'])] * 1+
	[Trace(['a','d','b','f','e','f','e','f','h','i','j'])] * 1+
	[Trace(['a','d','b','f','e','f','e','h','f','i','j'])] * 1+
	[Trace(['a','d','b','f','e','f','z','i','z','h','j'])] * 4+
	[Trace(['a','d','b','f','e','f','z','z','i','h','j'])] * 4+
	[Trace(['a','d','b','f','e','f','z','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','e','f','h','e','f','i','j'])] * 1+
	[Trace(['a','d','b','f','e','h','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','f','e','h','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','f','e','c','h','b','f','i','j'])] * 1+
	[Trace(['a','d','b','f','e','c','b','f','i','h','j'])] * 1+
	[Trace(['a','d','b','f','e','c','b','f','h','i','j'])] * 1+
	[Trace(['a','d','b','f','e','c','b','h','f','i','j'])] * 1+
	[Trace(['a','d','b','f','z','i','z','z','z','h','j'])] * 16+
	[Trace(['a','d','b','f','z','e','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','f','z','e','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','f','z','e','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','f','z','e','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','f','z','e','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','f','z','e','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','f','z','z','i','z','z','h','j'])] * 16+
	[Trace(['a','d','b','f','z','z','e','f','i','h','j'])] * 4+
	[Trace(['a','d','b','f','z','z','e','f','h','i','j'])] * 4+
	[Trace(['a','d','b','f','z','z','e','h','f','i','j'])] * 4+
	[Trace(['a','d','b','f','z','z','z','i','z','h','j'])] * 16+
	[Trace(['a','d','b','f','z','z','z','z','i','h','j'])] * 16+
	[Trace(['a','d','b','f','z','z','z','z','h','i','j'])] * 16+
	[Trace(['a','d','b','f','z','z','h','e','f','i','j'])] * 4+
	[Trace(['a','d','b','f','h','e','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','f','h','e','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','h','f','e','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','h','f','e','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','h','c','b','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','h','c','b','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','z','z','h','b','f','i','j'])] * 4+
	[Trace(['a','d','b','c','z','z','b','f','i','h','j'])] * 4+
	[Trace(['a','d','b','c','z','z','b','f','h','i','j'])] * 4+
	[Trace(['a','d','b','c','z','z','b','h','f','i','j'])] * 4+
	[Trace(['a','d','b','c','z','b','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','c','z','b','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','c','z','b','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','c','z','b','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','c','z','b','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','c','z','b','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','c','h','b','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','c','h','b','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','z','z','f','i','h','j'])] * 4+
	[Trace(['a','d','b','c','b','z','z','f','h','i','j'])] * 4+
	[Trace(['a','d','b','c','b','z','z','h','f','i','j'])] * 4+
	[Trace(['a','d','b','c','b','z','f','i','z','h','j'])] * 4+
	[Trace(['a','d','b','c','b','z','f','z','i','h','j'])] * 4+
	[Trace(['a','d','b','c','b','z','f','z','h','i','j'])] * 4+
	[Trace(['a','d','b','c','b','f','i','z','z','h','j'])] * 4+
	[Trace(['a','d','b','c','b','f','e','f','i','h','j'])] * 1+
	[Trace(['a','d','b','c','b','f','e','f','h','i','j'])] * 1+
	[Trace(['a','d','b','c','b','f','e','h','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','f','z','i','z','h','j'])] * 4+
	[Trace(['a','d','b','c','b','f','z','z','i','h','j'])] * 4+
	[Trace(['a','d','b','c','b','f','z','z','h','i','j'])] * 4+
	[Trace(['a','d','b','c','b','f','h','e','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','h','f','e','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','h','c','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','c','h','b','f','i','j'])] * 1+
	[Trace(['a','d','b','c','b','c','b','f','i','h','j'])] * 1+
	[Trace(['a','d','b','c','b','c','b','f','h','i','j'])] * 1+
	[Trace(['a','d','b','c','b','c','b','h','f','i','j'])] * 1
) 
alpha_plus_lpn_5 = LabelledPetriNet(
        places=[
                Place("P_sink",pid="dbdd0237-8ad1-41e6-8304-b936ae99afd0"),
                Place("P_({'f'},{'e', 'i'})",pid="5e406806-d04f-4d26-92b4-c600bee51343"),
                Place("P_({'b', 'e'},{'c', 'f'})",pid="2291bfce-d341-4fa8-bb14-a88d09a95a5c"),      
                Place("P_({'h'},{'j'})",pid="af98d503-9569-4022-8009-3096c1e68829"),
                Place("P_({'a', 'c'},{'b'})",pid="8f801b01-51a2-4070-9aef-f5eb657a40b0"),
                Place("P_({'a'},{'d'})",pid="a557921f-68f9-4f14-9a54-08b2168b75bb"),
                Place("P_({'d'},{'h'})",pid="4302656f-be39-4eb7-8796-36a990f6edf8"),
                Place("P_({'i'},{'j'})",pid="549d1720-266c-488e-abce-b4d3b295ad51"),
                Place("P_initial",pid="233785f2-d1f7-4ca5-98b9-ec763b64e15d"),
        ],
        transitions=[
                Transition("a",tid="beac9b42-59a7-4ff6-8108-dce47d036881",weight=1.0,silent=False), 
                Transition("c",tid="631534d2-7226-47ed-a9be-d753b22a1981",weight=1.0,silent=False), 
                Transition("b",tid="a91aa8e9-1ade-4186-9a21-226b0d69b2c6",weight=1.0,silent=False), 
                Transition("j",tid="b15fa8ea-71a9-4a27-8253-2717d2bf3fa9",weight=1.0,silent=False), 
                Transition("d",tid="2821344a-cd9e-4ca9-a858-3642b8b34607",weight=1.0,silent=False), 
                Transition("h",tid="267669ee-59a7-4857-8b02-0427a6c166b6",weight=1.0,silent=False), 
                Transition("z",tid="ef2278f3-c3ea-4430-b339-555d9b96767c",weight=1.0,silent=False), 
                Transition("i",tid="8b1a4029-1c1b-4f6b-9c0e-bee77c5fe141",weight=1.0,silent=False), 
                Transition("f",tid="91a41ea3-9f17-49d7-8133-6d87cbc9a644",weight=1.0,silent=False), 
                Transition("e",tid="46067b76-4630-4594-bf26-3c19ac2df923",weight=1.0,silent=False), 
        ],
        arcs=[
                Arc(from_node=Transition("a",tid="beac9b42-59a7-4ff6-8108-dce47d036881",weight=1.0,silent=False),to_node=Place("P_({'a'},{'d'})",pid="a557921f-68f9-4f14-9a54-08b2168b75bb")),
                Arc(from_node=Place("P_({'d'},{'h'})",pid="4302656f-be39-4eb7-8796-36a990f6edf8"),to_node=Transition("z",tid="ef2278f3-c3ea-4430-b339-555d9b96767c",weight=1.0,silent=False)),
                Arc(from_node=Transition("j",tid="b15fa8ea-71a9-4a27-8253-2717d2bf3fa9",weight=1.0,silent=False),to_node=Place("P_sink",pid="dbdd0237-8ad1-41e6-8304-b936ae99afd0")),
                Arc(from_node=Place("P_({'a'},{'d'})",pid="a557921f-68f9-4f14-9a54-08b2168b75bb"),to_node=Transition("d",tid="2821344a-cd9e-4ca9-a858-3642b8b34607",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'i'},{'j'})",pid="549d1720-266c-488e-abce-b4d3b295ad51"),to_node=Transition("j",tid="b15fa8ea-71a9-4a27-8253-2717d2bf3fa9",weight=1.0,silent=False)),
                Arc(from_node=Transition("i",tid="8b1a4029-1c1b-4f6b-9c0e-bee77c5fe141",weight=1.0,silent=False),to_node=Place("P_({'i'},{'j'})",pid="549d1720-266c-488e-abce-b4d3b295ad51")),
                Arc(from_node=Place("P_({'f'},{'e', 'i'})",pid="5e406806-d04f-4d26-92b4-c600bee51343"),to_node=Transition("e",tid="46067b76-4630-4594-bf26-3c19ac2df923",weight=1.0,silent=False)),     
                Arc(from_node=Transition("e",tid="46067b76-4630-4594-bf26-3c19ac2df923",weight=1.0,silent=False),to_node=Place("P_({'b', 'e'},{'c', 'f'})",pid="2291bfce-d341-4fa8-bb14-a88d09a95a5c")),
                Arc(from_node=Transition("z",tid="ef2278f3-c3ea-4430-b339-555d9b96767c",weight=1.0,silent=False),to_node=Place("P_({'d'},{'h'})",pid="4302656f-be39-4eb7-8796-36a990f6edf8")),
                Arc(from_node=Place("P_initial",pid="233785f2-d1f7-4ca5-98b9-ec763b64e15d"),to_node=Transition("a",tid="beac9b42-59a7-4ff6-8108-dce47d036881",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'h'},{'j'})",pid="af98d503-9569-4022-8009-3096c1e68829"),to_node=Transition("j",tid="b15fa8ea-71a9-4a27-8253-2717d2bf3fa9",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'d'},{'h'})",pid="4302656f-be39-4eb7-8796-36a990f6edf8"),to_node=Transition("h",tid="267669ee-59a7-4857-8b02-0427a6c166b6",weight=1.0,silent=False)),
                Arc(from_node=Transition("f",tid="91a41ea3-9f17-49d7-8133-6d87cbc9a644",weight=1.0,silent=False),to_node=Place("P_({'f'},{'e', 'i'})",pid="5e406806-d04f-4d26-92b4-c600bee51343")),     
                Arc(from_node=Place("P_({'a', 'c'},{'b'})",pid="8f801b01-51a2-4070-9aef-f5eb657a40b0"),to_node=Transition("b",tid="a91aa8e9-1ade-4186-9a21-226b0d69b2c6",weight=1.0,silent=False)),     
                Arc(from_node=Transition("b",tid="a91aa8e9-1ade-4186-9a21-226b0d69b2c6",weight=1.0,silent=False),to_node=Place("P_({'b', 'e'},{'c', 'f'})",pid="2291bfce-d341-4fa8-bb14-a88d09a95a5c")),
                Arc(from_node=Place("P_({'b', 'e'},{'c', 'f'})",pid="2291bfce-d341-4fa8-bb14-a88d09a95a5c"),to_node=Transition("c",tid="631534d2-7226-47ed-a9be-d753b22a1981",weight=1.0,silent=False)),
                Arc(from_node=Place("P_({'f'},{'e', 'i'})",pid="5e406806-d04f-4d26-92b4-c600bee51343"),to_node=Transition("i",tid="8b1a4029-1c1b-4f6b-9c0e-bee77c5fe141",weight=1.0,silent=False)),     
                Arc(from_node=Transition("a",tid="beac9b42-59a7-4ff6-8108-dce47d036881",weight=1.0,silent=False),to_node=Place("P_({'a', 'c'},{'b'})",pid="8f801b01-51a2-4070-9aef-f5eb657a40b0")),     
                Arc(from_node=Transition("c",tid="631534d2-7226-47ed-a9be-d753b22a1981",weight=1.0,silent=False),to_node=Place("P_({'a', 'c'},{'b'})",pid="8f801b01-51a2-4070-9aef-f5eb657a40b0")),     
                Arc(from_node=Transition("d",tid="2821344a-cd9e-4ca9-a858-3642b8b34607",weight=1.0,silent=False),to_node=Place("P_({'d'},{'h'})",pid="4302656f-be39-4eb7-8796-36a990f6edf8")),
                Arc(from_node=Place("P_({'b', 'e'},{'c', 'f'})",pid="2291bfce-d341-4fa8-bb14-a88d09a95a5c"),to_node=Transition("f",tid="91a41ea3-9f17-49d7-8133-6d87cbc9a644",weight=1.0,silent=False)),
                Arc(from_node=Transition("h",tid="267669ee-59a7-4857-8b02-0427a6c166b6",weight=1.0,silent=False),to_node=Place("P_({'h'},{'j'})",pid="af98d503-9569-4022-8009-3096c1e68829")),
        ],
        name='Petri net'
)

class SingleThreadAlphaPlusTest(unittest.TestCase):
    """
    The alpha-plus miner is equivalent to the alpla miner when given an 
    event log without one-length or two-length loops.
    """

    def weakly_compare(self, disc:LabelledPetriNet, expect:LabelledPetriNet):
        # weakly test that two nets are equivalent
        for p in disc.places:
            found_match = False
            for o in expect.places:
                if p.name == o.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Place ({p}) not found in expected places :\n{expect.places}")
        for t in disc.transitions:
            found_match = False
            for o in expect.transitions:
                if t.name == t.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Transition ({t}) not found in expected transitions :\n{expect.transitions}")
        for a in disc.arcs:
            found_match = False
            for o in expect.arcs:
                if o.from_node.name == a.from_node.name and o.to_node.name == a.to_node.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Arc ({a}) not found in expected arcs :\n{expect.arcs}")

    def setUp(self):
        self.miner = AlphaMinerPlusInstance()

    def test_creation(self):
        miner = AlphaMinerPlusInstance(min_inst=5)
        miner = AlphaMinerPlusInstance()
        miner = deepcopy(miner)

    def test_footprint_matrix(self):
        miner = self.miner
        matrix = miner.mine_footprint_matrix(LOG)
        # test that footprint matrix has the right follows
        # test that footprint matrix has the right relations
        for col in ACTS:
            for row in ACTS:
                crelation = matrix[col][row]
                rrelation = MATRIX[col][row]
                # test one
                self.assertEqual(crelation._follows, 
                    rrelation._follows,
                    "computed and expected follows differ :: "+
                    f"{crelation._follows} vs {rrelation._follows}"
                )
                # test two
                self.assertEqual(crelation.relation(), 
                    rrelation.relation(),
                    "computed and expected alpha relation differ :: "+
                    f"{crelation} vs {rrelation}"
                )

    def test_mine(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        net = miner.discover(BOOK_LOG)
        for p in net.places:
            found_match = False
            for o in BOOK_LPN_PL:
                if p.name == o.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Place ({p}) not found in expected places :\n{BOOK_LPN_PL}")
        for t in net.transitions:
            found_match = False
            for o in BOOK_LPN_TL:
                if t.name == t.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Transition ({t}) not found in expected transitions :\n{BOOK_LPN_TL}")
        for a in net.arcs:
            found_match = False
            for o in BOOK_LPN_FL:
                if o.from_node.name == a.from_node.name and o.to_node.name == a.to_node.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Arc ({a}) not found in expected arcs :\n{BOOK_LPN_FL}")


    def test_paper_example_1(self):
        miner = self.miner
        # following figure 2, the alpha+ miner should return the original
        # Petri net
        net = miner.discover(alpha_plus_log_1)
        # weakly test that two nets are equivalent
        self.weakly_compare(net, alpha_plus_lpn_1)

    def test_paper_example_2(self):
        miner = self.miner
        # following figure 5, the alpha+ miner should return the original
        # Petri net
        net = miner.discover(alpha_plus_log_2)
        # weakly test that two nets are equivalent
        self.weakly_compare(net, alpha_plus_lpn_2)

    def test_paper_example_3(self):
        miner = self.miner
        # following figure 5, the alpha+ miner should return the original
        # Petri net
        net = miner.discover(alpha_plus_log_3)
        # weakly test that two nets are equivalent
        self.weakly_compare(net, alpha_plus_lpn_3)

    def test_paper_example_4(self):
        miner = self.miner
        # following figure 5, the alpha+ miner should return the original
        # Petri net
        net = miner.discover(alpha_plus_log_4)
        # weakly test that two nets are equivalent
        self.weakly_compare(net, alpha_plus_lpn_4)

    def test_paper_example_5(self):
        miner = self.miner
        # following figure 5, the alpha+ miner should return the original
        # Petri net
        net = miner.discover(alpha_plus_log_5)
        # weakly test that two nets are equivalent
        self.weakly_compare(net, alpha_plus_lpn_5)

class OptimisedAlphaPlusTest(SingleThreadAlphaPlusTest):
    """
    Reuse the tests from SingleThreadAlphaTest to test that the optimised
    version returns the same results.
    """

    def setUp(self):
        from pmkoalas._logging import setLevel
        from logging import INFO
        self.miner = AlphaMinerPlusInstance(optimised=True)

    def tearDown(self) -> None:
        from pmkoalas._logging import setLevel
        from logging import ERROR
        setLevel(ERROR)
