import copy
import common
import commonApi


def pruning(dependency_tree, root, dependencies, token, tokens_remain, sentence):
    """
    Applies the novel core semantics-preserving pruning strategy.
    Args:
        dependency_tree: Dependency tree.
        root: The root node of the dependency tree.
        dependencies: List of dependency relationships.
        token: List of tokens.
        tokens_remain: List of indices indicating the tokens to be retained.
        sentence: Current source sentence.
    """

    if len(dependency_tree.children(root)) > 0:
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
                common.relationship.get(tag, -10) == 1
                or common.relationship.get(tag, -10) == -10
                or common.relationship.get(tag, -10) == 3
            ):
                if len(dependency_tree.children(index)) > 0:
                    sentence, tokens_remain = pruning(
                        dependency_tree,
                        index,
                        dependencies,
                        token,
                        tokens_remain,
                        sentence,
                    )
            elif common.relationship.get(tag, -10) == 4:
                return sentence, tokens_remain
            elif common.relationship.get(tag, -10) == 0:
                if len(dependency_tree.children(index)) > 0:
                    sentence, tokens_remain = pruning(
                        dependency_tree,
                        index,
                        dependencies,
                        token,
                        tokens_remain,
                        sentence,
                    )
                    # 对子树进行剪枝之后
                    if len(dependency_tree.children(index)) >= 0:
                        cut_subtree_from_dependency_tree(
                            dependency_tree,
                            index,
                            tokens_remain,
                            dependencies,
                            token,
                        )
                # 如果不需要保留
                elif not commonApi.should_retain(index):
                    cut_subtree_from_dependency_tree(
                        dependency_tree,
                        index,
                        tokens_remain,
                        dependencies,
                        token,
                    )
    else:
        tag = dependency_tree.nodes[root].data.type
        index = dependency_tree.nodes[root].identifier
        if common.relationship.get(tag, -10) == 0 and not commonApi.should_retain(
            index
        ):
            sentence = cut_subtree_from_dependency_tree(
                dependency_tree, index, tokens_remain, dependencies, token
            )
            return sentence, tokens_remain
        else:
            pass
    return sentence, tokens_remain


def cut_subtree_from_dependency_tree(
    dependency_tree, index, tokens_remain, dependencies, token
):
    """

    :param dependency_tree: 依赖关系树
    :param index: 需要剪掉的子树根节点index
    :param tokens_remain: 需要保留的token index
    :param dependencies: 依赖关系列表
    :param token: 所有的token
    :return:
    """
    remove = dependency_tree.remove_subtree(index)
    remove_node = remove.nodes
    # 删除(依赖关系、token序列)
    for i in remove_node:
        tokens_remain.remove(i - 1)
    for dependency in dependencies:
        if dependency[2] == index:
            dependencies.remove(dependency)
    temp_tree = copy.deepcopy(dependency_tree)
    common.remove_tree_dist[index] = temp_tree
    # 生成剪枝后的句子
    s = commonApi.token_to_sentence(token, tokens_remain)
    s = s.replace("  ", " ")
    common.sentences_gen.append(s)
    return s
