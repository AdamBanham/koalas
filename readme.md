
<img src="./project_header.png" style="width=325px; height:auto;"/>

[![Python 3.[9,10,11]](https://github.com/AdamBanham/koalas/actions/workflows/python-version.yml/badge.svg?branch=main)](https://github.com/AdamBanham/koalas/actions/workflows/python-version.yml)  [![Python 3.[12,13]](https://github.com/AdamBanham/koalas/actions/workflows/python-version-latest.yml/badge.svg)](https://github.com/AdamBanham/koalas/actions/workflows/python-version-latest.yml)

`pmkoalas` provides data structures for process mining research in a well-organized pythonic style.

## Current Features
* Event log structures
    * Importing and exporting of logs to XES formatted XML
    * Several views/types of log
        * Simplified logs
            * This type only considers sequences of process activities, and 
            nothing else.
        * Complex logs
            * This type considers sequences of events. Where an event is a 
            mapping of data. This log type can always be reduced to the 
            simplified type.
    * Generating logs quickly using delimited strings
        * currently only supports simplified logs
* Process model structures
    * Petri nets
        * exporting to pnml
        * creating dot files for a net
        * generation of a net using fragments of desirable behaviour
* Process discovery techniques
    * Generating a directly follows language from a log
    * The Alpha miner (original variant)

# Development Information
To install dependencies:

`py -m pip install -e .[dev]`

## Testing
To run tests:

`py -m unittest`

# The values of the team

## Postel's law

"Be liberal in what you accept, and conservative in what you send"

[https://en.wikipedia.org/wiki/Jon_Postel](cite)

Branches off main are meant to be either merged in a timely manner,
or show off a potential feature, or should be removed/released back
into the wild.

Features need a use case or a user before they can be explored
in detail.

It is better to delete code that is not used, than to keep it
around. You have written it once, you will write it better the 
next time. Don't be afraid to let it go.

## Politely ask for more resources

While many optimisations can be done when asking for more threads and 
resources of the user's system, such optimisations should always be turned 
off by default. 