'''
This module contains typical useful restricts on collections in computer 
science.

Included are the following structures:
    - `Stack`
    - `OutOfMemoryQueue`
    - `OutOfMemorySet`
'''
from pmkoalas._logging import debug

from copy import deepcopy
from typing import Collection, Union
from tempfile import TemporaryDirectory
from os.path import join
from dill import dumps as pickle_dumps, loads as pickle_loads, load as pickle_load

class Stack():
    '''
    A structure to represent a stack, where you can push, peek, or pop 
    elements on the stack.
    '''

    def __init__(self, starting:Collection) -> None:
        '''
        Initializes the stack with the starting collection, where the last
        element of the starting collection is at the top of the stack.
        '''
        self._stack = []
        for e in starting:
            self.push(e)

    def push(self, element) -> None:
        '''
        Pushes the element onto the stack.
        '''
        self._stack.append(element)

    def pop(self) -> Union[None, object]:
        '''
        Pop the top element off the stack, or return None when empty.
        '''
        if (len(self._stack) == 0):
            return None
        return self._stack.pop()
    
    def peek(self) -> Union[None, object]:
        '''
        Peek at the top element of the stack or returns None when empty.
        Returns a copy of the element.
        '''
        if (len(self._stack) == 0):
            return None
        return deepcopy(self._stack[-1])
    
    def is_empty(self) -> bool:
        '''
        Returns True if the stack is empty, False otherwise.
        '''
        return len(self._stack) == 0
    

class OutOfMemoryQueue():
    """
    A Queue which stores the items outside of memory by writing to disk their
    pickled version and iterating over the file.

    Currently functionality is limited to:
        - adding items;
        - iterating over the queue;
        - checking the length of the queue.
    """
    def __init__(self, expand_size=100) -> None:
        self._dir = TemporaryDirectory(ignore_cleanup_errors=True)
        self._fname = 'queue.txt'
        self._write_head = open(join(self._dir.name, self._fname), 'bw')
        self._curr_expansion = []
        self._expand_size = expand_size
        self._members = 0 
        self._writing = False

    def append(self, item) -> None:
        pickled = pickle_dumps(item, 4)
        with open(join(self._dir.name, 'test.txt'), 'wb') as f:
            f.write(pickled)
        with open(join(self._dir.name, 'test.txt'), 'rb') as f:
            loaded_pickle = pickle_load(f)
        if item != loaded_pickle:
            raise ValueError("repickled the item does not preverse equality.")
        # remove tabs and new lines
        self._curr_expansion.append(item)
        if len(self._curr_expansion) > self._expand_size:
            self._wiriting = True
            self._write_head.write(pickle_dumps(self._curr_expansion, 4))
            self._writing = False
            self._write_head.flush()
            self._curr_expansion = []
        self._members += 1

    # data model functions
    def __len__(self) -> int:
        return self._members
    
    def __iter__(self):
        reader = open(join(self._dir.name, self._fname), 'br')
        while True:
            try:
                while self._writing:
                    import time
                    time.sleep(0.1)
                for item in pickle_load(reader):
                    yield item
            except EOFError:
                break
        for item in self._curr_expansion:
            yield item
        reader.close()

    def __del__(self):
        self._write_head.flush()
        self._write_head.close()
        self._dir.cleanup()

class OutOfMemorySet():
    """
    A Set which stores the items outside of memory by writing to disk their
    pickled version and iterating over the file.

    Currently functionality is limited to:
     - adding items;
     - checking for membership (based on hash, not ==);
     - iterating over the set;
     - checking the length of the set.
    """

    def __init__(self, expand_size=100) -> None:
        self._dir = TemporaryDirectory(ignore_cleanup_errors=True)
        self._fname = 'queue.txt'
        self._write_head = open(join(self._dir.name, self._fname), 'bw')
        self._members = 0 
        self._contains = set()
        self._curr_expansion = set()
        self._expand_size = expand_size
        self._writing = False

    def add(self, item) -> None:
        if item in self:
            debug(f"Item {item} already in set.")
            return
        pickled = pickle_dumps(item, 4)
        with open(join(self._dir.name, 'test.txt'), 'wb') as f:
            f.write(pickled)
        with open(join(self._dir.name, 'test.txt'), 'rb') as f:
            loaded_pickle = pickle_load(f)
        if item != loaded_pickle:
            raise ValueError("repickled the item does not preverse equality.")
        # remove tabs and new lines
        self._curr_expansion.add(item)
        if len(self._curr_expansion) > self._expand_size:
            self._writing = True
            self._write_head.write(pickle_dumps(self._curr_expansion, 4))
            self._writing = False
            self._write_head.flush()
            self._curr_expansion.clear()
        self._contains.add(item.__hash__()) 
        self._members += 1

    # data model functions
    def __len__(self) -> int:
        return self._members
    
    def __iter__(self):
        reader = open(join(self._dir.name, self._fname), 'br')
        while True:
            try:
                while self._writing:
                    import time
                    time.sleep(0.1)
                for item in pickle_load(reader):
                    yield item
            except EOFError as e:
                debug(f"Iterator error:: {e}")
                break
        for item in self._curr_expansion:
            yield item
        reader.close()

    def __contains__(self, item) -> bool:
        return item.__hash__() in self._contains

    def __del__(self):
        self._write_head.flush()
        self._write_head.close()
        self._dir.cleanup()