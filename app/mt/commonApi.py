from typing import Any
import copy

import treelib.exceptions

import app.mt.common as common
import nltk.tree as tree

from treelib import Tree as Tr


def replace_clause(token, clause_to_replace, replace_word):
    """
    Delete clauses, add replacement words, generate new sentences
    :param token: original sentence token sequence
    :param replace_word: clause replacement word
    :param clause_to_replace: clause
    :return: the generated sentence after the clause is replaced
    """
    clause_tokens = common.nlpEN.word_tokenize(clause_to_replace)
    tokens_after_replacement = copy.deepcopy(token)

    replace_index = -1
    # Search the original sentence token sequence for a subsequence that matches the clause token sequence.
    for i in range(0, len(token) - len(clause_tokens) + 1):
        index = 0
        while index < len(clause_tokens):
            if tokens_after_replacement[i + index] != clause_tokens[index]:
                break
            index += 1
        if index == len(clause_tokens):
            replace_index = i
            break
    # could not find it
    if replace_index < 0:
        return common.de_tokenizer.detokenize(token)
    # Replacement clause
    tokens_after_replacement = (
        tokens_after_replacement[:replace_index]
        + [replace_word]
        + tokens_after_replacement[replace_index + len(clause_tokens) :]
    )
    if len(tokens_after_replacement) > 0 and (
        tokens_after_replacement[0] == "," or tokens_after_replacement[0] == "."
    ):
        tokens_after_replacement.pop(0)
    return common.de_tokenizer.detokenize(tokens_after_replacement)


def remove_clause_tokens(clause, token):
    """
    Delete clause token
    :param clause: Delete part of the token list
    :param token: list of all tokens
    :return: Delete part of token index
    """
    clause_tokens = common.nlpEN.word_tokenize(clause)
    tokens_after_remove = []
    for i in range(0, len(token) - len(clause_tokens) + 1):
        index = 0
        while index < len(clause_tokens):
            if token[i + index] != clause_tokens[index]:
                break
            index += 1
        if index == len(clause_tokens):
            for j in range(len(clause_tokens)):
                tokens_after_remove.append(j + i)
    return tokens_after_remove


def token_to_sentence(token, remain_token_indexes):
    """
    Generate new sentences based on the tokens that need to be retained
    :param token: token list
    :param remain_token_indexes: token index needs to be retained
    :return: new clause
    """
    tokens = [token[i] for i in remain_token_indexes]
    return common.de_tokenizer.detokenize(tokens)


def cons_traversal(t):
    """
    Clause identification, splitting and judgment
    :param t: component tree
    :return:
    """
    queue = [t]
    while queue:
        current = queue.pop(0)
        if isinstance(current, tree.Tree):
            flag = False
            if current.label() == "SBAR":
                if len(current.leaves()) > 1:
                    common.clauses_tokens.append(current.leaves())
                    common.inseparable.append(current.leaves())
                continue
            for i in range(len(current)):
                if isinstance(current[i], tree.Tree) and (current[i].label() == "HYPH"):  # type: ignore
                    flag = True
            if not flag:
                for i in range(len(current)):
                    queue.append(current[i])
            else:
                common.inseparable.append(current.leaves())
        elif isinstance(current, str):
            pass


def should_retain(index):
    """
    Determine whether to retain
    :param index: token index
    :return: Judgment result
    """
    for i in common.retain_tokens:
        for j in i:
            if index == j:
                return True
    return False


def find_right_index(dependency, index):
    """
    Find the rightmost node with index as the root, used to split clauses
    :param dependency:
    :param index:
    :return:
    """
    right_index = index
    find_list = [index]
    visit = {}
    for dependency_item in dependency:
        visit[dependency_item] = False
    while len(find_list) > 0:
        pop_item = find_list.pop()
        for dependency_item in dependency:
            tag, begin, end = dependency_item
            if begin == pop_item and not visit[dependency_item]:
                right_index = max(right_index, end)
                visit[dependency_item] = True
                find_list.append(pop_item)
    return right_index


def find_inseparable(token):
    """
    Find the inseparable word index that needs to be retained
    :param token: token character
    :return: keep the index list
    """
    inseparable_list = []
    for i in range(len(token)):
        for item in common.inseparable:
            if len(item) > len(token):
                continue
            index = 0
            item_num = len(item)
            while index < item_num:
                if token[i + index] != item[index]:
                    break
                index += 1
            if index == item_num:
                ll = []
                for j in range(item_num):
                    ll.append(j + i)
                inseparable_list.append(ll)
    return inseparable_list


def dependency_traversal(dependency_tree, token, trunk):
    """
    Keep the main ingredients
    :param dependency_tree: dependency tree
    :param token: token list
    :param trunk: retain content list
    :return:
    """
    dependency_parse = copy.deepcopy(dependency_tree)
    token = copy.deepcopy(token)
    while len(dependency_parse) != 0:
        dependency_parse_item = dependency_parse.pop(0)
        i, _, end = dependency_parse_item
        if common.relationship.get(i, -10) == 3:
            trunk.append(end - 1)


