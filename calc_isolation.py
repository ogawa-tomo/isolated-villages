import csv
from tqdm import tqdm
import folium
from point_dao import PointDAO
from point import *
from calc_relation_point import CalcRelationPoint
import os
import time
import shutil
import glob


def main(s):

    # hogehoge

    # 人口メッシュデータをDBから読み込み
    mpm = MeshPointManager()
    mpm.read_points(s.point_pop_lower_limit, s.region)

    # 隣接点を登録
    mpm.register_neighbors()

    # 集落の抽出
    villages = extract_villages(
        mpm.village_points,
        s.point_pop_lower_limit,
        s.village_size_upper_limit,
        s.village_pop_lower_limit,
        # s.coast_distance_threshold
    )

    # 集落の孤立度を計算
    crp = CalcRelationPoint()
    calc_relation_point(villages, crp)

    # 孤立度が高い順にソート
    sorted_villages = sorted(villages)

    # 結果書き出し
    t = str(time.time()).replace(".", "")
    csv_files = glob.glob("./static/*.csv")
    html_files = glob.glob("./static/*.html")
    files = csv_files.extend(html_files)
    if files is not None:
        for file in files:
            os.remove(file)
    dirs = glob.glob("./static/*")
    remove_dir_n = len(dirs) - 5
    remove_dirs = dirs[:remove_dir_n]
    for directory in remove_dirs:
        shutil.rmtree(directory)
    output_dir = "./static/" + t + "/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = output_dir + s.region
    output_result = OutputResult(output_file, sorted_villages, s)
    output_result.output_csv()
    output_result.output_map()

    return output_result


def extract_villages(
        village_points,
        point_pop_lower_limit,
        village_size_upper_limit,
        village_pop_lower_limit,
        # coast_distance_threshold
):
    """
    ポイント集合から集落を抽出して返すメソッド
    :param village_points:
    :param point_pop_lower_limit:
    :param village_size_upper_limit:
    :param village_pop_lower_limit:
    :param coast_distance_threshold:
    :return:
    """
    registered = []  # 既に集落に登録された点
    villages = []
    print("集落を抽出中")
    for p in tqdm(village_points):
        if p in registered:
            continue

        # p周辺の人口集中ポイントを登録
        try:
            village_points = p.get_my_village_points([], village_size_upper_limit, point_pop_lower_limit)
        except TooBigVillageException:
            # サイズが閾値を超えた場合には例外が返ってくる
            continue

        registered.extend(village_points)

        v = Village(village_points)

        # 人口などの条件を満たしていればリストに登録
        if village_pop_lower_limit <= v.population:  # and \
                # v.coast_distance >= coast_distance_threshold:
            villages.append(v)
    return villages


def calc_relation_point(villages, crp):
    print("集落の孤立度を計算中")
    for v in tqdm(villages):
        cp = v.center_point
        v_points = v.points.copy()
        v_points.remove(cp)
        v_relation_point = cp.relation_point_default
        for p in v_points:
            dist = cp.get_distance(p)
            pop = p.population
            rp = crp.get_relation_point_default(pop, dist)
            v_relation_point -= rp
        v.set_relation_point(v_relation_point)


class MeshPointManager(object):
    """
    人口点データを読み込み管理するクラス
    """

    def __init__(self):

        self.all_pop_points = []
        # self.calc_segment_pop_points = []
        self.village_points = []

    def read_points(self, point_pop_lower_limit, region):
        """
        all_pop_pointsとcalc_segment_pop_pointsとvillage_pointsに値を代入
        all_pop_pointsは地域関係なくすべて
        calc_segment_pop_pointsは計算セグメントのポイント
        village_pointsは該当地域かつ人口閾値以上のポイント
        :return:
        """

        dao = PointDAO()
        print("DBから人口点を読み込み中")
        # read_points = dao.read_pop_points_from_db(point_pop_lower_limit, region)
        read_points = dao.read_pop_points_from_csv(point_pop_lower_limit, region)

        self.all_pop_points = read_points["all"]
        # self.calc_segment_pop_points = read_points["calc_segment"]
        self.village_points = read_points["village"]

    def register_neighbors(self):
        """
        隣接点をDBから登録
        :return:
        """

        print("隣接点を登録中")
        for p in tqdm(self.village_points):
            for n_id in p.neighbor_ids:
                n = self.all_pop_points[n_id]
                p.neighbors.append(n)


