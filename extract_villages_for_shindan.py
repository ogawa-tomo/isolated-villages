from setting import Setting, RegionSetting
import calc_isolation


extracted_villages = []
for region in RegionSetting.get_region_list():
    small_village_setting = Setting(
        region,
        1,
        1,
        6,
    )
    result = calc_isolation.main(small_village_setting)
    villages = result.sorted_villages
    # if len(villages) < 100:
    #     extracted_villages.extend(villages[:10])
    #     print(region + "は10集落のみ抽出")
    # else:
    #     extracted_villages.extend(villages[:30])
    extracted_villages.extend(villages[:20])

# with open("./output/shindan.txt", "w") as f:
with open("./output/button.txt", "w") as f:
    for v in extracted_villages:
        # row = "".join([
        #     v.pref,
        #     v.city,
        #     v.district,
        #     "[BR]",
        #     str(v.latitude_round),
        #     ",",
        #     str(v.longitude_round),
        #     "\n"
        # ])
        # f.write(row)

        row = "".join([
            v.pref,
            v.city,
            v.district,
            "\n",
            "http://maps.google.com/maps?q=",
            str(v.latitude_round),
            ",",
            str(v.longitude_round),
            "&t=k",
            "\n\n"
        ])
        f.write(row)




