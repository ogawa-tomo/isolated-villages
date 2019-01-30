

class Setting(object):

    def __init__(
            self,
            region,
            # pop_param,
            # dist_param,
            point_pop_lower_limit,
            # point_pop_upper_limit,
            village_pop_lower_limit,
            # village_pop_upper_limit,
            # village_size_lower_limit,
            village_size_upper_limit,
            # max_density_lower_limit,
            # distance_threshold,
            # coast_distance_threshold,
            # point_output_num
    ):
        self.region = region
        # self.pop_param = pop_param
        # self.dist_param = dist_param
        self.point_pop_lower_limit = point_pop_lower_limit
        # self.point_pop_upper_limit = point_pop_upper_limit
        self.village_pop_lower_limit = village_pop_lower_limit
        # self.village_pop_upper_limit = village_pop_upper_limit
        # self.village_size_lower_limit = village_size_lower_limit
        self.village_size_upper_limit = village_size_upper_limit
        # self.max_density_lower_limit = max_density_lower_limit
        # self.distance_threshold = distance_threshold
        # self.coast_distance_threshold = coast_distance_threshold
        # self.point_output_num = point_output_num

        self.region_kanji = RegionSetting.get_region_kanji(region)

        self.setting = {
            "region": self.region_kanji,
            # "population_param": pop_param,
            # "distance_param": dist_param,
            "point_pop_lower_limit": point_pop_lower_limit,
            # "point_pop_upper_limit": point_pop_upper_limit,
            "village_pop_lower_limit": village_pop_lower_limit,
            # "village_pop_upper_limit": village_pop_upper_limit,
            # "village_size_lower_limit": village_size_lower_limit,
            "village_size_upper_limit": village_size_upper_limit,
            # "max_density_lower_limit": max_density_lower_limit,
            # "distance_threshold": distance_threshold,
            # "coast_distance_threshold": coast_distance_threshold,
            # "point_output_num": point_output_num
        }


class RegionSetting(object):

    # region_prefs = {
    #     "hokkaido": ["北海道"],
    #     "tohoku": ["青森県", "秋田県", "岩手県", "山形県", "宮城県", "福島県"],
    #     "kanto": ["東京都", "埼玉県", "神奈川県", "千葉県", "群馬県", "栃木県", "茨城県"],
    #     "chubu": ["山梨県", "長野県", "新潟県", "富山県", "福井県", "岐阜県", "静岡県", "愛知県", "石川県"],
    #     "kinki": ["滋賀県", "京都府", "大阪府", "兵庫県", "三重県", "奈良県", "和歌山県"],
    #     "chugoku": ["岡山県", "鳥取県", "広島県", "島根県", "山口県"],
    #     "shikoku": ["香川県", "愛媛県", "徳島県", "高知県"],
    #     "kyushu": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県"]
    # }

    region_prefs = {
        "hokkaido": ["北海道"],
        "tohoku": ["青森県", "秋田県", "岩手県", "山形県", "宮城県", "福島県"],
        "kanto": ["東京都", "埼玉県", "神奈川県", "千葉県", "群馬県", "栃木県", "茨城県"],
        "hokuriku": ["新潟県", "富山県", "福井県", "石川県"],
        "chubu": ["山梨県", "長野県", "静岡県", "岐阜県", "愛知県"],
        "kinki": ["滋賀県", "京都府", "大阪府", "兵庫県", "三重県", "奈良県", "和歌山県"],
        "chugoku": ["岡山県", "鳥取県", "広島県", "島根県", "山口県"],
        "shikoku": ["香川県", "愛媛県", "徳島県", "高知県"],
        "kyushu": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県"]
    }

    calc_segment = {
        "hokkaido": "hokkaido",
        "tohoku": "honshu",
        "chubu": "honshu",
        "hokuriku": "honshu",
        "kanto": "honshu",
        "kinki": "honshu",
        "chugoku": "honshu",
        "shikoku": "shikoku",
        "kyushu": "kyushu"
    }

    calc_segment_regions = {
        "hokkaido": ["hokkaido"],
        # "honshu": ["tohoku", "kanto", "chubu", "kinki", "chugoku"],
        "honshu": ["tohoku", "kanto", "hokuriku", "chubu", "kinki", "chugoku"],
        "shikoku": ["shikoku"],
        "kyushu": ["kyushu"]
    }

    region_kanji = {
        "hokkaido": "北海道",
        "tohoku": "東北",
        "chubu": "中部",
        "kanto": "関東",
        "hokuriku": "北陸",
        "kinki": "近畿",
        "chugoku": "中国",
        "shikoku": "四国",
        "kyushu": "九州",
        "zenkoku": "全国"
    }

    address_calc_segment_lon_thresholds = [
        130,
        132,
        134,
        136,
        138,
        140,
        142,
        144,
        146
    ]

    address_calc_segment_lat_thresholds = [
        30,
        32,
        34,
        36,
        38,
        40,
        42,
        44
    ]

    @classmethod
    def get_region_prefs(cls, region):
        if region == "zenkoku":
            return cls.get_all_prefs()
        else:
            return cls.region_prefs[region]

    @classmethod
    def get_all_prefs(cls):
        all_prefs = []
        for region in cls.region_prefs.keys():
            all_prefs.extend(cls.region_prefs[region])
        return all_prefs

    @classmethod
    def get_calc_segment(cls, region):
        return cls.calc_segment[region]

    @classmethod
    def get_region_kanji(cls, region):
        return cls.region_kanji[region]

    @classmethod
    def get_calc_segment_prefs_by_region(cls, region):
        calc_segment = cls.get_calc_segment(region)
        regions = cls.calc_segment_regions[calc_segment]
        prefs = []
        for region in regions:
            temp_prefs = cls.get_region_prefs(region)
            prefs.extend(temp_prefs)
        return prefs

    @classmethod
    def get_calc_segments(cls):
        return cls.calc_segment_regions.keys()

    @classmethod
    def get_region_by_pref(cls, pref):
        for region in cls.region_prefs.keys():
            if pref in cls.region_prefs[region]:
                return region
        raise Exception

    @classmethod
    def get_calc_segment_by_pref(cls, pref):
        region = cls.get_region_by_pref(pref)
        return cls.calc_segment[region]

    @classmethod
    def get_address_calc_segment_by_lat_lon(cls, lat, lon):

        lat_segment = len(cls.address_calc_segment_lat_thresholds) + 1
        for i, threshold in enumerate(cls.address_calc_segment_lat_thresholds):
            if lat < threshold:
                lat_segment = i
                break

        lon_segment = len(cls.address_calc_segment_lon_thresholds) + 1
        for i, threshold in enumerate(cls.address_calc_segment_lon_thresholds):
            if lon < threshold:
                lon_segment = i
                break

        return lat_segment, lon_segment

    @classmethod
    def get_address_calc_segment_list(cls):
        segment_list = []
        lat_segments = len(cls.address_calc_segment_lat_thresholds) + 2
        lon_segments = len(cls.address_calc_segment_lon_thresholds) + 2
        for i in range(lat_segments):
            for j in range(lon_segments):
                segment_list.append((i, j))
        return segment_list

    @classmethod
    def get_region_list(cls):
        return cls.region_prefs.keys()


if __name__ == "__main__":
    print(RegionSetting.get_calc_segment_prefs_by_region("kinki"))



