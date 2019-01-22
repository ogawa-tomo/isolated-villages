import psycopg2
from point import MeshPoint
from setting import RegionSetting
from tqdm import tqdm
import csv


class PointDAO(object):

    def __init__(self):
        self.conn_db = "dbname=village_db user=village_admin password = sukasuka"
        self.pop_table = "pop_points"
        self.pop_data_csv = "./input/pop_points.csv"

    def create_table(self):
        conn = self.connect_db()
        cur = conn.cursor()
        query = "".join([
            "create table ",
            self.pop_table,
            " (id integer PRIMARY KEY, key text, neighbors text, ",
            "pref text, city text, district text, population integer, ",
            "latitude double precision, longitude double precision, ",
            "coast boolean, coast_distance double precision, relation_point_default double precision);"
        ])
        cur.execute(query)
        self.close_connect(conn)

    def connect_db(self):
        conn = psycopg2.connect(self.conn_db)
        return conn

    @staticmethod
    def close_connect(conn):
        conn.commit()
        conn.close()

    def register_point(self, conn, p):
        """
        点をDBに登録する
        :param conn:
        :param p:
        :return:
        """
        cur = conn.cursor()
        query = "".join([
            "insert into ",
            self.pop_table,
            " (id,",
            " key,",
            " neighbors,",
            " pref,",
            " city,",
            " district,",
            " population,",
            " latitude,",
            " longitude,",
            " coast,",
            " coast_distance,",
            " relation_point_default)",
            " values (",
            str(p.id), ", ",
            p.key_code, ", ",
            "\'", p.neighbor_ids, "\', ",
            "\'", p.pref, "\', ",
            "\'", p.city, "\', ",
            "\'", p.district, "\', ",
            str(p.population), ", ",
            str(p.latitude), ", ",
            str(p.longitude), ", ",
            str(p.coast), ", ",
            str(p.coast_distance), ", ",
            str(p.relation_point_default),
            ");"
        ])
        cur.execute(query)

    def read_pop_points_from_db(self, point_pop_lower_limit, region):
        """
        all_pop_pointsは地域関係なくすべて
        calc_segment_pop_pointsは計算セグメントのポイント
        village_pointsは該当地域かつ人口閾値以上のポイント
        :param point_pop_lower_limit:
        :param region:
        :return:
        """

        conn = self.connect_db()
        cur = conn.cursor()
        query = "select * from " + self.pop_table + " order by id;"
        cur.execute(query)

        # データごとのインデックスを取得
        key_idx = -1
        neighbor_ids_idx = -1
        pref_idx = -1
        city_idx = -1
        district_idx = -1
        pop_idx = -1
        lat_idx = -1
        lon_idx = -1
        coast_idx = -1
        coast_distance_idx = -1
        relation_point_idx = -1
        descriptions = cur.description
        for i, d in enumerate(descriptions):
            if d.name == "key":
                key_idx = i
            elif d.name == "neighbors":
                neighbor_ids_idx = i
            elif d.name == "pref":
                pref_idx = i
            elif d.name == "city":
                city_idx = i
            elif d.name == "district":
                district_idx = i
            elif d.name == "population":
                pop_idx = i
            elif d.name == "latitude":
                lat_idx = i
            elif d.name == "longitude":
                lon_idx = i
            elif d.name == "coast":
                coast_idx = i
            elif d.name == "coast_distance":
                coast_distance_idx = i
            elif d.name == "relation_point_default":
                relation_point_idx = i

        # 1行ずつMeshPointを生成しリストに格納
        all_pop_points = []
        calc_segment_pop_points = []
        village_points = []
        calc_segment_prefs = RegionSetting.get_calc_segment_prefs_by_region(region)
        region_prefs = RegionSetting.get_region_prefs(region)

        for row in tqdm(cur):
            p = MeshPoint()
            p.key_code = row[key_idx]
            if row[neighbor_ids_idx] != "":
                p.neighbor_ids = [int(i) for i in row[neighbor_ids_idx].split("-")]
            else:
                p.neighbor_ids = []
            p.pref = row[pref_idx]
            p.city = row[city_idx]
            p.district = row[district_idx]
            p.population = row[pop_idx]
            p.latitude = row[lat_idx]
            p.longitude = row[lon_idx]
            p.coast = row[coast_idx]
            p.coast_distance = row[coast_distance_idx]
            p.relation_point_default = row[relation_point_idx]

            # 条件に応じてリストに登録
            all_pop_points.append(p)
            if p.pref in calc_segment_prefs:
                calc_segment_pop_points.append(p)
            if p.pref in region_prefs and p.population >= point_pop_lower_limit:
                village_points.append(p)

        read_points = {
            "all": all_pop_points,
            "calc_segment": calc_segment_pop_points,
            "village": village_points
        }

        self.close_connect(conn)

        return read_points

    def make_point_data_csv(self):

        conn = self.connect_db()
        cur = conn.cursor()
        query = "select * from " + self.pop_table + " order by id;"
        cur.execute(query)

        descriptions = cur.description

        with open(self.pop_data_csv, "w", encoding="utf8") as f:
            writer = csv.writer(f, lineterminator="\n")

            # ヘッダ
            header = [d.name for d in descriptions]
            writer.writerow(header)

            # データ
            for row in tqdm(cur):
                writer.writerow(row)

        self.close_connect(conn)

    def read_pop_points_from_csv(self, point_pop_lower_limit, region):
        """
        all_pop_pointsは地域関係なくすべて
        calc_segment_pop_pointsは計算セグメントのポイント
        village_pointsは該当地域かつ人口閾値以上のポイント
        :param point_pop_lower_limit:
        :param region:
        :return:
        """

        # 作るデータを定義
        all_pop_points = []
        calc_segment_pop_points = []
        village_points = []
        calc_segment_prefs = RegionSetting.get_calc_segment_prefs_by_region(region)
        region_prefs = RegionSetting.get_region_prefs(region)

        # データごとのインデックスを定義
        key_idx = -1
        neighbor_ids_idx = -1
        pref_idx = -1
        city_idx = -1
        district_idx = -1
        pop_idx = -1
        lat_idx = -1
        lon_idx = -1
        coast_idx = -1
        coast_distance_idx = -1
        relation_point_idx = -1

        with open(self.pop_data_csv, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for i, line in enumerate(reader):

                if i == 0:
                    # インデックスを取得
                    for j, d in enumerate(line):
                        if d == "key":
                            key_idx = j
                        elif d == "neighbors":
                            neighbor_ids_idx = j
                        elif d == "pref":
                            pref_idx = j
                        elif d == "city":
                            city_idx = j
                        elif d == "district":
                            district_idx = j
                        elif d == "population":
                            pop_idx = j
                        elif d == "latitude":
                            lat_idx = j
                        elif d == "longitude":
                            lon_idx = j
                        elif d == "coast":
                            coast_idx = j
                        elif d == "coast_distance":
                            coast_distance_idx = j
                        elif d == "relation_point_default":
                            relation_point_idx = j
                    continue

                # MeshPointを作る
                p = MeshPoint()
                p.key_code = line[key_idx]
                if line[neighbor_ids_idx] != "":
                    p.neighbor_ids = [int(k) for k in line[neighbor_ids_idx].split("-")]
                else:
                    p.neighbor_ids = []
                p.pref = line[pref_idx]
                p.city = line[city_idx]
                p.district = line[district_idx]
                p.population = int(line[pop_idx])
                p.latitude = float(line[lat_idx])
                p.longitude = float(line[lon_idx])
                if line[coast_idx] == "True":
                    p.coast = True
                else:
                    p.coast = False
                p.coast_distance = float(line[coast_distance_idx])
                p.relation_point_default = float(line[relation_point_idx])

                # 条件に応じてリストに登録
                all_pop_points.append(p)
                if p.pref in calc_segment_prefs:
                    calc_segment_pop_points.append(p)
                if p.pref in region_prefs and p.population >= point_pop_lower_limit:
                    village_points.append(p)

        read_points = {
            "all": all_pop_points,
            "calc_segment": calc_segment_pop_points,
            "village": village_points
        }

        return read_points