class Village(object):
    """
    集落クラス（ポイントの集合）
    """

    def __init__(self, mesh_points):
        self.points = mesh_points
        self.size = len(self.points)
        self.relation_point = 0
        self.relation_point_round = 0
        self.population = self.calc_pop()

        self.center_point = self.get_center_point()

        self.latitude = self.center_point.latitude
        self.longitude = self.center_point.longitude
        self.latitude_round = round(self.latitude, 4)
        self.longitude_round = round(self.longitude, 4)

        self.pref = self.center_point.pref
        self.city = self.center_point.city
        self.district = self.center_point.district
        self.len_district = len(self.district)

        self.coast = self.get_is_coast()
        self.coast_distance = 0
        self.coast_distance_round = 0
        self.set_coast_distance()

        self.google_map_url = self.get_google_map_url()

    def add_point(self, p):
        self.points.append(p)

    def add_points(self, v):
        self.points.extend(v)

    def calc_pop(self):
        population = 0
        for p in self.points:
            population += p.population
        return population

    def get_center_point(self):
        """
        最も人口の多いポイント
        :return:
        """
        max_pop = 0
        center_point = None
        for p in self.points:
            if p.population > max_pop:
                max_pop = p.population
                center_point = p
        return center_point

    def get_is_coast(self):
        for p in self.points:
            if p.coast:
                return True
        return False

    def set_coast_distance(self):
        """
        海岸点が含まれていれば0
        そうでなければ、中心点からの距離
        :return:
        """

        if self.get_is_coast():
            self.coast_distance = 0
            self.coast_distance_round = 0
        else:
            self.coast_distance = self.center_point.coast_distance
            self.coast_distance_round = round(self.coast_distance, 2)

    def __repr__(self):
        return str("relation_point = " + str(self.relation_point) +
                   ", population = " + str(self.population) +
                   ", points = " + str(self.points))

    def __lt__(self, other):
        return self.relation_point < other.relation_point

    def get_point_distance(self, point):
        """
        自身の中心点とポイントの距離を計算する関数
        :param point:
        :return:
        """
        return get_distance(self.longitude, self.latitude, point.longitude, point.latitude)

    def set_relation_point(self, relation_point):
        self.relation_point = relation_point
        self.relation_point_round = round(relation_point, 4)

    def get_google_map_url(self):
        lat = str(self.latitude_round)
        lon = str(self.longitude_round)
        url = "http://maps.google.com/maps?q=" + lat + "," + lon
        return url


class OutputResult(object):
    """
    結果出力を担当するクラス
    """
    def __init__(self, file, sorted_villages, setting):
        self.file = file
        self.sorted_villages = sorted_villages
        self.setting = setting
        self.region = setting.region
        self.csv_file = self.file + ".csv"
        self.map_file = self.file + "_map.html"
        self.csv_url = self.csv_file.strip(".")
        self.map_url = self.map_file.strip(".")

    def output_csv(self):
        """
        結果をcsvファイルに書き出す
        :return:
        """
        with open(self.csv_file, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            for k in self.setting.setting.keys():
                writer.writerow([k, self.setting.setting[k]])

            writer.writerow(["順位",
                             "都道府県",
                             "市町村",
                             "地区",
                             "緯度経度",
                             "人口",
                             "都会度",
                             "海岸距離",
                             "メッシュ数",
                             "メッシュKEY_CODE"])
            for i, v in enumerate(self.sorted_villages):
                row = [i + 1,
                       v.pref,
                       v.city,
                       v.district,
                       str(v.latitude) + ", " + str(v.longitude),
                       v.population,
                       v.relation_point,
                       v.coast_distance,
                       str(len(v.points))
                       ]
                row.extend(v.points)
                writer.writerow(row)

    def output_map(self):
        """
        地域の地図を出力するクラス
        :return:
        """
        lat_lon = self.get_lat_lon(self.sorted_villages)
        map_ = folium.Map(location=lat_lon, zoom_start=8)
        n = len(self.sorted_villages)
        for i in range(10):
            if i >= n:
                break
            marker = self.get_marker(self.sorted_villages[i], i + 1)
            marker.add_to(map_)
        file = self.map_file
        map_.save(file)

    @staticmethod
    def get_marker(v, rank):
        address = "".join([v.pref, v.city, v.district])
        name = "".join([str(rank), "位：", address])
        lat_lon = ", ".join([str(v.latitude_round), str(v.longitude_round)])
        popup = " ".join([name, lat_lon])
        marker = folium.Marker([v.latitude, v.longitude], popup=popup,
                               icon=folium.Icon(icon="home", prefix="fa"))
        return marker

    @staticmethod
    def get_lat_lon(sorted_villages):
        lat_list = []
        lon_list = []
        for v in sorted_villages:
            lat_list.append(v.latitude)
            lon_list.append(v.longitude)
        lat = (min(lat_list) + max(lat_list)) / 2
        lon = (min(lon_list) + max(lon_list)) / 2
        return [lat, lon]
