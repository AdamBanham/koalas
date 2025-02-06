'''
This module contains helper classes that find competition within a Petri net.
These helpers are designed to enable decision mining in a straightfoward way.

To find collection of classification problems, use the function 
`find_classification_problems`
'''

from pmkoalas.models.petrinet import LabelledPetriNet
from pmkoalas.models.petrinet import Transition
from pmkoalas.models.petrinet import PetriNetMarking
from pmkoalas.models.guards import Guard
from pmkoalas._logging import debug

from typing import Set, Literal, Mapping, List
from copy import deepcopy
from abc import abstractmethod

OneHotEncTag = "oneHotEnc"

class ClassficiationProblemExample:
    """
    Helper class to reprsent an example for a classification problem, useful
    for decision mining.
    """

    def __init__(self, target:Transition, data:Mapping[str,object]) -> None:
        self._target = deepcopy(target)
        self._data = deepcopy(data)

    @property
    def target(self) -> Transition:
        return deepcopy(self._target)
    
    @property
    def data(self) -> Mapping[str,object]:
        return deepcopy(self._data)

class ClassificationProblem:
    """
    Helper class to represent a classification problem, can be used to 
    identify if the problem represents in an replayed execution over the 
    original net.
    """

    def __init__(self, targets:Set[Transition], 
                 sources:Set[PetriNetMarking],
                 exact_match:bool=False,
                 examples:List[ClassficiationProblemExample]=None) -> None:
        self._targets = deepcopy(targets)
        self._sources = deepcopy(sources)
        self._exact_match = exact_match
        self._seen_vars = set()
        self._seen_tars = dict(
            (t.name,0)
            for t in self._targets
        )
        if (examples is None):
            self._examples = list()
        else:
            self._examples = deepcopy(examples)

    def reached(self, marking:PetriNetMarking) -> bool:
        """
        Determines if the marking has reached the target transitions.
        """
        if (self._exact_match):
            for pos in self.sources:
                if pos == marking:
                    return True 
        else:
            for pos in self.sources:
                if pos.is_subset(marking):
                    return True
        return False
    
    def add_example(self, target:Transition, data:Mapping[str,object]) -> None:
        if target not in self._targets:
            raise ValueError(f"Target {repr(target)} not in the set of "\
                             +f"targets ({self._targets})")
        self._seen_vars = self._seen_vars.union(set(data.keys()))
        self._seen_tars[target.name] += 1
        self._examples.append(ClassficiationProblemExample(target, data))

    def _rule_reduction(self, rules:List[List[str]]) -> str:
        """
        Reduces a set of rules to a single rule.
        """
        debug(f"calling red with :: {rules}")
        options = set( rule[0] for rule in rules )
        debug(f"selecting options from :: {options}")
        if  len(options) == 1:
            a = options.pop()
            reduce = [ list( a for a in rule[1:]) for rule in rules ]
            reduce = [ r for r in reduce if len(r) > 0 ]
            if len(reduce) > 0:
                ret = f"({a}&&"
                red = self._rule_reduction(reduce)
                ret += f"{red}"
                ret += ")"
            else:
                ret = f"({a})"
            debug(f"returning case a :: {ret} from options :: {options} "\
                  +f"based on {rules}")
            return ret
        elif len(options) > 1:
            count = {
                a: sum( 1 for rule in rules if rule[0] == a )
                for a in options
            }
            debug(f"case b checking freqs :: {count}")
            ret = "("
            for a,count in count.items():
                if count == 1:
                    rule = [ rule for rule in rules if rule[0] == a ][0]
                    ret += f"{'&&'.join(rule)}||"
                else:
                    reduce = [ list( a for a in rule[1:]) 
                              for rule in rules if rule[0] == a ]
                    reduce = [ r for r in reduce if len(r) > 0 ]
                    if len(reduce) > 0:
                        ret += f"({a}&&"
                        red = self._rule_reduction(reduce)
                        ret += f"{red}"
                        ret += ")||"
                    else:
                        ret = f"{a}||"
            if ret.endswith("||"):
                ret = ret[:-2]
            ret += ")"
            debug(f"returning case b :: {ret} from options :: {options} "\
                  +"based on {rules}")
            return ret
        else:
            debug(f"returning case c :: found no options :: {rules}")
            return ""

    def _convert_cart_dnode(self, feature_name, op, threshold, 
        num_features, cat_features) -> str:
        """
        Handles converting back from one-hot encoding to easier to read
        guards.
        """
        
        if feature_name in num_features:
            return f"({feature_name} {op} {threshold:.3f})"
        elif feature_name in cat_features:
            literal = feature_name.split("_")[-1]
            feature = "_".join(feature_name.split("_")[1:-1])
            if op == "<=":
                # return a not equal to feature value
                return f"({feature} != \"{literal}\")" 
            else:
                # return a equal to feature value
                pass
                return f"({feature} == \"{literal}\")"
        else:
            return f"({feature_name} {op} {threshold:.3f})"

    def solve(self) -> None:
        """
        Solves the classification problem, by finding a decision tree.
        """
        from importlib.util import find_spec
        
        if find_spec("sklearn"):
            import numpy as np
            import pandas as pd
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.preprocessing import OneHotEncoder
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import Pipeline
            from sklearn.compose import ColumnTransformer
            from sklearn.tree import plot_tree, export_graphviz
            from matplotlib import pyplot as plt
            # work out tpying for cols, e.g. cat or numeric
            col_types = dict()
            for e in self._examples:
                for k,v in e.data.items():
                    if k not in col_types.keys():
                        col_types[k] = set()
                    col_types[k].add(type(v))
                    if len(col_types[k]) > 1:
                        raise ValueError(
                            f"Cannot solve mixed type columns ::" \
                            +f" {col_types[k]}"
                        )
            temp = dict()
            for k,v in col_types.items():
                temp[k] = v.pop()
            col_types = temp
            cat_cols = list( k for k,v in col_types.items() if v == str )
            # create dataset in pandas for target and columns
            cols = sorted(list(self._seen_vars))
            num_cols = [ c for c in cols if c not in cat_cols ]
            X = [ [ e.data[c] if c in e.data.keys() else np.nan for c in cols] 
                 for e in self._examples ]
            X = pd.DataFrame(X, columns=cols)
            targets = sorted(list( t.name for t in self._targets))
            targets = dict( (t,i) for i,t in enumerate(targets) )
            Y = [ targets[e.target.name] for e in self._examples ]
            # create a pipeline for the decision tree
            tree = DecisionTreeClassifier(
                max_depth=15,
                min_samples_split=max(int(len(self._examples)*0.05), 20),
                min_samples_leaf=max(int(len(self._examples)*0.025), 1),
                ccp_alpha=0.01,
                # class_weight="balanced"
            )
            cat_imputer = SimpleImputer(strategy="constant", 
                                        fill_value="unset",copy=False)
            num_imputer = SimpleImputer(strategy="constant", 
                                        fill_value=-99,copy=False)
            X[num_cols] = num_imputer.fit_transform(X[num_cols])
            cat_transformers = Pipeline(steps=[
                ('impute', cat_imputer),
                ('encode', OneHotEncoder(handle_unknown='ignore',
                                         feature_name_combiner=
                                         lambda f,c: OneHotEncTag+"_"+f+"_"+c)
                )
            ])    
            num_transformers = Pipeline(steps=[
                ("impute", num_imputer)  
            ])
            ctransform = ColumnTransformer([
                ('categorical', cat_transformers, cat_cols),
                ('numeric', num_transformers, num_cols)
                ],
                remainder='passthrough',
                verbose_feature_names_out=False)
            pipe = Pipeline(steps=
                [('preprocessor', ctransform), 
                 ('classifier', tree)])
            # fit the model
            pipe.fit(X,Y)
            dot_data = export_graphviz(tree, out_file=None, 
                     feature_names=ctransform.get_feature_names_out(),  
                     class_names=sorted(list( t.name for t in self._targets)),  
                     filled=True, rounded=True,  
                     special_characters=True)  
            debug("discovered decision tree:: "+dot_data)
            # input("Press enter to continue")
            # attempt to construct guards from paths for all targets
            guards = dict()
            feature_names = ctransform.get_feature_names_out()
            cat_cols = set([ 
                f for f in feature_names
                if f.startswith(OneHotEncTag+"_")
            ])
            num_cols = set([
                f for f in feature_names
                if f not in cat_cols
            ])
            class_names = sorted(list( t.name for t in self._targets))
            # decision tree data
            n_nodes = tree.tree_.node_count
            children_left = tree.tree_.children_left
            children_right = tree.tree_.children_right
            feature = tree.tree_.feature
            threshold = tree.tree_.threshold
            values = tree.tree_.value
            stack = [([],0)]
            completed = []
            # traverse the tree
            ## see: https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html
            def is_leaf_node(node_id):
                return children_left[node_id] == children_right[node_id]
            while len(stack) > 0:
                hist, node_id = stack.pop(0)
                # If the left and right child of a node is not the same we have a split
                # node
                is_split_node = not is_leaf_node(node_id)
                left = children_left[node_id]
                right = children_right[node_id]
                if is_split_node and is_leaf_node(left) and is_leaf_node(right):
                    lclass = class_names[np.argmax(values[left][0])]
                    rclass = class_names[np.argmax(values[right][0])]
                    if lclass == rclass:
                        debug("both children are leaf nodes with the same class")
                        completed.append(hist+[("F",node_id)])
                        continue
                # check to see if both children are leaf nodes 
                # If a split node, append left and right children and depth 
                # to `stack` so we can loop through them
                if is_split_node:
                    stack.append(
                        (deepcopy(hist)+[("L",node_id)],
                         children_left[node_id]))
                    stack.append(
                        (deepcopy(hist)+[("R",node_id)],
                         children_right[node_id]))
                else:
                    completed.append(hist+[("F",node_id)])
            # for each path, construct the guard
            for path in completed:
                debug(path)
                if len(path) == 0:
                    continue
                elif len(path) == 1:
                    continue
                else:
                    leaf_class = class_names[np.argmax(values[path[-1][1]][0])]
                # find the guard
                guard = list()
                for (dir,node_id) in path[:-1]:
                    if dir == "L":
                        converted_dnode = self._convert_cart_dnode(
                            feature_names[feature[node_id]],
                            "<=", threshold[node_id], 
                            num_cols, cat_cols)
                        debug(f"converted left node :: {converted_dnode}")
                        guard.append( 
                            converted_dnode
                        )
                    else:
                        converted_dnode = self._convert_cart_dnode(
                            feature_names[feature[node_id]],
                            ">", threshold[node_id], 
                            num_cols, cat_cols)
                        debug(f"converted right node :: {converted_dnode}")
                        guard.append( 
                            converted_dnode
                        )
                if leaf_class not in guards.keys():
                    guards[leaf_class] = list()
                guards[leaf_class].append("&&".join(guard))
            ret_guards = dict()
            for tar in self._targets:
                debug(f"Guards for {tar.name} ::")
                if tar.name in guards.keys():
                    if len(guards[tar.name]) >= 1:
                        ret_gaurd = ""
                        for g in guards[tar.name]:
                            debug(f"\t{g}")
                            ret_gaurd += f"({g})||"
                        ret_guards[tar] = Guard(ret_gaurd[:-2])
                    else:
                        ret_guards[tar] = Guard("true")
                else:
                    ret_guards[tar] = Guard("true")
                try:
                    red = self._rule_reduction([ 
                        r.split("&&") for r in guards[tar.name] 
                    ])
                    assert len(list(l for l in red if l == "(")) == \
                           len(list(l for l in red if l == ")"))
                    debug(f"reduction completed for '{tar.name}'::")
                    debug(red)
                    g = Guard(red)
                    ret_guards[tar] = g
                    debug(f"where the reduced guard (pmkoalas) is ::\n\t{g}")
                except Exception as e:
                    debug(f"Failed to reduce :: {str(e)}")
                # input("Press enter to continue")
            return ret_guards, col_types
        else:
            raise ImportError("sklearn (~1.5) is required to solve " \
                              +"classification problems")

    def describe(self) -> str:
        """
        Describes the breakdown of examples for this classification problem.
        """
        ret = "Problem ::\n"
        ret += "\tObserved variables:: " + str(self._seen_vars) + "\n"
        ret += "\tClasses:: \n"
        for tar in self._targets:
            ret += f"\t\t{tar.name} :: {self._seen_tars[tar.name]}\n"
        return ret

    @property
    def examples(self) -> Set[ClassficiationProblemExample]:
        return deepcopy(self._examples)
    
    @property
    def targets(self) -> Set[Transition]:
        return deepcopy(self._targets)
    
    @property
    def sources(self) -> Set[PetriNetMarking]:
        return deepcopy(self._sources)
    
    def __str__(self) -> str:
        return "Problem awaits " \
            +f"{'exactly' if self._exact_match else 'at least'} "\
            +f"for  {set( str(s) for s in self.sources )}"\
            +" such that the following fires "\
            +f"{set( t.name for t in self.targets )}"
    
    def __repr__(self) -> str:
        ret = "ClassificationProblem("

        ret +=")"
        return ret

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ClassificationProblem):
            return False
        return self.targets == value.targets and self.sources == value.sources
    
    def __hash__(self) -> int:
        return hash((frozenset(self.targets), frozenset(self.sources)))

