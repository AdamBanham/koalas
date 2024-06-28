'''
Allows the creation of Petri nets with short one line ASCII sketches, for 
example:
initialPlace -> [transition1] -> mp -> [transition2] -> finalPlace

Larger nets can be created with multiple invocations. Existing nodes will be 
looked up by label. 

Weighted transitions without weights, as in {b}, are defaulted to weight 1.0.

Nodes with duplicate labels can be specified using a [tranLabel__id] syntax. 

Example uses::
    net1 = pnfrag.create_net()
    net2 = pnfrag.parse_net_fragments("tester_net",
                "I -> [A] -> p1 -> [tau] -> F",
                "I -> [A] -> p1 -> [B] -> p2 -> [E] -> p3 -> [G] -> F",
                "I -> [A] -> p1 -> [C] -> p2 -> [E] -> p3 -> [H] -> F",
                "I -> [A] -> p1 -> [D] -> p2 -> [E] -> p3 -> [K] -> F")
    parser = pnfrag.PetriNetFragmentParser()
    net3 = parser.create_net()
    parser.add_to_net(net3, "I -> {a__1 3.0} -> F")
 

Weighted transitions, allowing support of Stochastic Labelled Petri Nets. 

Current limitations: No time distributions or weighted arcs.

 
Grammar

PETRI_ONELINE_NET 	:: PLACE EDGE TRANSITION EDGE PLACE_LED_SUBNET
PLACE_LED_SUBNET  	:: PLACE EDGE TRANSITION EDGE PLACE_LED_SUBNET
PLACE_LED_SUBNET  	:: PLACE 
TRANSITION_SUBNET 	:: TRANSITION EDGE PLACE EDGE TRANSITION_SUBNET
TRANSITION_SUBNET 	:: TRANSITION 
TRANSITION        	:: SIMPLE_TRANSITION || WEIGHTED_TRANSITION
SIMPLE_TRANSITION 	:: TRAN_START TRAN_LABEL TRAN_END
WEIGHTED_TRANSITION     :: WEIGHTED_TRAN_VALUE | WEIGHTED_TRAN_DEFAULT
WEIGHTED_TRAN_VALUE     :: '{' TRAN_LABEL WEIGHT '}'
WEIGHTED_TRAN_DEFAULT   :: '{' TRAN_LABEL '}'
TRAN_LABEL		:: TLABEL || T_ID_LABEL
T_ID_LABEL		:: TLABEL ID_PREFIX ID
TLABEL			:: LABEL || SILENT_LABEL || LABEL TLABEL
PLACE             	:: LABEL || P_ID_LABEL
P_ID_LABEL              :: LABEL ID_PREFIX ID
EDGE              	:: '->'
SIMPLE_TRAN_START	:: '['
SIMPLE_TRAN_END		:: ']' 
ID_PREFIX		:: '__'
WEIGHT		 	:: NUM_STR
ID             		:: NUM_STR
NUM_STR			:: numeric string
SILENT_LABEL            :: 'tau'
LABEL             	:: alphanumeric string

This is adapted from PetriNetFragmentParser.java in the prom-helpers library.

See also: 
    - https://github.com/adamburkegh/prom-helpers
    - https://adamburkeware.net/2021/05/20/petri-net-fragments.html

'''

from enum import Enum
import re

from pmkoalas.models.petrinet import *
from logging  import debug


ID_LEXEME = '__'

class TokenInfo(Enum):
    SIMPLE_TRAN_START = "\\[",
    SIMPLE_TRAN_END = "\\]",
    WEIGHTED_TRAN_START = "\\{",
    WEIGHTED_TRAN_END = "\\}",
    ID_PREFIX = ID_LEXEME,
    EDGE = "->",
    SILENT_LABEL = "tau",
    LABEL = "[a-zA-Z][a-zA-Z0-9]*",
    WEIGHT = "[0-9]+\\.[0-9]+",
    ID = "[0-9]+",
    TERMINAL = ""

    def __init__(self,strp):
        self._strp = strp
        self._pattern = re.compile(strp)

    @property
    def pattern(self):
        return self._pattern

TOKEN_LEX_VALUES = [toki for toki in TokenInfo] 
TOKEN_LEX_VALUES.remove(TokenInfo.TERMINAL)


