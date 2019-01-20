from param_default import *


class CalcRelationPoint(object):
    """
    集落の連帯度を計算するクラス
    """

    # def __init__(self, setting):
    #     self.pop_param = setting.pop_param
    #     self.dist_param = setting.dist_param
        # self.dist_threshold = setting.distance_threshold

    # def get_relation_point(self, v, points):
    #     relation_point = 0
    #     for p in points:
    #         if p in v.points:
    #             continue
    #         dist = v.get_point_distance(p)
    #         # if dist > self.dist_threshold or dist == 0:
    #         if dist == 0:
    #             continue
    #         pop = p.population
    #         relation_point += (pop**self.pop_param) / (dist**self.dist_param)
    #     return relation_point

    @staticmethod
    def get_relation_point_default(pop, dist):
        try:
            return (pop ** POP_PARAM) / (dist ** DIST_PARAM)
        except ZeroDivisionError:
            print("ZeroDivisionError")
            return 0
