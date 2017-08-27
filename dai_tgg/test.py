# -*- coding: utf-8 -*-
import re
tuan_bao_duong_char  ='a b.s'
tuan_bao_duong_char = re.sub('\.|\s', '', tuan_bao_duong_char,0, re.I)
print tuan_bao_duong_char
# 
# a=  '''access_dai_tgg_trucca    dai_tgg.trucca    model_trucca    base.group_user    1    1    1    1
# access_dai_tgg_res_users    dai_tgg.res.users    model_res_users    base.group_user    1    1    1    1
# access_dai_tgg_sukien    dai_tgg.sukien    model_sukien    base.group_user    1    1    1    1
# access_dai_tgg_tram    dai_tgg.tram    model_tram    base.group_user    1    1    1    1
# access_dai_tgg_tuyen_cap    dai_tgg.tuyen_cap    model_tuyen_cap    base.group_user    1    1    1    1
# access_dai_tgg_huong    dai_tgg.huong    model_huong    base.group_user    1    1    1    1
# access_dai_tgg_port_thiet_bi    dai_tgg.port.thiet_bi    model_port_thiet_bi    base.group_user    1    1    1    1
# access_dai_tgg_huong    dai_tgg.huong    model_huong    base.group_user    1    1    1    1
# access_dai_tgg_padp    dai_tgg.padp    model_padp    base.group_user    1    1    1    1
# access_dai_tgg_dai_tgg_soi    dai_tgg.dai_tgg.soi    model_dai_tgg_soi    base.group_user    1    1    1    1
# access_dai_tgg_comment    dai_tgg.comment    model_comment    base.group_user    1    1    1    1
# access_dai_tgg_ada    dai_tgg.ada    model_ada    base.group_user    1    1    1    1
# access_dai_tgg_líchsuchay    dai_tgg.líchsuchay    model_líchsuchay    base.group_user    1    1    1    1
# '''
# 
# rs =  re.sub('    ', ',', a)
# print rs