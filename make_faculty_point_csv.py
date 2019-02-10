import os
from make_point_db import PointDataReader, JsonPointData, RegionPointDataReader
from point import FacultyPoint
from tqdm import tqdm
from calc_isolation import MeshPointManager
from setting import RegionSetting
from calc_relation_point import CalcRelationPoint
import csv


def main():

    # データファイル（郵便局）
    # input_file = os.path.join("./input", "post_office.txt")
    # output_file = "./input/post_office_points.csv"
    # json_data_class = JsonPostOfficeData

    # データファイル（学校）
    input_file = os.path.join("./input", "elementary_schools.txt")
    output_file = "./input/elementary_school_points.csv"
    json_data_class = JsonSchoolData

    # 地域点データファイル
    region_point_input_file = os.path.join("./input", "japan_region.txt")

    # 施設データ読み込み
    ppd = FacultyPointDataReader(input_file, output_file, json_data_class, FacultyPoint)
    ppd.read_points()

    # 人口データ読み込み
    mpm = MeshPointManager()
    mpm.read_points(0, "zenkoku")

    # 施設データにそれが含まれる人口データを登録（なければ登録しない）
    ppd.register_in_pop_point(mpm.all_pop_points)

    # 地域点データ読み込み
    rpd = RegionPointDataReader(region_point_input_file)

    # 施設データに住所を登録
    ppd.register_address(rpd.region_points_by_segment)

    # 施設データに都会度を登録
    ppd.register_relation_point_default(mpm.all_pop_points)

    # csv吐き出し
    ppd.register_points_to_csv()


class FacultyPointDataReader(PointDataReader):

    def __init__(self, input_file, output_file, json_data_class, point_data_class):
        super().__init__(input_file)
        self.post_office_points = []
        self.output_file = output_file
        self.json_data_class = json_data_class
        self.point_data_class = point_data_class

        self.post_office_points_by_calc_segment = {}
        for calc_segment in RegionSetting.get_calc_segments():
            self.post_office_points_by_calc_segment[calc_segment] = []

    def read_points(self):

        print("施設データ読み込み中")
        for raw_data in tqdm(self.raw_data_set):
            p = self.point_data_class()
            data = self.json_data_class(raw_data)
            p.latitude = data.get_latitude()
            p.longitude = data.get_longitude()
            p.name = data.get_name()
            self.post_office_points.append(p)

    def register_in_pop_point(self, pop_points):
        """
        含まれている人口点を登録する
        ない場合はフラグを立てる
        :param pop_points:
        :return:
        """

        print("含まれている人口点を登録中")
        for post_point in tqdm(self.post_office_points):

            # 最寄りの候補となる点を探索する
            candidates = []
            for pop_point in pop_points:
                if post_point.get_may_be_in_mesh(pop_point):
                    candidates.append(pop_point)

            if len(candidates) == 0:
                post_point.is_in_pop_point = False
                continue
            else:
                post_point.is_in_pop_point = True

            # 候補点から最寄りの点を探す
            min_dist = 0
            in_pop_point = None
            for i, candidate in enumerate(candidates):
                dist = post_point.get_distance(candidate)
                if i == 0:
                    min_dist = dist
                    in_pop_point = candidate
                    continue
                if dist < min_dist:
                    min_dist = dist
                    in_pop_point = candidate
            post_point.set_in_pop_point(in_pop_point)

    def register_address(self, region_points_by_segment):
        print("住所を登録中")
        for post_point in tqdm(self.post_office_points):
            min_dist = 0
            nearest_region_point = None
            segment = RegionSetting.get_address_calc_segment_by_lat_lon(post_point.latitude, post_point.longitude)
            for i, region_point in enumerate(region_points_by_segment[segment]):
                dist = post_point.get_distance(region_point)
                if i == 0:
                    min_dist = dist
                    nearest_region_point = region_point
                    continue
                if dist < min_dist:
                    min_dist = dist
                    nearest_region_point = region_point
            post_point.pref = nearest_region_point.pref
            post_point.city = nearest_region_point.city
            post_point.district = nearest_region_point.district

            # 計算地域別のポイントリストを生成
            calc_segment = RegionSetting.get_calc_segment_by_pref(post_point.pref)
            self.post_office_points_by_calc_segment[calc_segment].append(post_point)

    def register_relation_point_default(self, all_pop_points):

        print("都会度を登録中")
        for post_point in tqdm(self.post_office_points):

            if post_point.in_pop_point is not None:
                post_point.relation_point_default = post_point.in_pop_point.relation_point_default
            else:
                # メッシュに含まれていない場合は、都会度を計算する
                calc_segment = RegionSetting.get_calc_segment_by_pref(post_point.get_pref())
                for pop_point in all_pop_points:
                    pop_point_calc_segment = RegionSetting.get_calc_segment_by_pref(pop_point.pref)
                    if calc_segment != pop_point_calc_segment:
                        continue
                    dist = post_point.get_distance(pop_point)
                    post_point.relation_point_default \
                        += CalcRelationPoint.get_relation_point_default(pop_point.population, dist)

    def register_points_to_csv(self):
        with open(self.output_file, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            header = [
                "name",
                "pref",
                "city",
                "district",
                "latitude",
                "longitude",
                "relation_point_default"
            ]
            writer.writerow(header)
            for p in self.post_office_points:
                row = [
                    p.name,
                    p.pref,
                    p.city,
                    p.district,
                    p.latitude,
                    p.longitude,
                    p.relation_point_default
                ]
                writer.writerow(row)


class JsonPostOfficeData(JsonPointData):

    def get_name(self):
        name = self.data["properties"]["P30_005"]
        return name


class JsonSchoolData(JsonPointData):

    def get_name(self):
        name = self.data["properties"]["P29_005"]
        return name


if __name__ == "__main__":
    main()
