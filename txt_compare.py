#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Revision : txt_compare_v2_0.py
# @Author : https://zhuanlan.zhihu.com/p/62910942；vivid_yellow
# @Date : 2020-4-16

# Previous version : asr_txt_comp_v1_0.py
# Function :
"""
    比对两个中文句子（或者多个句子的总距离）的距离（莱文斯坦距离，又称 Levenshtein 距离）（编辑距离与ASR评测的python实现代码：https://zhuanlan.zhihu.com/p/62910942）
"""
# Description of Changes :
"""
new:
    增加了如下三个函数，并兼容多个句子的对比总结果统计
    def single_sen_comp(str_ref, str_hyp)
    def get_result(sub_num, del_num, ins_num, n_num, sen_num, wrong_recog_num)
    def main()
    "打印对比的两个句子的具体详细修改位置"这段代码，优化：中文推进2个字符，英文（ASCII码在128以内）推进1个字符，这样三段文字就对齐了
"""
# Remarks :
"""    
"""

import numpy as np
import pandas as pd
# from collections import Counter
import time
import re

equal = lambda x, y: True if (x == y) else False


def get_edit_path(ptr_matrix):
    '''
    通过ptr操作记录的矩阵来还原编辑过程
    '''
    path = []
    start = ptr_matrix[ptr_matrix.shape[0] - 1, ptr_matrix.shape[1] - 1]
    while (isinstance(start, int) != True):
        path.append(start[0])
        start = ptr_matrix[start[1][0], start[1][1]]
    path.reverse()
    return path


def get_edit_distance(ref, hyp):
    '''
    hyp: 输入串
    ref: 原始字符串
    使用动态规划的方法实现编辑距离,
    insert、deletion、sub等错误描述的是由输入串到原始串的操作 比如 hyp: 'abbcd', ref: 'ac', 三个insert错误。
    '''
    len_ref = len(ref)
    len_hyp = len(hyp)

    # 矩阵的横轴为输入串，纵轴为原始串，矩阵用来保存当前的最优编辑距离是多少
    edit_matrix = np.zeros((len_ref + 1, len_hyp + 1), dtype=int)
    edit_matrix[0, :] = [i for i in range(len_hyp + 1)]
    edit_matrix[:, 0] = [i for i in range(len_ref + 1)]

    # 记录每一步的路径
    ptr_matrix = np.zeros((len_ref + 1, len_hyp + 1), dtype=tuple)
    # print("ptr_matrix after np.zeros: ", ptr_matrix)

    ptr_matrix[0, 1:] = [('insertion', (0, i - 1)) for i in range(1, len_hyp + 1)]
    # print("ptr_matrix  after ptr_matrix[0, 1:]: insertion", ptr_matrix)

    ptr_matrix[1:, 0] = [('deletion', (i - 1, 0)) for i in range(1, len_ref + 1)]
    # print("ptr_matrix  after : ptr_matrix[1:, 0] deletion", ptr_matrix)

    for i in range(1, edit_matrix.shape[0]):
        for j in range(1, edit_matrix.shape[1]):

            # 是否有替换错误
            is_equal = equal(ref[i - 1], hyp[j - 1])
            add_number = 0 if is_equal else 1
            sub = edit_matrix[i - 1, j - 1] + add_number  # 直接根据是否相同而判断是不是加1

            # 删除错误 (j 少了一个)
            deletion = edit_matrix[i - 1, j] + 1

            # 插入错误 (j 多插入了一个)
            insertion = edit_matrix[i, j - 1] + 1

            min_edit = min(sub, insertion, deletion)

            # 记录路径
            if (sub == min_edit):
                if (not is_equal):
                    ptr_matrix[i, j] = ('sub', (i - 1, j - 1))
                else:
                    ptr_matrix[i, j] = ('', (i - 1, j - 1))
            elif (deletion == min_edit):
                ptr_matrix[i, j] = ('deletion', (i - 1, j))
            elif (insertion == min_edit):
                ptr_matrix[i, j] = ('insertion', (i, j - 1))
            else:
                print('error')

            edit_matrix[i, j] = min_edit

    # print (ptr_matrix)
    # print (get_edit_path(ptr_matrix))
    return edit_matrix[len_ref, len_hyp], get_edit_path(ptr_matrix), edit_matrix


