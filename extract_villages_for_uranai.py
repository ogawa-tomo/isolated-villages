from setting import Setting, RegionSetting
import calc_isolation


extracted_villages = []
for region in RegionSetting.get_region_list():
    small_village_setting = Setting(
        region,
        1,
        1,
        299,
        6,
        0
    )
    big_village_setting = Setting(
        region,
        100,
        300,
        10000,
        6,
        0
    )
    for s in [small_village_setting, big_village_setting]:
        s.region = region
        result = calc_isolation.main(s)
        villages = result.sorted_villages
        extracted_villages.extend(villages[:30])

with open("./output/uranai.txt", "w") as f:
    for v in extracted_villages:
        row = "".join([
            v.pref,
            v.city,
            v.district,
            "[BR]",
            str(v.latitude_round),
            ",",
            str(v.longitude_round),
            "\n"
        ])
        f.write(row)




