# -*- coding: utf-8 -*-

l =  [(1L, None), (3, 53), (5, 52), (2, 49), (20, 1), (7, 50), (20, 47), (2, 51)]
print reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,l,[] )