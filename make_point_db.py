import os
import json
from point_dao import PointDAO
from tqdm import tqdm
from point import MeshPoint, RegionPoint
from setting import RegionSetting
from calc_relation_point import CalcRelationPoint


def main():

    # 読み込むデータファイルの定義
    # calc_segment = sys.argv[1]
    mesh_point_input_file = os.path.join("./input", "japan_mesh.txt")
    region_point_input_file = os.path.join("./input", "japan_region.txt")
    # mesh_point_input_file = os.path.join("./input", "honshu", "honshu.txt")
    # region_point_input_file = os.path.join("./input", "honshu", "honshu_region.txt")

    # 人口メッシュデータの読み込み
    mpd = MeshPointDataReader(mesh_point_input_file, "population")

    # 地域点データの読み込み
    rpd = RegionPointDataReader(region_point_input_file)

    # 住所データの登録
    mpd.register_address(rpd.region_points_by_segment)

    # 隣接点の登録
    mpd.register_neighbors()

    # 海岸からの距離の登録
    mpd.register_coast_distance()

    # 連帯度の登録
    mpd.register_relation_point_default()

    # DBへの登録
    mpd.register_points_to_db()


class PointDataReader(object):

    def __init__(self, file):
        self.file = file
        self.raw_data_set = self.get_raw_data_set()

    def get_raw_data_set(self):
        with open(self.file, "r", encoding="utf-8") as f:
            data = f.read()
        data = json.loads(data)
        data = data["features"]
        return data


class RegionPointDataReader(PointDataReader):

    def __init__(self, file):
        super().__init__(file)
        self.region_points_by_segment = {}
        self.read_points()

    def read_points(self):

        n = RegionSetting.get_address_calc_segment_list()
        for segment in n:
            self.region_points_by_segment[segment] = []

        print("地域点の読み込み中")
        for raw_data in tqdm(self.raw_data_set):
            data = JsonRegionPointData(raw_data)
            p = RegionPoint()
            p.key_code = data.get_key_code()
            p.latitude = data.get_latitude()
            p.longitude = data.get_longitude()
            p.pref = data.get_pref()
            p.city = data.get_city()
            p.district = data.get_district()

            # 緯度のセグメントごとに格納
            segment = RegionSetting.get_address_calc_segment_by_lat_lon(p.latitude, p.longitude)
            self.region_points_by_segment[segment].append(p)

        # test
        # for segment in RegionSetting.get_address_calc_segment_list():
        #     print(str(segment) + ": " + str(len(self.region_points_by_segment[segment])))


