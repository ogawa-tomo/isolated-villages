import psycopg2


class PointRelationDAO(object):

    def __init__(self):
        self.conn_db = "dbname=village_db user=village_admin password = sukasuka"

    @classmethod
    def get_table_name(cls, region):
        """
        テーブル名を返す関数
        :param region:
        :return:
        """
        return region + "_neighbor_relation"

    def has_table(self, region):
        """
        地域の関係テーブルが存在するかを返す関数
        :param region:
        :return:
        """

        conn = psycopg2.connect(self.conn_db)
        cur = conn.cursor()
        query = "".join(["select * from ", self.get_table_name(region), ";"])
        try:
            cur.execute(query)
            return True
        except psycopg2.ProgrammingError:
            return False

    def get_neighbor_keys(self, key, region, conn):
        """
        keyで指定したポイントに隣接するポイントのkeyのリストを返す関数
        接続は行われている前提
        :param key:
        :param region:
        :param conn:
        :return:
        """

        cur = conn.cursor()
        query = "".join(["select neighbors from ", self.get_table_name(region),
                         " where key = \'", str(key), "\';"])
        cur.execute(query)
        records = cur.fetchall()
        if len(records) == 0:
            return []
        else:
            neighbors = records[0][0].split(",")
            return neighbors

    def create_relation_table(self, region):
        conn = psycopg2.connect(self.conn_db)
        cur = conn.cursor()
        query = "".join(["create table ",
                         self.get_table_name(region),
                         " (key text PRIMARY KEY, neighbors text);"])
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()

    def exist_record(self, key, region, conn):
        """
        テーブルにkeyのレコードがあるかを調べる
        :param key:
        :param region:
        :param conn:
        :return:
        """
        # レコードの数が1以上ならTrue
        cur = conn.cursor()
        query = "".join(["select count(key) from ", self.get_table_name(region),
                         " where key = \'", str(key), "\';"])
        cur.execute(query)
        n = cur.fetchall()[0][0]

        if n == 1:
            return True
        else:
            return False

    def add_record(self, key, region, conn):
        """
        レコードをたす
        :param key:
        :param region:
        :param conn:
        :return:
        """
        cur = conn.cursor()
        query = "".join(["insert into ", self.get_table_name(region), " values (\'", str(key), "\', \'\');"])
        cur.execute(query)

    def add_relation(self, key1, key2, region, conn):
        """
        隣接関係の登録（相互に行う）
        :param key1:
        :param key2:
        :param region:
        :param conn:
        :return:
        """

        self.add_neighbor(key1, key2, region, conn)
        self.add_neighbor(key2, key1, region, conn)

    def add_neighbor(self, key, neighbor_key, region, conn):
        """
        keyのレコードにneighborを1つ足す
        :param key:
        :param neighbor_key:
        :param region:
        :param conn:
        :return:
        """

        if self.exist_record(key, region, conn):
            # レコードがある場合は、カンマつきでneighbor_keyをたす
            set_data = "neighbors || \'," + str(neighbor_key) + "\'"
        else:
            # レコードがない場合は、レコードを作ってneighbor_keyをたす
            self.add_record(key, region, conn)
            set_data = "\'" + str(neighbor_key) + "\'"

        cur = conn.cursor()
        query = "".join(["update ", self.get_table_name(region), " set neighbors = ", set_data,
                         " where key = \'", str(key), "\';"])
        cur.execute(query)

    def connect_table(self):
        conn = psycopg2.connect(self.conn_db)
        return conn

    @staticmethod
    def close_connect_table(conn):
        conn.commit()
        conn.close()
