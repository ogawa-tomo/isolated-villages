import math


class Point(object):
    def __init__(self):
        self.key_code = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.pref = ""
        self.city = ""
        self.district = ""
        self.len_district = 0

    def get_distance(self, p):
        """
        自分とpの距離を調べる関数
        :param p:
        :return: 距離km
        """
        return get_distance(self.longitude, self.latitude, p.longitude, p.latitude)

    def get_google_map_url(self):
        lat = str(self.latitude)
        lon = str(self.longitude)
        url = "http://maps.google.com/maps?q=" + lat + "," + lon + "&t=k"
        return url

    def __repr__(self):
        return self.key_code


class FacultyPoint(Point):

    def __init__(self):
        super().__init__()
        self.name = ""
        self.in_pop_point = None
        self.is_in_pop_point = True
        self.relation_point_default = 0

    def get_name(self):
        return self.name

    def get_pref(self):
        return self.pref

    def get_city(self):
        return self.city

    def get_district(self):
        return self.district

    def set_len_district(self):
        self.len_district = len(self.district)

    def get_may_be_in_mesh(self, mesh_point):

        # 緯度経度の差だけで判断
        dx = abs(self.longitude - mesh_point.longitude)
        dy = abs(self.latitude - mesh_point.latitude)
        if dx < 0.009 and dy < 0.006:
            return True
        else:
            return False

    def set_in_pop_point(self, pop_point):
        self.in_pop_point = pop_point

    def __lt__(self, other):
        return self.relation_point_default < other.relation_point_default


class RegionPoint(Point):

    def get_pref(self):
        return self.pref

    def get_city(self):
        return self.city

    def get_district(self):
        return self.district

    def set_len_district(self):
        self.len_district = len(self.district)


class MeshPoint(Point):
    """
    人口メッシュポイントデータクラス
    """

    def __init__(self):
        super().__init__()
        self.id = 0
        self.population = 0
        self.coast = False
        self.neighbors = []
        self.neighbor_ids = ""
        self.coast_distance = 0
        self.relation_point_default = 0

    # def add_neighbor(self, p):
    #     self.neighbors.append(p)

    # def add_village_neighbor(self, p):
    #     self.village_neighbors.append(p)

    def add_neighbor_id(self, p_id):
        if self.neighbor_ids == "":
            self.neighbor_ids = str(p_id)
        else:
            self.neighbor_ids += "-" + str(p_id)

    def get_is_adjacent(self, p):
        """
        自分とpが隣接しているかを調べる関数
        :param p:
        :return:
        """
        # 緯度経度の差だけで判断
        dx = abs(self.longitude - p.longitude)
        dy = abs(self.latitude - p.latitude)
        if dx < 0.018 and dy < 0.012:
            return True
        else:
            return False

    def get_my_village_points(self, ignore_org, village_size_upper_limit, point_pop_lower_limit):
        """
        自分に隣接する、人口閾値以上のポイントを返す関数
        :param ignore_org:
        :param size_limit
        :param point_pop_lower_limit
        :return:
        """

        ignore = ignore_org.copy()
        ignore.append(self)
        if len(ignore) > village_size_upper_limit:
            # raise TooBigVillageException(ignore)
            return {"is_village": False, "points": ignore}  # 集落ではないことを示し、そのポイントの集合を返す
        my_village_points = [self]
        for p in self.neighbors:
            if p in ignore or p.population < point_pop_lower_limit:
                continue
            my_village_points.append(p)
            # try:
            #     points = p.get_my_village_points(ignore, village_size_upper_limit, point_pop_lower_limit)  # 再帰的に呼ぶ
            # except TooBigVillageException:
            #     # サイズの閾値を超えると例外が返ってくる
            #     raise TooBigVillageException
            points = p.get_my_village_points(ignore, village_size_upper_limit, point_pop_lower_limit)  # 再帰的に呼ぶ

            if not points["is_village"]:
                return points

            ignore.extend(points["points"])
            my_village_points.extend(points["points"])
            my_village_points = list(set(my_village_points))

        return {"is_village": True, "points": my_village_points}


def get_distance(x1, y1, x2, y2):
    """
    日本周辺の緯度経度からの距離（km）
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    dx = abs(x1 - x2) * 91
    dy = abs(y1 - y2) * 111
    dist = math.sqrt(dx ** 2 + dy ** 2)
    return dist


class TooBigVillageException(Exception):
    pass
