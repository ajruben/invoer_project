import random
import matplotlib.pyplot as plt
from SweepIntersectorLib.SweepIntersector import SweepIntersector

segList = []

# create some random segments
for i in range(50):
    vs = (random.uniform(-1,1),random.uniform(-1,1))
    ve = (random.uniform(-1,1),random.uniform(-1,1))
    segList.append( (vs,ve) )



# compute intersections
isector = SweepIntersector()
isecDic = isector.findIntersections(segList)
print(isecDic)