def show_sentences_comp(str_ref, str_hyp, paths):
    """根据paths：['', 'sub', 'insertion', '', 'deletion']得到两个句子的所有异同字符的位置"""

    i = 0
    j = 0
    str_ref_new = ""
    str_hyp_new = ""
    str_renew = ""
    for path in paths:
        if path == "":
            str_renew += "."
            str_ref_new += str_ref[i]
            str_hyp_new += str_hyp[j]

            if ord(str_ref[i]) <= 128:
                # if ord(str_hyp[j]) <= 128:
                #     pass
                if ord(str_hyp[j]) > 128:
                    str_renew += "."
                    str_ref_new += "."
            elif ord(str_hyp[j]) <= 128:
                str_renew += "."
                str_hyp_new += "."
            elif ord(str_hyp[j]) > 128:
                str_renew += "."

            i += 1
            j += 1
        elif path == 'sub':
            str_renew += "S"
            str_ref_new += str_ref[i]
            str_hyp_new += str_hyp[j]

            if ord(str_ref[i]) <= 128:
                # if ord(str_hyp[j]) <= 128:
                #     pass
                if ord(str_hyp[j]) > 128:
                    str_renew += "."
                    str_ref_new += "."
            elif ord(str_hyp[j]) <= 128:
                str_renew += "."
                str_hyp_new += "."
            elif ord(str_hyp[j]) > 128:
                str_renew += "."

            i += 1
            j += 1

        elif path == 'deletion':
            str_renew += "D"
            str_ref_new += str_ref[i]
            str_hyp_new += "*"  # str_hyp[j]

            if ord(str_ref[i]) > 128:
                str_renew += "."
                str_hyp_new += "."

            i += 1
            # j += 1

        elif path == 'insertion':
            str_renew += "I"
            str_ref_new += "*"  # str_ref[i]
            str_hyp_new += str_hyp[j]

            if ord(str_hyp[j]) > 128:
                str_renew += "."
                str_ref_new += "."

            # i += 1
            j += 1
        else:
            print("path有误: {}".format(path))

    print("ref: " + str_ref_new)
    print("hyp: " + str_hyp_new)
    print("     " + str_renew)
    print()


def single_sen_comp(str_ref, str_hyp):
    """两个句子的比对"""

    ttt = get_edit_distance(str_ref, str_hyp)
    # edit_distance = ttt[0]
    paths = ttt[1]
    # print('edit distance:', edit_distance)
    print('\npaths: ', paths)
    # print(pd.DataFrame(ttt[2], columns = [i for i in '#' + str_hyp], index = [i for i in '#' + str_ref]))

    # show_sentences_comp(str_ref, str_hyp, paths) # 打印

    # 结果的处理
    s_d_i = pd.value_counts(paths)
    dict_s_d_i = dict(s_d_i)
    # print("dict(dict_s_d_i):",dict(dict_s_d_i))

    sub_num = dict_s_d_i.get("sub", 0)
    del_num = dict_s_d_i.get("deletion", 0)
    ins_num = dict_s_d_i.get("insertion", 0)
    n_num = len(str_ref)
    # h_num = n_num - sub_num - del_num

    wrong_recog_num = 0
    if sub_num + del_num + ins_num:
        wrong_recog_num = 1

    return wrong_recog_num, sub_num, del_num, ins_num, n_num, paths


def get_result(sub_num, del_num, ins_num, n_num, sen_num, wrong_recog_num):
    """计算最终观测指标值"""

    # sen_num = 1  # 句子总数（这个要根据实际情况获取）
    # wrong_recog_num = 0  # 识别错误的句子总数（一个句子只要有S/D/I任何一个错误就算错）
    ser = float(wrong_recog_num) / float(sen_num)  # 句子错误率（带错误的句子数/总句子数）
    s_corr = 1 - ser  #

    wer = float(sub_num + del_num + ins_num) / float(n_num)  # 字错率（带错误的单词数/总字数）
    cer = float(sub_num + del_num + ins_num) / float(n_num)  # 字符错率（带错误的单词数/总字数）
    w_acc = 1 - wer  # 字准确率（这个统计了插入的）

    w_corr = float(n_num - (sub_num + del_num)) / float(n_num)  # 字正确率（不包括插入的）

    sub_er = float(sub_num) / float(n_num)
    del_er = float(del_num) / float(n_num)
    ins_er = float(ins_num) / float(n_num)

    str1 = "{:<18}{:<10d}\t {:<18}{:<10d}\t {:<18}{:<10d}\t {:<18}{:<10d}".format("sub_num:", sub_num, "del_num:",
                                                                                  del_num, "ins_num:", ins_num,
                                                                                  "n_num:", n_num)
    str2 = "{:<18}{:<10,.2%}\t {:<18}{:<10.2%}\t {:<18}{:<10.2%}".format("sub_er:", sub_er, "del_er:", del_er,
                                                                         "ins_er:", ins_er)
    str3 = "{:<18}{:<10,.2%}\t {:<18}{:<10.2%}\t {:<18}{:<10.2%}\t {:<18}{:<10.2%}".format("wer:", wer, "cer:", cer,
                                                                                           "w_acc:", w_acc, "w_corr:",
                                                                                           w_corr)
    str4 = "{:<18}{:<10d}\t {:<18}{:<10d}\t {:<18}{:<10.2%}".format("sen_num:", sen_num, "wrong_recog_num:",
                                                                      wrong_recog_num, "s_corr:", s_corr)
    print("----------------比对结果如下：----------------")
    print(str1)
    print(str2)
    print(str3)
    print(str4)