class Token:
    def __init__(self,token_info,token_str):
        self.token_info = token_info
        self.token_str = token_str

class ParseException(Exception):
    pass

def create_net(net_title, net_text) -> LabelledPetriNet:
    return PetriNetFragmentParser().create_net(net_title,net_text)

def parse_net_fragments(net_title:str, *fragments:str) -> LabelledPetriNet:
    """
    Given a set of fragments following the gammar mentioned below, this function
    returns a Petri net that contains all the fragments.

    See the module documentation for a full grammar.
    """
    parser = PetriNetFragmentParser()
    if (len(fragments) > 0):
        net = parser.create_net(net_title, fragments[0])
        for frag in fragments[1:]:
            parser.add_to_net(net, frag)
    return net


class PetriNetFragmentParser:
    def __init__(self):
        self.init()

    def init(self):
        self.tokens = []
        self.ctid = 0
        self.label_lookup = {}
        self.id_lookup = {}

    def create_net(self,net_title:str, net_text:str) -> BuildablePetriNet:
        net = BuildablePetriNet(label=net_title)
        self.init()
        self.add_to_net(net,net_text)
        return net

    def add_to_net(self, net:LabelledPetriNet, net_text: str):
        self.tokenize(net_text)
        self.net = net
        self.parse()

    def tokenize(self,tstr: str):
        self.tokens = []
        ctstr = tstr.strip()
        while (ctstr != ""):
            match = False
            ctstr = ctstr.strip()
            for tokinfo in TOKEN_LEX_VALUES:
                mo = tokinfo.pattern.match(ctstr)
                if mo:
                    match = True
                    tok = mo.group().strip()
                    debug( f'{tokinfo}::{tok}')
                    self.tokens.append( Token(tokinfo,tok) )
                    ctstr = ctstr.replace(mo.group(),"",1)
                    break
            if not match:
                raise ParseException("Unexpected character in input:\""  \
                                    + ctstr + "\"")

    def parse(self):
        self.lookahead = self.tokens[0]
        self.petri_one_line_net()
        if(self.lookahead.token_info != TokenInfo.TERMINAL):
            raise ParseException(f"Unexpected symbol {self.lookahead} found")

    def check_existing_node(self,label: str, node_type):
        if not label in self.label_lookup:
            return None
        n = self.label_lookup[label]
        if node_type != type(n):
            raise ParseException(f"New node {label} duplicates existing node of wrong type")
        return n

    def check_existing_node_by_id(self, nid, node_type):
        if not nid in self.id_lookup:
            return None
        n = self.id_lookup[nid]
        if node_type != type(n):
            raise ParseException(f"New node {nid} duplicates existing node of wrong type")
        return n

    def check_existing_place(self, label: str):
        return self.check_existing_node(label,Place)

    def check_existing_place_by_id(self,pid):
        return self.check_existing_node_by_id(pid,Place)

    def check_existing_transition(self,label: str):
        return self.check_existing_node(label,Transition)

    def check_existing_transition_by_id(self,tran_id):
        return self.check_existing_node_by_id(tran_id,Transition)

    def petri_one_line_net(self):
        p1 = self.place()
        self.edge()
        transition = self.transition()
        self.edge()
        p2 = self.place_led_subnet()
        self.readd_arc(p1, transition)
        self.readd_arc(transition, p2)

    def place(self):
        label = self.lookahead.token_str
        self.next_token()
        pid = None
        place = None
        if self.lookahead.token_info == TokenInfo.ID_PREFIX:
            self.next_token()
            pid = self.id()
            self.next_token()
        if pid:
            place = self.check_existing_place_by_id(pid)
        else:
            place = self.check_existing_place(label)
        if (place is None):
            if not pid:
                pid = self.next_id()
            place = Place(label,pid=pid)
            self.net.add_place(place)
            self.label_lookup[label] = place
        return place;

    def edge(self):
        if self.lookahead.token_info != TokenInfo.EDGE:
            self.token_error(TokenInfo.EDGE)
        self.next_token()

    def transition(self):
        transition = None
        if self.lookahead.token_info == TokenInfo.SIMPLE_TRAN_START: 
            transition = self.simple_transition()
        if self.lookahead.token_info == TokenInfo.WEIGHTED_TRAN_START: 
            transition = self.weighted_value_transition()
        self.next_token()
        return transition

    def simple_transition(self):
        transition = None
        self.next_token()
        label = ''
        tran_id = None
        silent_tran = False
        if self.lookahead.token_info == TokenInfo.LABEL:
            label = self.tran_label()
            self.next_token()
        else: 
            if self.lookahead.token_info == TokenInfo.SILENT_LABEL:
                label = self.tran_label()
                silent_tran = True
                self.next_token()
            else:
                raise ParseException(
                        f"Expected label, but found {self.lookahead.token_str}")
        if self.lookahead.token_info == TokenInfo.SIMPLE_TRAN_END:
            transition = self.check_existing_transition(label)
        else:
            if self.lookahead.token_info == TokenInfo.ID_PREFIX:
                transition = None
                self.next_token()
                tran_id = self.id()
                self.next_token()
                if self.lookahead.token_info != TokenInfo.SIMPLE_TRAN_END:
                    self.token_error(TokenInfo.SIMPLE_TRAN_END,
                                    TokenInfo.ID_PREFIX)
            else:
                self.token_error(TokenInfo.SIMPLE_TRAN_END,
                                TokenInfo.ID_PREFIX)
        if not tran_id is None:
            transition = self.check_existing_transition_by_id(tran_id)
        if not transition:
            if tran_id:
                transition = Transition(label,tid=tran_id,silent=silent_tran)
                self.id_lookup[tran_id] = transition
            else:
                transition = Transition(label,tid=self.next_id(),
                                        silent=silent_tran)
                self.label_lookup[label] = transition
            self.net.add_transition(transition)
        return transition

    def weighted_value_transition(self):
        transition = None
        self.next_token()
        label = ''
        tran_id = None
        silent_tran = False
        weight = 1.0
        if self.lookahead.token_info == TokenInfo.LABEL:
            label = self.tran_label()
            self.next_token()
        else:
            if self.lookahead.token_info == TokenInfo.SILENT_LABEL:
                label = self.tran_label()
                silent_tran = True
                self.next_token()
            else:
                raise ParseException(
                        f"Expected label, but found {self.lookahead.token_str}")

        if self.lookahead.token_info == TokenInfo.ID_PREFIX:
            transition = None
            self.next_token()
            tran_id = self.id()
            self.next_token()
        if self.lookahead.token_info == TokenInfo.WEIGHT:
            weight = self.weight()
            self.next_token()
        if self.lookahead.token_info == TokenInfo.WEIGHTED_TRAN_END:
            transition = self.check_existing_transition(label)
        else:
            self.token_error(TokenInfo.WEIGHTED_TRAN_END,
                            TokenInfo.ID_PREFIX)
        if not transition:
            if tran_id:
                transition = Transition(label,tid=tran_id,silent=silent_tran,
                                    weight=weight)
                self.id_lookup[tran_id] = transition
            else:
                transition = Transition(label,tid=self.next_id(),
                                         silent=silent_tran, weight=weight)
                self.label_lookup[label] = transition
            self.net.add_transition(transition)
        return transition


    def tran_label(self):
        label = self.lookahead.token_str
        while self.tokens[1].token_info == TokenInfo.LABEL:
                self.next_token() 
                label += " " + self.lookahead.token_str
        return label

    def place_led_subnet(self):
        head = self.place()
        if self.lookahead.token_info == TokenInfo.EDGE:
            self.edge()
            tran = self.transition()
            self.edge()
            tail = self.place_led_subnet()
            self.readd_arc(head,tran)
            self.readd_arc(tran,tail)
        return head

    def id(self):
        return int(self.lookahead.token_str)

    def weight(self):
        return float(self.lookahead.token_str)

    def token_error(self,*tokens):
        raise ParseException(
                f"Expected one of {tokens} but found {self.lookahead.token_str}")


    def next_token(self):
        self.tokens.pop(0)
        # at the end of input we return an epsilon token
        if not self.tokens:
            self.lookahead = Token(TokenInfo.TERMINAL, "")
        else:
            self.lookahead = self.tokens[0]

    def readd_arc(self,from_node,to_node):
        self.net.add_arc_between(from_node,to_node)

    def next_id(self):
        self.ctid += 1
        return self.ctid

