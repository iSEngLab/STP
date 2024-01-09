"""
剪枝
"""
import copy
import common
import commonApi


def pruning(dependency_tree, root, dependencies, token, tokens_remain, s):
    """
    剪枝函数，对树进行剪枝
    :param dependency_tree: 依存树
    :param root: 依存树根结点
    :param dependencies: 依存关系
    :param token: token列表
    :param tokens_remain: 当前保留token index列表
    :param s: 当前字符串
    :return:
    """

    if len(dependency_tree.children(root)) > 0:
        nodes = dependency_tree.children(root)
        # 子节点个数大于0的节点按照子节点个数从大到小排列，子节点个数等于0的节点按照关系树中的顺序从左向右排列
        nodes1 = [x for x in nodes if len(dependency_tree.children(x.identifier)) == 0]
        nodes2 = [x for x in nodes if len(dependency_tree.children(x.identifier)) != 0]
        nodes2.sort(key=lambda x: len(dependency_tree.children(x.identifier)))
        nodes2.reverse()
        nodes = nodes2 + nodes1

        for node in nodes:
            index = node.identifier
            tag = node.data.type
            if (
                common.relationship.get(tag, -10) == 1
                or common.relationship.get(tag, -10) == -10
                or common.relationship.get(tag, -10) == 3
            ):
                if len(dependency_tree.children(index)) > 0:
                    s, tokens_remain = pruning(
                        dependency_tree,
                        index,
                        dependencies,
                        token,
                        tokens_remain,
                        s,
                    )
            elif common.relationship.get(tag, -10) == 4:
                return s, tokens_remain
            elif common.relationship.get(tag, -10) == 0:
                if len(dependency_tree.children(index)) > 0:
                    s, tokens_remain = pruning(
                        dependency_tree,
                        index,
                        dependencies,
                        token,
                        tokens_remain,
                        s,
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
            s = cut_subtree_from_dependency_tree(
                dependency_tree, index, tokens_remain, dependencies, token
            )
            return s, tokens_remain
        else:
            pass
    return s, tokens_remain


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
