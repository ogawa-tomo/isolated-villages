from setting import Setting, RegionSetting
import calc_isolation


extracted_villages = []
for region in RegionSetting.get_region_list():
    small_village_setting = Setting(
        region,
        1,
        1,
        # 299,
        6,
        0
    )
    big_village_setting = Setting(
        region,
        100,
        300,
        # 10000,
        6,
        0
    )
    for s in [small_village_setting, big_village_setting]:
        s.region = region
        result = calc_isolation.main(s)
        villages_temp = result.sorted_villages
        villages = []
        if s.village_pop_lower_limit == 1:
            # 300人以下の集落のみ
            for v in villages_temp:
                if v.population < 300:
                    villages.append(v)
        else:
            villages = villages_temp

        extracted_villages.extend(villages[:20])

with open("./output/shindan.txt", "w") as f:
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