class MeshPointDataReader(PointDataReader):
    """
    jsonからすべてのポイントのデータを読み込み、DBに登録
    """

    def __init__(self, file, pop_column_name):
        super().__init__(file)
        self.pop_column_name = pop_column_name
        # self.point_pop_upper_limit = setting.point_pop_upper_limit
        # self.region = region
        # self.setting = setting
        self.pop_points = []
        self.coast_points = []

        self.pop_points_by_calc_segment = {}
        for calc_segment in RegionSetting.get_calc_segments():
            self.pop_points_by_calc_segment[calc_segment] = []

        self.read_points()

    def read_points(self):
        """
        点の読み込み（人口のある点と海岸点）
        :return:
        """

        print("人口点の読み込み中")
        i = 0
        for raw_data in tqdm(self.raw_data_set):
            """
            jsonデータから全ポイントデータのリストを生成
            """

            p = MeshPoint()

            data = JsonMeshPointData(raw_data, self.pop_column_name)
            p.population = data.get_population()
            p.key_code = data.get_key_code()
            p.latitude = data.get_latitude()
            p.longitude = data.get_longitude()
            p.coast = data.get_coast()

            if p.population > 0:
                p.id = i
                self.pop_points.append(p)
                i += 1
            if p.coast:
                self.coast_points.append(p)

    def register_address(self, region_points_by_segment):
        """
        住所を登録する
        :param region_points_by_segment:
        :return:
        """
        print("住所を登録中")
        for pop_point in tqdm(self.pop_points):
            min_dist = 0
            nearest_region_point = None
            segment = RegionSetting.get_address_calc_segment_by_lat_lon(pop_point.latitude, pop_point.longitude)
            for i, region_point in enumerate(region_points_by_segment[segment]):
                dist = pop_point.get_distance(region_point)
                if i == 0:
                    min_dist = dist
                    nearest_region_point = region_point
                    continue
                if dist < min_dist:
                    min_dist = dist
                    nearest_region_point = region_point
            pop_point.pref = nearest_region_point.pref
            pop_point.city = nearest_region_point.city
            pop_point.district = nearest_region_point.district

            # 計算地域別のポイントリストを生成
            calc_segment = RegionSetting.get_calc_segment_by_pref(pop_point.pref)
            self.pop_points_by_calc_segment[calc_segment].append(pop_point)

    def register_neighbors(self):
        """
        人口ポイントについて、隣接点を登録する
        :return:
        """

        for calc_segment in RegionSetting.get_calc_segments():
            print(calc_segment + "の隣接点を登録中")
            target_points = self.pop_points_by_calc_segment[calc_segment].copy()
            for p in tqdm(self.pop_points_by_calc_segment[calc_segment]):
                target_points.remove(p)
                for tp in target_points:
                    if p.get_is_adjacent(tp):
                        p.add_neighbor_id(tp.id)
                        tp.add_neighbor_id(p.id)

    def register_coast_distance(self):
        """
        海岸からの距離を登録する
        :return:
        """
        print("海岸からの距離を登録中")
        for p in tqdm(self.pop_points):
            if p.coast:
                p.coast_distance = 0
            else:
                min_dist = 0
                for i, cp in enumerate(self.coast_points):
                    dist = p.get_distance(cp)
                    if i == 0:
                        min_dist = dist
                        continue
                    if dist < min_dist:
                        min_dist = dist
                p.coast_distance = min_dist

    def register_relation_point_default(self):
        """
        連帯度を計算する
        :return:
        """
        for calc_segment in RegionSetting.get_calc_segments():
            print(calc_segment + "の連帯度を計算中")
            target_points = self.pop_points_by_calc_segment[calc_segment].copy()
            for p in tqdm(self.pop_points_by_calc_segment[calc_segment]):
                target_points.remove(p)
                for tp in target_points:
                    # 連帯度を相互に計算する
                    dist = p.get_distance(tp)
                    p.relation_point_default += CalcRelationPoint.get_relation_point_default(tp.population, dist)
                    tp.relation_point_default += CalcRelationPoint.get_relation_point_default(p.population, dist)

    def register_points_to_db(self):
        """
        ポイントをDBに登録する
        :return:
        """

        dao = PointDAO()
        dao.create_table()
        conn = dao.connect_db()

        print("ポイントをDBに登録中")
        for p in tqdm(self.pop_points):
            dao.register_point(conn, p)

        dao.close_connect(conn)


class JsonPointData(object):
    """
    geojson形式のポイントデータを保持し、値を取り出すメソッドを提供するクラス
    """

    def __init__(self, data):
        self.data = data

    def get_key_code(self):
        key_code = self.data["properties"]["KEY_CODE"]
        return key_code

    def get_latitude(self):
        latitude = self.data["geometry"]["coordinates"][1]
        return latitude

    def get_longitude(self):
        longitude = self.data["geometry"]["coordinates"][0]
        return longitude


class JsonRegionPointData(JsonPointData):
    """
    geojson形式の小地域ポイントデータを保持するクラス
    """

    def get_pref(self):
        pref = self.read_data(self.data["properties"]["PREF_NAME"])
        return pref

    def get_city(self):
        city = self.read_data(self.data["properties"]["CITY_NAME"])
        return city

    def get_district(self):
        district = self.read_data(self.data["properties"]["S_NAME"])
        return district

    @staticmethod
    def read_data(data):
        if data is None:
            return ""
        else:
            return data


class JsonMeshPointData(JsonPointData):
    """
    geojson形式のメッシュポイントデータを保持するクラス
    """
    def __init__(self, data, pop_column_name):
        super().__init__(data)
        self.pop_column_name = pop_column_name

    def get_population(self):
        pop = self.data["properties"][self.pop_column_name]
        if type(pop) is not int:
            population = 0
        else:
            population = int(pop)
        return population

    def get_coast(self):
        coast = self.data["properties"]["coast"]
        if type(coast) is not int:
            return False
        elif int(coast) == 1:
            return True
        else:
            raise Exception("海岸データが不正です")


if __name__ == "__main__":
    main()
