from setting import Setting, RegionSetting
import calc_isolation
import operator
from make_point_db import RegionPointDataReader
import os


region_point_input_file = os.path.join("./input", "japan_region.txt")
rpd = RegionPointDataReader(region_point_input_file)
rpd.read_points()
all_regions = []
for segment in RegionSetting.get_address_calc_segment_list():
    all_regions.extend(rpd.region_points_by_segment[segment])

for rp in all_regions:
    rp.set_len_district()

all_regions.sort(key=operator.attrgetter("len_district"), reverse=True)

with open("./output/long_name.txt", "w") as f:
    for v in all_regions:
        row = "".join([
            v.pref,
            v.city,
            v.district,
            "\n"
        ])
        f.write(row)




# extracted_villages = []
# for region in RegionSetting.get_region_list():
#     small_village_setting = Setting(
#         region,
#         1,
#         1,
#         # 299,
#         4,
#         0
#     )
#     # big_village_setting = Setting(
#     #     region,
#     #     100,
#     #     300,
#     #     # 10000,
#     #     4,
#     #     0
#     # )
#     for s in [small_village_setting]:
#         s.region = region
#         result = calc_isolation.main(s)
#         extracted_villages.extend(result.sorted_villages)
#         # villages_temp = result.sorted_villages
#         # villages = []
#         # if s.village_pop_lower_limit == 1:
#         #     # 300人以下の集落のみ
#         #     for v in villages_temp:
#         #         if v.population < 300:
#         #             villages.append(v)
#         #     extracted_villages.extend(villages[:30])
#         # else:
#         #     villages = villages_temp
#         #     extracted_villages.extend(villages[:20])

# extracted_villages.sort(key=operator.attrgetter("len_district"), reverse=True)
# with open("./output/long_name.txt", "w") as f:
#     for v in extracted_villages:
#         row = "".join([
#             v.pref,
#             v.city,
#             v.district,
#             "[BR]",
#             str(v.latitude_round),
#             ",",
#             str(v.longitude_round),
#             "\n"
#         ])
#         f.write(row)




