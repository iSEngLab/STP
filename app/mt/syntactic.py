"""
句式分析
"""

from nltk.tree.parented import ParentedTree

import nltk.tree as tree

import app.mt.commonApi as commonApi
import app.mt.common as common


def find_clauses(sent):
    """
    识别从句
    :param sent:
    :return:
    """
    t = tree.Tree.fromstring(common.nlpEN.parse(sent))  # 生成短语结构树
    common.clauses_tokens.clear()
    common.sentences_gen.clear()
    parent_tree = ParentedTree.convert(t)
    # 主语从句：
    s_clause, s_sentence, s_add_sentence = find_subject_clause(parent_tree)

    # 表语从句：
    parent_tree = ParentedTree.convert(t)
    t_clause, t_sentence, t_add_sentence = find_predicative_clause(parent_tree)

    # 其他名词性从句：
    parent_tree = ParentedTree.convert(t)
    d_clause, d_sentence, d_add_sentence = find_other_clause(parent_tree)

    result = []
    token = common.nlpEN.word_tokenize(sent)

    # 由于从句可能出现包含关系，这里为了能够最大程度去除从句，因而按照长度从长到短依次去除从句
    s_t_d = [
        (s_clause, s_sentence, s_add_sentence),
        (t_clause, t_sentence, t_add_sentence),
        (d_clause, d_sentence, d_add_sentence),
    ]
    s_t_d.sort(key=lambda x: len(x[1]), reverse=True)
    for s_t_d_clause, s_t_d_sentence, s_t_d_add_sentence in s_t_d:
        clause_de_tokenize = common.de_tokenizer.detokenize(s_t_d_clause)
        sentence_de_tokenize = common.de_tokenizer.detokenize(s_t_d_sentence)
        if clause_de_tokenize != "":
            clause_de_tokenize = clause_de_tokenize + "."
            result.append(clause_de_tokenize)
            sent = commonApi.replace_clause(
                token, sentence_de_tokenize, s_t_d_add_sentence
            )
            token = common.nlpEN.word_tokenize(sent)

    source_tree = tree.Tree.fromstring(common.nlpEN.parse(sent))
    clauses_local = []
    common.clauses_tokens.clear()
    common.sentences_gen.clear()
    clauses_remain_tokens = []
    token = common.nlpEN.word_tokenize(sent)
    main_remain_token_indexes = [i for i in range(len(token))]  # 主句保留的token index
    # 对于从句的删除应该是连续的token
    commonApi.cons_traversal(source_tree)  # 识别不可拆组合词、从句

    # 如果主句中还有从句
    if len(common.clauses_tokens) > 0:
        # 对每一句从句
        for i in range(len(common.clauses_tokens)):
            clause = " ".join(common.clauses_tokens[i])
            # 删除从句
            remain_tokens = commonApi.remove_clause_tokens(clause, token)
            if clause[-1] != ".":
                clause += "."
            clauses_remain_tokens.append(remain_tokens)
            clauses_local.append(clause)

    # 从主句的token index删除从句
    for clause_token in clauses_remain_tokens:
        for j in clause_token:
            main_remain_token_indexes.remove(j)
    # 对主句进行处理：
    sent_main = commonApi.token_to_sentence(token, main_remain_token_indexes)
    clauses_local += result
    return sent_main, clauses_local


def find_subject_clause(sent_tree):
    """
    主语从句
    :param sent_tree:
    :return:从句token(替换词)，从句token(无替换词)，替换词
    e.g. input: What is good to you is good to me.
         output: ['it','is','good','to','you'], ['what','is','good','to','you'],'it'
    """
    # 主语从句：
    queue = [sent_tree]
    s_clause = []
    s_add_sentence = ""
    s_sentence = []
    invert_wh = False  # 宾语前置wh句式
    original_wh = ""  # wh原词
    while len(queue) > 0:
        current = queue.pop(0)
        if isinstance(current, tree.Tree):
            if current.label() == "SBAR":  # sbar:subordinate clause，从句
                if len(queue) == 0:
                    break
                current_next = queue[0]
                if (
                    isinstance(current_next, tree.Tree)
                    and current.parent() == current_next.parent()  # type: ignore
                    and current_next.label() == "VP"
                ):  # Verb phrase
                    s_sentence = current.leaves()
                    son = current[0]
                    if isinstance(son, tree.Tree):
                        if son.label() == "WHNP":
                            original_wh = son.leaves()[0]
                            invert_wh = commonApi.is_invert_wh_structure(current)
                            if (
                                len(son.leaves()) == 1
                                and son.leaves()[0].lower() == "who"
                            ):
                                s_add_sentence = "he"
                            else:
                                s_add_sentence = "it"
                            current.remove(son)
                        elif son.label() == "IN":
                            current.remove(son)
                        s_clause = current.leaves()
                    break
            for i in range(len(current)):
                queue.append(current[i])

    s_add_sentence2 = [s_add_sentence] if s_add_sentence != "" else []
    return (
        ([original_wh] + s_clause if invert_wh else s_add_sentence2 + s_clause),
        s_sentence,
        s_add_sentence,
    )