def read_txt(file_name):
    """读取两个文本，容错空行，以ref文本为依据（寻找是否hyp文本都有对应句子（句子末尾有方括号的！方括号里面的文本（截取前面一部分？）当做名字，多个重复的也报错），不全就报错！）"""

    pat1 = re.compile("[(（]([\d\D]*?)[)）]") # 可以优化一下，左边是中文"（"，右边也只能是中文“）”
    dict_sentence = {}
    try:
        fo = open(file_name,"r",encoding="utf-8")
    except Exception as e:
        print(e)
        fo = open(file_name,"r",encoding="gbk")

    error_set_replicate = set()
    for line in fo:
        if line.strip() == "":
            pass
        else:
            match_list = re.finditer(pat1,line)
            sentence_name,span = "",(0,0)
            for match in match_list: # 只要最后一个匹配项，考虑没有匹配到的情况
                sentence_name,span = match.group(1), match.span()
            if sentence_name != "": # 匹配到
                if line[span[1]:].rstrip() == "": # 匹配到，而且（匹配到取【1】不会报错）右边是空字符的情况，就算真的是的
                    sentence_content = line[:span[0]]
                    if dict_sentence.get(sentence_name,"have_replicated") != "have_replicated":
                        # print("重复了！只取到第一个！请确认此条文本：", sentence_name)
                        error_set_replicate.add(sentence_name)
                        continue
                    sentence_name = sentence_name.rsplit(".",1)[0]
                    # print(sentence_name)
                    dict_sentence[sentence_name] = sentence_content
                else:
                    print("匹配到，但是（）不在末尾，忽略此句子")
            else:
                print("没有匹配到句子名！忽略此句子")
    fo.close()

    print(dict_sentence)
    print("【警告！！】这些句子名称重复出现！只取到第一个！请确认这些句子：",error_set_replicate)
    return dict_sentence


def main():
    st = time.time()

    sen_num = 0 # 句子数
    total_wrong_recog_num = 0 # 判断有误的句子数
    total_sub_num, total_del_num, total_ins_num, total_n_num = 0, 0, 0, 0 # 装最后总的错误数（分类别）

    filename_ref = "ref.txt"
    filename_hyp = "hyp.txt"

    #
    print("dict_sentence_ref: ",end="")
    dict_sentence_ref = read_txt(filename_ref)
    print("dict_sentence_hyp: ", end="")
    dict_sentence_hyp = read_txt(filename_hyp)

    # 找出两个字典公共的key，然后遍历就可以得到一一对应的两个句子了
    keys_ref = set((x for x in dict_sentence_ref.keys()))
    keys_hyp = set((x for x in dict_sentence_hyp.keys()))
    public_keys = keys_ref.intersection(keys_hyp)
    missed_keys = keys_ref.difference(keys_hyp)
    print("\n【警告！！】这些句子没有对应的识别文本：", missed_keys)

    for key in public_keys:
        # 遍历所有句子【这一段代码可以根据实际情况而改写，比如从两个文本（特定格式）中读取若干对句子，一一比对】，将sub_num, del_num, ins_num, n_num等累加，遍历完后输出一个总的指标值
        # str_ref = "今天天气非常的不错"
        # str_hyp = "今天天气嗯嗯非常不措"
        # str_ref = "今天天气啊嗯非常不措"
        # str_hyp = "今天天气，嗯嗯。非常不措！"
        # str_ref = "B3A9C-FA962-3866D-中国CD7EF-49FC9$17061b42e6c83b099ab22d5311a76c1a"
        # str_hyp = "B}A9C-FJ}9}2一38C6D一CD7EF-}9FC9$17}}中国1b}2e6c8}b}99ab22d5# }11a76c1a/#CE1}O,EXE"

        str_ref = dict_sentence_ref[key]
        str_hyp = dict_sentence_hyp[key]
        # print("str_ref: ",str_ref)
        # print("str_hyp: ",str_hyp)

        wrong_recog_num, sub_num, del_num, ins_num, n_num, paths = single_sen_comp(str_ref, str_hyp)
        show_sentences_comp(str_ref, str_hyp, paths)  # 根据paths：['', 'sub', 'insertion', '', 'deletion']得到两个句子的所有异同字符的位置

        total_sub_num += sub_num
        total_del_num += del_num
        total_ins_num += ins_num
        total_n_num += n_num
        total_wrong_recog_num += wrong_recog_num
        sen_num += 1

    if total_n_num != 0: # 考虑到比对句子为空的情况
        get_result(total_sub_num, total_del_num, total_ins_num, total_n_num, sen_num, total_wrong_recog_num)
    else:
        print("【警告！！】比对句子为空，请确认！")

    print("time consumed: {:,.8f} s".format(time.time() - st))


if __name__ == "__main__":
    main()
