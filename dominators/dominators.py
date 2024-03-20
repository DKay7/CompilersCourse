import matplotlib.pyplot as plt
import networkx as nx
import sys


def main():
    if len(sys.argv) <= 1 or 'help' in sys.argv[1].lower().strip():
        print_help_and_exit() 
    
    cfg = nx.read_adjlist(sys.argv[1], create_using=nx.DiGraph())

    print("\n\nDOMINATORS:")
    doms = compute_dominators(cfg)
    print_dominators(doms)
    plot_graph(cfg, 'neato')

    print("\n\nIMMEDIATE DOMINATORS:\n")
    imm_doms = compute_immediate_dominators(cfg, doms)
    print_immediate_dominators(imm_doms)

    dom_tree = create_dominators_tree(imm_doms)
    plot_graph(dom_tree, 'dot')

    return


def compute_dominance_frontier(cfg: nx.DiGraph, dom_tree: nx.DiGraph):
    sink_nodes = [node for node in cfg.nodes if len(cfg.pred[node]) > 1]


def create_dominators_tree(immediate_dominators: dict):
    dom_tree = nx.DiGraph(immediate_dominators)
    return dom_tree

def compute_immediate_dominators(cfg: nx.DiGraph, dominators: dict):
    immediate_dominators = dict()

    for cur_node, cur_node_dominators in dominators.items():
        print(f"Processing {cur_node} with Dom[{cur_node}] = {cur_node_dominators}")

        for dom in cur_node_dominators:
            if dom == cur_node:
                continue
            
            #checks that there's no cur_node dominators between dom and cur_node
            path = nx.shortest_path(cfg, dom, cur_node)
            is_imm_dom = True

            print(f"\tprocessing imm dom candidate: {dom}\n\tpath from {dom} to {cur_node}: {path}")

            for node in path:
                if node != cur_node and node != dom and node in cur_node_dominators:
                    print(f"\tnode {node} in path from {dom} to {cur_node} is {cur_node}'s dominator so it's not imm. dominator")
                    is_imm_dom = False
                    break
            
            if is_imm_dom:
                print(f"\taccepting {dom} as imm. dom for {cur_node}")
                immediate_dominators[cur_node] = [dom] # Adding a list because it will be easier to plot dom tree lately
                break

    return immediate_dominators


def compute_dominators(cfg: nx.DiGraph):
    dominators = {}

    # Fill initial dominators as all nodes
    for node in cfg.nodes:
        dominators[node] = set(cfg.nodes)

    dominators['entry'] = {'entry'}

    changed = True

    while changed:
        changed = False

        for node in cfg.nodes:
            print(f"Processing {node}\n\tPreds[{node}] = {cfg.pred[node]}")
            cur_node_dominators = dominators[node]

            for predcessor in cfg.predecessors(node):
                print(f"\tPredcessor {predcessor}")

                # intersect all predcessors' dominators
                # and save result as current node's dominators
                cur_node_dominators &= dominators[predcessor]
                print(f"\t\tIntersecting {dominators[predcessor]} and {cur_node_dominators}")

            print(f"Dominators[{node}] = [{node}] U {cur_node_dominators}")

            cur_node_dominators  |= {node}
            # if computed dominators are not equal to saved
            # then something changed...
            if cur_node_dominators != dominators[node]:
                changed = True 
            
            dominators[node] = cur_node_dominators

    return dominators


def plot_graph(graph, program='dot'):
    pos = nx.nx_agraph.graphviz_layout(graph, prog=program)
    nx.draw(graph, with_labels=True)
    plt.show()
    return


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
