

# こうかけばいいらしい
url = "https://www.google.com/maps/dir/?api=1&origin=38.25543,140.339616&destination=38.26821,140.869373&waypoints=39.4099089,140.5524455|40.0, 141.0&travelmode=walking"


def main(region, destination):
    villages = []

    # 集落を抽出

    # 最終目的地から順に辿ってルート作成
    way_points = []

    # ルートを描画
