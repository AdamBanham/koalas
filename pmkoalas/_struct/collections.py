'''
This module contains typical useful restricts on collections in computer 
science.

Included are the following structures:
    - `Stack`
'''
from copy import deepcopy
from typing import Collection, Union

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
        Pushes a copy of the element onto the stack.
        '''
        self._stack.append(deepcopy(element))

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