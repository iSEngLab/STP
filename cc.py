import copy
import commonApi
import common

# def cc_part(dependencies, token):
#     """
#
#     :param dependencies: 依赖关系
#     :param token: token列表
#     :return:
#     """
#     result = []
#     # 找出所有的conj
#     conjs = filter(lambda x: x[0].startswith("conj"), dependencies)
#     conjs = [(x[1], x[2]) for x in conjs]
#
#     if len(conjs) == 0:
#         return []
#
#     # 对conj进行分组
#     head = set([z[0] for z in conjs])
#     conjs_groups = [[x for x in conjs if x[0] == y] for y in head]
#
#     # 按照conj组进行操作
#     for conjs_group in conjs_groups:
#         node_indexes = []
#         for t in conjs_group:
#             node_indexes += list(t)
#         node_indexes = set(node_indexes)
#         for node_index in node_indexes:
#             # 需要删除的并列成分
#             index_to_remove = node_indexes.difference({node_index})
#             # 复制关系树
#             dependencies_copy = copy.deepcopy(dependencies)
#             # 在关系树中将含有这些并列成分的关系去除
#             dependencies_copy_remain = filter(
#                 lambda x: x[1] not in index_to_remove and x[2] not in index_to_remove, dependencies_copy)
#
#             # 去除保留并列成分上的cc
#             dependencies_copy_remain = list(filter(
#                 lambda x: x[0] != "cc" or (x[0] == "cc" and x[1] != node_index),
#                 dependencies_copy_remain))
#
#             # 转化为可达性矩阵
#             arrival_matrix = [[0] * (len(token) + 1) for _ in range(len(token) + 1)]
#             for d in dependencies_copy_remain:
#                 arrival_matrix[d[1]][d[2]] = 1
#
#             # 从保留的并列成分开始搜索
#             arrival_token_index = {node_index}
#             current_token_index = {node_index}
#             while len(current_token_index) > 0:
#                 current = current_token_index.pop()
#                 can_arrive = set()
#                 # 搜索行
#                 for i in range(len(token)):
#                     if arrival_matrix[current][i] > 0:
#                         can_arrive.add(i)
#                 # 搜索列
#                 for i in range(len(token)):
#                     if arrival_matrix[i][current] > 0:
#                         can_arrive.add(i)
#                 # 尚未搜索到的
#                 new_added = can_arrive.difference(arrival_token_index)
#                 # 加入
#                 arrival_token_index = arrival_token_index.union(new_added)
#                 current_token_index = current_token_index.union(new_added)
#             arrival_token_index = list([x - 1 for x in arrival_token_index if x > 0])
#             arrival_token_index.sort()
#             result.append(token_to_sentence(token, arrival_token_index))
#     # print(result)
#     return result


def cc_part(dependencies, constituent_tree: commonApi.IndexTree):
    """
    借助依存树和语法树进行剪枝
    :param constituent_tree:
    :param dependencies:
    :return:
    """

    commonApi.constituent_tree_with_indexes(constituent_tree)
    result = []
    # 找出所有的conj
    conjs = filter(lambda x: x[0].startswith("conj"), dependencies)
    conjs = [(x[1], x[2]) for x in conjs]

    if len(conjs) == 0:
        return []

    # 对conj进行分组
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

    # 找出属于每个conj组的cc
    ccs = []
    for conjs_group in conjs_groups_flat:
        cc = filter(lambda x: x[0] == "cc" and x[1] in conjs_group, dependencies)
        ccs.append([x[2] for x in cc])

    for i in range(len(conjs_groups_flat)):
        conjs_group = conjs_groups_flat[i]
        cc = list(ccs[i])
        # 如果一组并列成分没有cc,不处理
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
