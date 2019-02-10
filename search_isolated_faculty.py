import csv
from point import FacultyPoint
from setting import RegionSetting


def main(region, faculty):

    # region = "zenkoku"

    # input_file = "./input/post_office_points.csv"
    # input_file = "./input/elementary_school_points.csv"
    input_file = "./input/" + faculty + "_points.csv"

    # output_file_without_region = "./output/post_office_"
    # output_file_without_region = "./output/elementary_school_"
    output_file_without_region = "./output/" + faculty + "_"

    read_points = read_post_office_point_csv(input_file, region)

    region_post_points = read_points[region]

    sorted_post_points = sorted(region_post_points)

    # output_csv(sorted_post_points, region, output_file_without_region)

    return sorted_post_points


def read_post_office_point_csv(input_file, region):

    # 作るデータを定義
    all_post_points = []
    region_post_points = []
    region_prefs = RegionSetting.get_region_prefs(region)

    # データごとのインデックスを定義
    name_idx = -1
    pref_idx = -1
    city_idx = -1
    district_idx = -1
    lat_idx = -1
    lon_idx = -1
    relation_point_idx = -1

    with open(input_file, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for i, line in enumerate(reader):

            if i == 0:
                # インデックスを取得
                for j, d in enumerate(line):
                    if d == "name":
                        name_idx = j
                    elif d == "pref":
                        pref_idx = j
                    elif d == "city":
                        city_idx = j
                    elif d == "district":
                        district_idx = j
                    elif d == "latitude":
                        lat_idx = j
                    elif d == "longitude":
                        lon_idx = j
                    elif d == "relation_point_default":
                        relation_point_idx = j
                continue

            # Pointを作る
            p = FacultyPoint()
            p.name = line[name_idx]
            p.pref = line[pref_idx]
            p.city = line[city_idx]
            p.district = line[district_idx]
            p.latitude = float(line[lat_idx])
            p.longitude = float(line[lon_idx])
            p.relation_point_default = float(line[relation_point_idx])

            # 条件に応じてリストに登録
            all_post_points.append(p)
            # if p.pref in calc_segment_prefs:
            #     calc_segment_pop_points.append(p)
            if p.pref in region_prefs:
                region_post_points.append(p)

    read_points = {
        "all": all_post_points,
        region: region_post_points
    }

    return read_points


def output_csv(sorted_post_points, region, output_file_without_region):

    file = output_file_without_region + region + ".csv"
    with open(file, "w") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([
            "順位",
            "名前",
            "都道府県",
            "市町村",
            "地区",
            "緯度経度",
            "都会度"
        ])
        for i, p in enumerate(sorted_post_points):
            row = [
                i + 1,
                p.name,
                p.pref,
                p.city,
                p.district,
                str(p.latitude) + ", " + str(p.longitude),
                p.relation_point_default
            ]
            writer.writerow(row)


if __name__ == "__main__":
    main("zenkoku")