def find_predicative_clause(sent_tree):
    """
    表语从句
    :param sent_tree:
    :return:从句token(替换词)，从句token(无替换词)，替换词
    e.g. input: He looked just as he had looked ten years before.
         output: ['just', 'as', 'he', 'had', 'looked', 'ten', 'years', 'before'], ['just', 'as', 'he', 'had', 'looked', 'ten', 'years', 'before'],''
    """
    queue = [sent_tree]
    t_clause = []
    t_sentence = []
    t_add_sentence = ""
    invert_wh = False  # 宾语前置wh句式
    original_wh = ""  # wh原词
    while len(queue) > 0:
        current = queue.pop(0)
        if isinstance(current, tree.Tree):
            if current.label() == "VP":
                if len(current) > 1:
                    flag1 = False
                    flag2 = False
                    index_to = -1
                    for i in range(len(current)):
                        if (
                            not flag1
                            and isinstance(current[i], tree.Tree)
                            and (current[i].label().startswith("VB"))  # type: ignore
                        ):
                            flag1 = True
                        if (
                            flag1
                            and not flag2
                            and isinstance(current[i], tree.Tree)
                            and (current[i].label() == "SBAR")  # type: ignore
                        ):
                            flag2 = True
                            index_to = i

                    if flag1 and flag2:
                        t_sentence = current[index_to].leaves()  # type: ignore
                        son = current[index_to][0]
                        if isinstance(son, tree.Tree):
                            if son.label() == "WHNP":
                                original_wh = son.leaves()[0]
                                invert_wh = commonApi.is_invert_wh_structure(current)
                                if son.leaves()[0].lower() == "who":
                                    t_add_sentence = "he"
                                else:
                                    t_add_sentence = "it"
                                current[index_to].remove(son)
                            elif son.label() == "IN":
                                current[index_to].remove(son)
                            t_clause = current[index_to].leaves()  # type: ignore
                        break

            for i in range(len(current)):
                queue.append(current[i])

    t_add_sentence2 = [t_add_sentence] if t_add_sentence != "" else []
    return (
        (([original_wh] + t_clause) if invert_wh else (t_add_sentence2 + t_clause)),
        t_sentence,
        "",
    )


def find_other_clause(sent_tree):
    """
    其他名词性从句
    :param sent_tree:
    :return:从句token(替换词)，从句token(无替换词)，替换词
    e.g. input: He who is a doctor is famous.
         output: ['he', 'is', 'a', 'doctor'], ['who', 'is', 'a', 'doctor'], ''
    """
    queue = [sent_tree]
    d_clause = []
    d_sentence = []
    d_add_sentence = ""
    invert_wh = False  # 宾语前置wh句式
    original_wh = ""  # wh原词
    while len(queue) > 0:
        current = queue.pop(0)
        if isinstance(current, tree.Tree):
            if current.label() == "NP":
                if len(current) > 1:
                    flag1 = False
                    flag2 = False
                    index_to = -1
                    for i in range(len(current)):
                        if (
                            not flag1
                            and isinstance(current[i], tree.Tree)
                            and (current[i].label() == "NP")  # type: ignore
                        ):
                            flag1 = True
                        if (
                            flag1
                            and not flag2
                            and isinstance(current[i], tree.Tree)
                            and (current[i].label() == "SBAR")  # type: ignore
                        ):
                            flag2 = True
                            index_to = i

                    if flag1 and flag2:
                        d_sentence = current[index_to].leaves()  # type: ignore
                        son = current[index_to][0]
                        if isinstance(son, tree.Tree):
                            if son.label() == "WHNP":
                                original_wh = son.leaves()[0]
                                invert_wh = commonApi.is_invert_wh_structure(current)
                                if son.leaves()[0].lower() == "who":
                                    d_add_sentence = "he"
                                else:
                                    d_add_sentence = "it"
                                current[index_to].remove(son)
                            elif son.label() == "IN":
                                current[index_to].remove(son)
                            d_clause = current[index_to].leaves()  # type: ignore
                        break
            for i in range(len(current)):
                queue.append(current[i])

    d_add_sentence2 = [d_add_sentence] if d_add_sentence != "" else []
    return (
        ([original_wh] + d_clause if invert_wh else d_add_sentence2 + d_clause),
        d_sentence,
        "",
    )


if __name__ == "__main__":
    print(
        find_clauses(
            "he said he expected that fiscal policy will be supportive and the macro leverage ratio will rise modestly next year."
        )
    )
