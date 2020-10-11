import MySQLdb

class connectDB:

    def __init__(self):
        self.connection = MySQLdb.connect(
            host = 'localhost',
            user = '',
            passwd = '',
            db = '755PJT',
            charset = 'utf8',
        )
        self.cursor = self.connection.cursor()

    def __makeSelectSQL(self, select, table, conditions = None):
        if select:
            selectCol = ''
            for i in range(len(select)):
                if i < len(select) - 1:
                    selectCol += select[i] + ', '
                if i == len(select) - 1:
                    selectCol += select[i]
        else:
            selectCol = '*'

        sql = 'SELECT ' \
                + selectCol \
                + ' FROM ' \
                + table

        if conditions:
            sql += ' WHERE ' + conditions
        print(sql)
        return sql

    def getSelectAll(self, select, table, conditions = None):
        sql = connectDB.__makeSelectSQL(self, select, table, conditions)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows

    def getSelectOne(self, select, table, conditions = None):
        sql = connectDB.__makeSelectSQL(self, select, table, conditions)
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        for value in row:
            return value

    def __dbCommint(self):
        self.connection.commit()

    def __dbClose(self):
        self.connection.close()