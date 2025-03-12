import unittest

from pmkoalas.enhancement.decision_mining import mine_guards_for_lpn
from pmkoalas.enhancement.decision_mining import _earnst_expansion
from pmkoalas.enhancement.decision_mining import _shortcut_expansion
from pmkoalas.enhancement.decision_mining import _duplicate_expansion
from pmkoalas.models.petrinet import parse_pnml_into_lpn
from pmkoalas.models.petrinet import parse_pnml_for_dpn
from pmkoalas.models.petrinet import export_net_to_pnml
from pmkoalas.models.petrinet import Transition, Place
from pmkoalas.conformance.alignments import find_alignments_for_variants
from pmkoalas.conformance.alignments import Alignment, AlignmentMove
from pmkoalas.conformance.alignments import AlignmentMoveType
from pmkoalas.conformance.tokenreplay import PetriNetMarking
from pmkoalas.read import read_xes_complex 
from pmkoalas._logging import setLevel

from os.path import join
from os import environ
from logging import INFO, ERROR

EXAMPLES_DIR = join("tests","enhancement", "examples")
RF_PNML_FILE = join(EXAMPLES_DIR, "road_fines_normative_model.pnml")
RF_LOG_FILE = join(EXAMPLES_DIR, "roadfines_big_sampled.xes")
PROBLEM_NET = join(EXAMPLES_DIR, "disc_norm_postset.pnml")

SKIP_SLOW = eval(environ['SKIP_SLOW_TESTS'])

# TODO: need more tests that focus on checking all the rules of the 
# expansion strategies. Solving problems seems to be very stable, but 
# getting to that point has been prone to errors.

problem_net = parse_pnml_for_dpn(PROBLEM_NET)

problem_prone_aligment = Alignment([AlignmentMove( AlignmentMoveType.SYNC,Transition("Create Fine",tid="67c838fc-01c6-4cba-9475-3194c0d3b538",weight=1.0,silent=False), 'Create Fine',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 1, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 0, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Send Fine",tid="6a92c9bd-94ee-4dad-8f3e-605caa9c7c91",weight=1.0,silent=False), 'Send Fine',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 0, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 1, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Insert Fine Notification",tid="ab982947-6238-41f6-86a5-7f3ade92c661",weight=1.0,silent=False), 'Insert Fine Notification',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 1, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 0, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Appeal to Judge",tid="fff25743-af71-4ae4-9a12-25302f605426",weight=1.0,silent=False), 'Appeal to Judge',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.LOG,None, 'Add penalty',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 1, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 0, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.MODEL,Transition("tau5",tid="5326cf59-54a8-4e82-bba1-300db8dc21ee",weight=1.0,silent=True), None,PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 1, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 0, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.SYNC,Transition("Payment",tid="10d06484-e60d-46b5-b14f-8d98c9755c3d",weight=1.0,silent=False), 'Payment',PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None),
 AlignmentMove( AlignmentMoveType.MODEL,Transition("tau3",tid="c6cbfa46-cde1-4db6-ac75-a44a2b295ede",weight=1.0,silent=True), None,PetriNetMarking(problem_net, eval('{Place("I",pid="b9248d18-bca3-4f14-80f2-466bfed178f0"): 0, Place("p7",pid="5db71268-b50f-4f3e-bdaf-79bb8ab171c6"): 0, Place("p4",pid="a2abf799-f419-4b05-b457-1afa00226adc"): 0, Place("p2",pid="041fc672-d29b-484c-ab8c-ac2f3aeca955"): 0, Place("p3",pid="d25b0ab6-0b93-469a-b0bc-a1673979e1da"): 1, Place("p6",pid="03e8f59c-a8af-4035-b09f-d90776bb6b52"): 0, Place("p1",pid="2dc260ee-67ab-4ccc-ab23-7a98fbfb8ba7"): 0, Place("F",pid="0dbb8766-ab49-48da-8c7f-78c85a430293"): 0, Place("p5",pid="a0e43fe3-7a0f-4636-8711-2612458c8ca8"): 0}')),None)
 ])

class DecisionMiningTest(unittest.TestCase):

    def setUp(self):
        self.log = read_xes_complex(RF_LOG_FILE)
        self.lpn = parse_pnml_into_lpn(RF_PNML_FILE)
        if (not False):
            self.ali = find_alignments_for_variants(self.log, self.lpn, 'pm4py')

    @unittest.skipIf(False, "testing can take up to 90s")
    def test_postset_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="postset",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "postset_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="postset", 
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "postset_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log,
            alignment=self.ali,
            identification="postset", 
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "postset_duplicate.pnml",
            include_prom_bits=True)
    
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_marking_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "marking_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "marking_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "marking_duplicate.pnml",
            include_prom_bits=True)
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_regions_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "regions_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "regions_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "regions_duplicate.pnml",
            include_prom_bits=True)
        
    def test_earnst_expansion(self):
        expanded = _earnst_expansion(problem_net, problem_prone_aligment)

    def test_shortcut_expansion(self): 
        expanded = _shortcut_expansion(problem_net)

    def test_duplciate_expansion(self):
        expanded = _duplicate_expansion(problem_net)
    
    def tearDown(self):
        del self.log 
        del self.lpn
        setLevel(ERROR)