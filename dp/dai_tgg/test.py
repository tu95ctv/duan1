# -*- coding: utf-8 -*-
import json
s = "{'a':2}"
d = json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
print d