class ClassificationProblemSolver:
    """
    Interface for a technique to solve a classification problem.
    """

    def __init__(self,balance_target_classes:bool=True) -> None:
        self._balance_target_classes = balance_target_classes

    @abstractmethod
    def solve(self, problem:ClassificationProblem) -> Mapping[Transition,Guard]:
        """
        Solves a classification problem, returning a mapping of transitions to
        guards.
        """
        pass

class BigTreeSolver(ClassificationProblemSolver):
    """
    Implementation of a classification problem solver that uses a single 
    decision tree for each problem, regardless of the number of targets.
    """

    def __init__(self, balance_target_classes: bool = True) -> None:
        super().__init__(balance_target_classes)

    def solve(self, problem: ClassificationProblem) -> Mapping[Transition, Guard]:
        ret = dict()
        return ret


class OneVsAllSolver(ClassificationProblemSolver):
    """
    Implementation of a classification problem solver that uses a one vs all
    approach to construct decision trees for each problem, if the number
    of targets is greater than two. Otherwise the BigTreeSolver is used.
    """

    def __init__(self, balance_target_classes: bool = True) -> None:
        super().__init__(balance_target_classes)

    def solve(self, problem: ClassificationProblem) -> Mapping[Transition, Guard]:
        ret = dict()
        return ret

