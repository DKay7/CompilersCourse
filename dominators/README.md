# Compilers course's test solver

## How-to install:
From this directory, execute:

0. make sure you have graphiz libs: `sudo apt install graphviz graphviz-dev`
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip3 install -r requirements.txt`

## How-to use:
To get help: `python3 dominators.py --help`

Create file, like in examples and run `python3 dominators.py path/to/your/file`

### File format:
```
entry parent_node
parent_node child1 child2 child3
child1 grand_child1
grandchild1 exit
child2 exit
```
Please, note that `entry` and `exit` nodes should be named **exactly** like that.

