import matplotlib.pyplot as plt
import networkx as nx
import sys
from copy import deepcopy

REVERSE = False

def main():
    if len(sys.argv) <= 1 or 'help' in sys.argv[1].lower().strip():
        print_help_and_exit() 
    
    cfg = nx.read_adjlist(sys.argv[1], create_using=nx.DiGraph())

    print("\n-----------------\nNORMAL GRAPH\n-----------------\n")
    solve_all(cfg)
    
    print("\n-----------------\nREVERSED GRAPH\n-----------------\n")
    cfg.reverse()
    solve_all(cfg)
    
    return


def solve_all(cfg: nx.DiGraph):
    print("\n\nDOMINATORS:")
    doms = compute_dominators(cfg)
    print_dominators(doms)
    plot_graph(cfg, 'neato')

    print("\n\nIMMEDIATE DOMINATORS:\n")
    imm_doms = compute_immediate_dominators(cfg, doms)
    print_immediate_dominators(imm_doms)

    print("\nIMMEDIATE DOMINATORS BY NETWORKX")
    nx_imm_dom = nx.immediate_dominators(cfg, 'entry')
    print_immediate_dominators(nx_imm_dom)

    dom_tree = create_dominators_tree(imm_doms)
    plot_graph(dom_tree, 'dot')

    dom_front = compute_dominance_frontier(cfg, imm_doms)
    print_dominance_frontier(dom_front)

    print("\nDOMINANCE FRONTIER BY NETWORKX")
    nx_dom_front = nx.dominance_frontiers(cfg, 'entry')
    print_dominance_frontier(nx_dom_front)


def compute_dominance_frontier(cfg: nx.DiGraph, immediate_dominators: dict):
    print("\nComputuing dominance frontier...")

    dom_frontier = dict()
    for node in cfg.nodes:
        dom_frontier[node] = set()

    sink_nodes = [node for node in cfg.nodes if len(cfg.pred[node]) > 1]
    print(f"Sink nodes: {sink_nodes}\n")

    for sink_node in sink_nodes:
        print(f"Processing {sink_node}")
        print(f"\tPredcessors: {cfg.pred[sink_node]}")

        for predcessor in cfg.predecessors(sink_node):
            cur_node = predcessor

            print(f"\t\tprocessing predcessor {predcessor}")
            print(f"\t\ttraversing IDomTree from {cur_node} to {immediate_dominators[sink_node]}")

            while cur_node and cur_node != immediate_dominators[sink_node]:
                print(f"\t\t\tDF({cur_node}) = DF({cur_node}) U {sink_node}")

                dom_frontier[cur_node].add(sink_node)

                # Processing special case bc. IDom(entry) = []
                cur_node = immediate_dominators[cur_node]

    return dom_frontier


def create_dominators_tree(immediate_dominators: dict):
    dom_tree = nx.DiGraph()
    dom_tree_edges = [edge for edge in immediate_dominators.items() if edge[1]]

    dom_tree.add_nodes_from(immediate_dominators.keys())
    dom_tree.add_edges_from(dom_tree_edges)
    return dom_tree

def compute_immediate_dominators(cfg: nx.DiGraph, dominators: dict):
    print("\nComputing immediate dominators...")
    immediate_dominators = dict()
    immediate_dominators['entry'] = None #TODO: ['entry']

    for cur_node, cur_node_dominators in dominators.items():
        print(f"Processing {cur_node} with Dom[{cur_node}] = {cur_node_dominators}")

        for dom in cur_node_dominators:
            if dom == cur_node:
                continue
            
            #checks that there's no cur_node dominators between dom and cur_node
            path = nx.shortest_path(cfg, dom, cur_node)
            is_imm_dom = True

            print(f"\tprocessing imm. dom. candidate: {dom}")
            print(f"\t\tpath from {dom} to {cur_node}: {path}")

            for node in path:
                if node != cur_node and node != dom and node in cur_node_dominators:
                    print(f"\t\tnode {node} in path from {dom} to {cur_node} is {cur_node}'s dominator so it's not imm. dominator")
                    is_imm_dom = False
                    break
            
            if is_imm_dom:
                print(f"\t\taccepting {dom} as imm. dom for {cur_node}")
                immediate_dominators[cur_node] = dom
                break

    return immediate_dominators


def compute_dominators(cfg: nx.DiGraph):
    print("\nComputing dominators...")

    dominators = {}

    # Fill initial dominators as all nodes
    for node in cfg.nodes:
        dominators[node] = set(cfg.nodes)

    dominators['entry'] = {'entry'}

    changed = True
    first_iteration = True

    while changed:

        changed = False
        if not first_iteration:
            print("\n------\nSomething have changed so we have to iterate one more time\n------\n")

        for node in cfg.nodes:
            print(f"Processing {node}\n\tPreds[{node}] = {cfg.pred[node]}")
            cur_node_dominators = deepcopy(dominators[node])

            for predcessor in cfg.predecessors(node):
                print(f"\tPredcessor {predcessor}")

                # intersect all predcessors' dominators
                # and save result as current node's dominators
                print(f"\t\tIntersecting {dominators[predcessor]} and {cur_node_dominators}")
                cur_node_dominators &= dominators[predcessor]

            print(f"Dominators[{node}] = [{node}] U {cur_node_dominators}")

            cur_node_dominators  |= {node}
            # if computed dominators are not equal to saved
            # then something changed...
            if cur_node_dominators != dominators[node]:
                changed = True
                first_iteration = False

            dominators[node] = cur_node_dominators

    return dominators


def plot_graph(graph, program='dot'):
    pos = nx.nx_agraph.graphviz_layout(graph, prog=program)
    nx.draw(graph, with_labels=True)
    plt.show()
    return


def print_dominance_frontier(dominance_frontier: dict):
    print("\nDOMINANCE FRONTIER LIST:")
    for node, dom_front in dominance_frontier.items():
        print(f"DF({node}) = {list(dom_front)}")


def print_dominators(dominators: dict):
    print("\nDOMINATORS LIST:")
    for node, doms in dominators.items():
        print(f"DOM({node}) = {list(doms)}\n")


def print_immediate_dominators(dominators: dict):
    print("\nIMMEDIATE DOMINATORS LIST:")
    for node, imm_dom in dominators.items():
        print(f"IMM_DOM({node}) = {imm_dom}\n")


def print_help_and_exit():
    print(
        "Provide path to file, containing graph as first argument.",
        "File must contain graph's adjastency list and it's structure must be:",
        "`a b c # source target target`",
        "where `#` is comment separator.",
        "You can check file's example in examples/cfg_example.adj",
        "P.S. `entry` and `exit nodes should be named exactly like in the example`",
        sep='\n'
    )
    
    exit(0)


if __name__ == "__main__":
    main()