class CompetitionIdentifier:
    """
    Interface for a technique to identify competition within a Petri net.
    """

    @abstractmethod
    def identify(self, lpn:LabelledPetriNet) -> Set[ClassificationProblem]:
        """
        For a given labelled Petri net, find the classification problems to 
        represent where competition exists within the firing of the net.
        
        Returns a possibly empty set of classification problems.
        """
        pass
            

class PostsetCompetitionIdentifier(CompetitionIdentifier):
    """
    Implementation of a competition identifier to find competition within the 
    postset of places.
    """
    
    def identify(self, lpn:LabelledPetriNet) -> Set[ClassificationProblem]:
        ret = set()
        for place in lpn.places:
            postset = [ a for a in lpn.arcs if a.from_node == place ]
            if (len(postset)> 1):
                ret.add(ClassificationProblem(
                    set([a.to_node for a in postset]),
                    set([PetriNetMarking(lpn,{place:1})])
                ))
        return ret

class MarkingCompetitionIdentifier(CompetitionIdentifier):
    """
    Implementation of a competition identifier to find competition within the 
    markings of a Petri net.
    """
    
    def identify(self, lpn:LabelledPetriNet) -> Set[ClassificationProblem]:
        ret = set()
        from pmkoalas.models.transitionsystem import generate_marking_system
        ts = generate_marking_system(lpn)
        for state in ts.states:
            mark:PetriNetMarking = state.src
            firable = mark.can_fire()
            if (len(firable) > 1):
                ret.add(ClassificationProblem(
                    firable,
                    set([mark]),
                    True
                ))
        return ret

