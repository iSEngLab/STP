import copy
import app.mt.commonApi as commonApi
import app.mt.common as common


def cc_part(dependencies, constituent_tree: commonApi.IndexTree):
    """
    Pruning with dependency trees and syntax trees
    :param constituent_tree:
    :param dependencies:
    :return:
    """

    commonApi.constituent_tree_with_indexes(constituent_tree)
    result = []
    # Find all conj
    conjs = filter(lambda x: x[0].startswith("conj"), dependencies)
    conjs = [(x[1], x[2]) for x in conjs]

    if len(conjs) == 0:
        return []

    # Group conj
    head = set([z[0] for z in conjs])
    conjs_groups = [[x for x in conjs if x[0] == y] for y in head]
    conjs_groups_flat = []
    for conjs_group in conjs_groups:
        t = []
        for c in conjs_group:
            if c[0] not in t:
                t.append(c[0])
            if c[1] not in t:
                t.append(c[1])
        conjs_groups_flat.append(t)

    # Find the cc belonging to each conj group
    ccs = []
    for conjs_group in conjs_groups_flat:
        cc = filter(lambda x: x[0] == "cc" and x[1] in conjs_group, dependencies)
        ccs.append([x[2] for x in cc])

    for i in range(len(conjs_groups_flat)):
        conjs_group = conjs_groups_flat[i]
        cc = list(ccs[i])
        # If a group of parallel components does not have cc, it will not be processed.
        if len(cc) == 0:
            continue
        for j in range(len(conjs_group)):
            conjs_to_remove = copy.deepcopy(conjs_group)
            conjs_to_remove.pop(j)
            constituent_tree_copy = copy.deepcopy(constituent_tree)
            cc_to_remove = cc[0]
            constituent_tree_copy.remove_nodes_at_same_level(
                cc_to_remove, conjs_to_remove, conjs_group[j]
            )
            result.append(
                common.de_tokenizer.detokenize(constituent_tree_copy.leaves())
            )
    return result
