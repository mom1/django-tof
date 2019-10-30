# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 13:47:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-30 13:48:05


def create_dict_from_line(name, value, **kwargs):
    dic = kwargs
    name, splitter, last_key = name.replace('\\', '').rpartition('__')
    for key in name.split('__'):
        dic = dic.setdefault(key, {})
    dic.setdefault(last_key, value)
    return kwargs