class RegionCompetitionIdentifier(CompetitionIdentifier):    
    """
    Implementation of a competition identifier to find competition within the 
    regions of the marking system for a Petri net.
    """
    def identify(self, lpn:LabelledPetriNet) -> Set[ClassificationProblem]:
        ret = set()
        from pmkoalas.models.transitionsystem import generate_marking_system
        from pmkoalas.models.transitionsystem import find_regions
        ts = generate_marking_system(lpn,use_trans_id=True)
        regions = find_regions(ts.initial_states().pop(), ts)
        for reg in regions:
            tids = [ 
                edge.event.name
                for edge in ts.transitions
                if edge.source in reg.states 
            ]
            if (len(tids) > 1):
                ret.add(ClassificationProblem(
                    set( t for t in lpn.transitions if t.tid in tids ),
                    set(s.src for s  in reg.states),
                    True
                ))
        return ret
    
class SingleBagCompetitionIdentifier(CompetitionIdentifier):
    """
    Implementation of a competition identifier to find cometeition within the
    traversed states of a Petri net in a single problem.
    """

    def identify(self, lpn: LabelledPetriNet) -> Set[ClassificationProblem]:
        ret = set()
        ret.add(
            ClassificationProblem(
                set(lpn.transitions),
                set([PetriNetMarking(lpn,{place:1}) for place in lpn.places])
            )
        )
        return ret 

CLASSIFICATION_STRATEGIES = Literal["single-bag","postset","marking","regions"]

def find_classification_problems(lpn:LabelledPetriNet, 
    type:Literal["single-bag","postset","marking","regions"]="postset") \
    -> Set[ClassificationProblem]:
    """
    For a given labelled Petri net, find the classification problems to 
    represent where competition exists within the firing of the net.
    
    Returns a possibly empty set of classification problems.
    """
    if type == "postset":
        return PostsetCompetitionIdentifier().identify(lpn)
    elif type == "marking":
        return MarkingCompetitionIdentifier().identify(lpn)
    elif type == "regions":
        return RegionCompetitionIdentifier().identify(lpn)
    elif type == "single-bag":
        return SingleBagCompetitionIdentifier().identify(lpn)
    else:
        raise ValueError("Invalid type of competition identifier")