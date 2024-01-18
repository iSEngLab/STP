import copy
import common
import commonApi


def pruning(
    dependency_tree, root, dependencies, tokens, remaining_tokens_indices, sentence
):
    """
    Applies the novel core semantics-preserving pruning strategy.
    Args:
        dependency_tree: Dependency tree.
        root: The root node of the dependency tree.
        dependencies: List of dependency relationships.
        token: List of tokens.
        remaining_tokens_indices: List of indices indicating the tokens to be retained.
        sentence: Current source sentence.
    """

    if len(dependency_tree.children(root)) == 0:
        tag = dependency_tree.nodes[root].data.type
        index = dependency_tree.nodes[root].identifier
        if common.relationship.get(tag, -10) == 0 and not commonApi.should_retain(
            index
        ):
            sentence = cut_subtree_from_dependency_tree(
                dependency_tree, index, remaining_tokens_indices, dependencies, tokens
            )
        return sentence, remaining_tokens_indices

    # len(dependency_tree.children(root)) > 0
    nodes = dependency_tree.children(root)
    # Nodes with the number of child nodes equal to 0 are arranged from left to right in the order in the relationship tree.
    nodes1 = [x for x in nodes if len(dependency_tree.children(x.identifier)) == 0]
    # Nodes with the number of child nodes greater than 0 are arranged from large to small according to the number of child nodes.
    nodes2 = [x for x in nodes if len(dependency_tree.children(x.identifier)) != 0]
    nodes2.sort(key=lambda x: len(dependency_tree.children(x.identifier)))
    nodes2.reverse()

    nodes = nodes2 + nodes1

    # Start recursively traversing the dependency tree.
    for node in nodes:
        index = node.identifier
        tag = node.data.type
        if (
            # Relationship 1 refers to either of the following:
            # dependent (dep)
            # auxiliary verbs or copula (aux, auxpass, cop),
            # clausal complement and open clausal complement (ccomp, xcomp),
            # expletive (expl) - e.g. "there are", "here is" and "it is", "indeed", “in fact”
            # determiner (det)
            # multi-word expression (mwe)
            # marker (mark)
            # particle (prt)
            # goes with (goeswith)
            # case marker (case)
            common.relationship.get(tag, -10) == 1
            # No relationship.
            or common.relationship.get(tag, -10) == -10
            # Relationship 3 refers to either of the following:
            # Object-related dependencies (obj, dobj, iobj)
            # Subject-related dependencies (nsubj, csubj, xsubj)
            or common.relationship.get(tag, -10) == 3
        ):
            if len(dependency_tree.children(index)) > 0:
                sentence, remaining_tokens_indices = pruning(
                    dependency_tree,
                    index,
                    dependencies,
                    tokens,
                    remaining_tokens_indices,
                    sentence,
                )
        # punctuation (punct)
        # parataxis
        elif common.relationship.get(tag, -10) == 4:
            return sentence, remaining_tokens_indices
        # adjectival clause modifier (acl)
        # adverbial modifier (advmod)
        # compound (compound)
        elif common.relationship.get(tag, -10) == 0:
            if len(dependency_tree.children(index)) > 0:
                sentence, remaining_tokens_indices = pruning(
                    dependency_tree,
                    index,
                    dependencies,
                    tokens,
                    remaining_tokens_indices,
                    sentence,
                )
                # After pruning the subtree
                if len(dependency_tree.children(index)) >= 0:
                    cut_subtree_from_dependency_tree(
                        dependency_tree,
                        index,
                        remaining_tokens_indices,
                        dependencies,
                        tokens,
                    )
            # If there is no need to retain
            elif not commonApi.should_retain(index):
                cut_subtree_from_dependency_tree(
                    dependency_tree,
                    index,
                    remaining_tokens_indices,
                    dependencies,
                    tokens,
                )

    return sentence, remaining_tokens_indices


def cut_subtree_from_dependency_tree(
    dependency_tree, index, remaining_tokens_indices, dependencies, tokens
):
    """
    Cuts a subtree from a dependency tree, updates the necessary data structures, and
    generates a sentence from the modified tree structure.

    Args:
        dependency_tree: dependency tree
        index: the index of the subtree root node that needs to be pruned
        remaining_tokens_indices: list of indices for tokens that need to be retained
        dependencies: list of dependencies
        tokens: full list of tokens
    """
    # Store the removed subtree.
    removed_subtree = dependency_tree.remove_subtree(index)
    removed_nodes = removed_subtree.nodes
    # Updates the list of remaining tokens by removing the indices of the nodes in the removed subtree.
    for node in removed_nodes:
        remaining_tokens_indices.remove(node - 1)
    # Remove dependencies that involve the root of the removed subtree from the list of dependencies.
    for dependency in dependencies:
        if dependency[2] == index:
            dependencies.remove(dependency)

    temp_tree = copy.deepcopy(dependency_tree)
    common.remove_tree_dist[index] = temp_tree
    # Generates a sentence (s) from the modified list of tokens.
    s = commonApi.generate_subsentence(tokens, remaining_tokens_indices)
    s = s.replace("  ", " ")
    common.sentences_gen.append(s)
    return s