class Node:
    def __init__(self, t, flag=0, word=""):
        self.type = t
        self.flag = flag
        self.word = word


def construct_dependency_tree(dependency, token):
    """
    Build dependency tree
    :param dependency: dependency tuple
    :param token: word segmentation result list
    :return: dependency tree
    """
    dependency_parse = copy.deepcopy(dependency)
    token = copy.deepcopy(token)
    t = Tr()
    root = -1

    # Build dependency tree
    dependency_parse.sort(key=lambda x: x[1])

    while len(dependency_parse) != 0:
        dependency_parse_item = dependency_parse.pop(0)
        i, begin, end = dependency_parse_item
        if begin == 0:
            root = end
            try:
                t.create_node(token[end - 1], end, data=Node(i, 0, token[end - 1]))
            except treelib.exceptions.MultipleRootError:
                continue
            continue
        elif t.contains(begin):
            t.create_node(
                token[end - 1], end, parent=begin, data=Node(i, 0, token[end - 1])
            )
        elif len(dependency_parse) >= 1:
            dependency_parse.append(dependency_parse_item)
    return t, root


class IndexTree(tree.Tree):
    def __init__(
        self,
        node,
        children: Any = None,
        indexes: list[Any] | None = None,
    ):
        super().__init__(node, children)
        self.indexes: list[Any] | None = indexes

    def __deepcopy__(self, memo):
        return type(self).convert(self)

    def makeList(self) -> dict[str, Any]:
        if isinstance(self, str):
            return {
                "name": self,
                "children": [],
            }
        return {
            "name": self._label,
            "children": [
                child.makeList()
                if not isinstance(child, str)
                else {
                    "name": child,
                    "children": [],
                }
                for child in self
            ],
        }

    def remove_nodes_at_same_level(self, cc_index: int, nodes_index, retain):
        """
        在找到保留并列成分的前提下,删除和cc同一level的并列成分
        :param cc_index: cc的index
        :param nodes_index: 需要删除的并列成分index
        :param retain: 需要保留的并列成分
        :return:
        """
        current: Any = self
        # 是否找到cc
        found = False
        while True:
            flag = False  # cc是否存在
            for k in range(len(current)):
                # 如果是cc
                if (
                    isinstance(current[k].indexes, list)
                    and len(current[k].indexes) == 1
                    and current[k].indexes[0] == cc_index
                ):
                    found = True
                    flag = True
                    break
                # cc所在子树
                if (
                    isinstance(current[k].indexes, list)
                    and cc_index in current[k].indexes
                ):
                    current = current[k]
                    flag = True
                    break
            # 如果找到cc或cc不存在
            if not flag or found:
                break
        if found:
            # 需要删除的树节点
            to_remove = []
            # 是否找到需保留的并列成分
            find_retain = False
            for i in range(len(current)):
                # 找到需保留并列成分
                if retain in current[i].indexes:
                    find_retain = True
                # 含有需删除并列成分
                if (
                    len(
                        set(current[i].indexes).intersection(
                            set(nodes_index + [cc_index])
                        )
                    )
                    > 0
                    and retain not in nodes_index
                ):
                    to_remove.append(current[i])
            if find_retain:
                [current.remove(i) for i in to_remove]

    @classmethod
    def convert(cls, t):
        """
        :type t: Tree
        :param t: The tree that should be converted.
        :return: The new Tree.
        """
        if isinstance(t, IndexTree):
            children = [cls.convert(child) for child in t]
            return cls(t._label, children, t.indexes)
        else:
            return t


def constituent_tree_with_indexes(constituent_tree: IndexTree | Any, start_index=1):
    """
    为成分树添加indexes
    :param constituent_tree:
    :param start_index:
    :return:
    """
    # 叶子节点
    if len(constituent_tree) == 1 and isinstance(constituent_tree[0], str):
        constituent_tree.indexes = [start_index]
    # 非叶子节点
    else:
        leaves = constituent_tree.leaves()
        constituent_tree.indexes = list(range(start_index, start_index + len(leaves)))

        offset = 0
        for i in range(len(constituent_tree)):
            child_leaves = constituent_tree[i].leaves()  # type: ignore
            constituent_tree_with_indexes(constituent_tree[i], offset + start_index)
            offset += len(child_leaves)


def read_conf(p="./related-documentation/Relationship"):
    """
    读取配置文件
    :return:
    """
    f = open(p)
    line = f.readline()
    while line:
        line = line[0 : len(line) - 1]
        sarr = line.split(" ")
        common.relationship[sarr[0]] = eval(sarr[1])
        line = f.readline()
    f.close()


def is_invert_wh_structure(sbar):
    """
    宾语前置句
    :param sbar: 从句短语树
    :return:
    """
    if len(sbar) < 2:
        return False
    return sbar[0].label() == "WHNP" and is_sp_structure(sbar[1])


def is_sp_structure(t):
    """
    主谓结构
    :param t: 短语树
    :return:
    """
    if len(t) < 2:
        return False
    return t[0].label() == "NP" and t[1].label() == "VP"
