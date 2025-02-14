# Growing Pains in development

- Currently difficult to extend `PetriNet` 
    - They are complex math structures that does not lend towards a clear hierachy or OOP class
    - PetriMarking is a good example of bad composition
    - Graphs should precal postset-T and preset-T 
    - tid/pid is number; they just need to be objects.
    - exporting and reading pnmls
        - we use be able to get a lpn from a dpn
        - could use a chain of responsiblity (pattern) for export/read

- Dr. B.: I had seperated state and execution semantics, but did not add classes to core
    - favour composition over inheritance
- greater distinction between `accepted structures` and `research`/`experimental` concepts.
    - rule of thumb: `popular`/`highly cited` must be exist in literature
- for the library to be good, it needs to be a software development project first and foremost.
- hinting/code should not lie to you

- For users (i.e. researchers) and you wanted to propose some new concepts using library.
    - we suggest the following procedure:
        - add a dependency to `your` project
        - use our structures and have fun
        - If really want to change a shortcut, hard fork and change the class `inline`.
        - but don't except us to merge your code 