#!/usr/bin/python

__author__  = 'Jacky Yang <yangrq@kuxun.com>'
__date__    = '2012-08-11'

import sys
import types
import MySQLdb
import traceback


class MySQLOperator(object):
    '''
    database wrapper
    '''
    def __init__(self, debug=False):
        self.__host     = None
        self.__user     = None
        self.__passwd   = None
        self.__database = None
        self.__charset  = None
        self.__port     = None
        self.__conn     = None
        self.__cursor   = None
        self.__debug    = debug
        self.__autocommit = True

    def SetDebug(self, debug):
        self.__debug = debug


    def SetAutocommit(self, flag):
        self.__autocommit = flag


    def StartTransaction(self):
        self.__conn.commit()
        self.__autocommit = False


    def Commit(self):
        self.__conn.commit()


    def Rollback(self):
        self.__conn.rollback()


    def __str__(self):
        return "%s:%s#%s" % (self.__host, str(self.__port), self.__database)


    def Dump(self):
        print >> sys.stderr, self.__host,self.__user, self.__passwd,self.__database, self.__port, self.__charset


    def Connect(self, host, user, passwd, database, port=3306, charset='utf8'):
        ret     = True
        port    = int(port)
        if self.__debug:
            print >> sys.stderr, host,user,passwd,database,charset,port
        try:
            self.__conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database,
                                          charset=charset, port=port)
            self.__cursor = self.__conn.cursor()
            self.__cursor.execute('set names %s;', charset)
            self.__cursor.execute('set CHARACTER_SET_CLIENT=%s;', charset)
            self.__cursor.execute('set CHARACTER_SET_RESULTS=%s;', charset)
        except MySQLdb.Error, e:
            print >> sys.stderr, "Connect %s %s %s %s %s %s: %s\n" % (host, user, passwd, database, charset, port,
                                                       str(e))
            ret = False
        if ret:
            self.__host = host
            self.__user = user
            self.__passwd = passwd
            self.__database = database
            self.__charset  = charset
            self.__port     = port
        return ret


    def Query(self, sql, args=None):
        if self.__debug:
            print >> sys.stderr, 'Debug Query:', sql, args
        self.__cursor.execute(sql, args)
        return self.__cursor.fetchall()


    def QueryDict(self, sql, args=None):
        if self.__debug:
            print >> sys.stderr, 'Debug QueryDict:', sql, args

        ret     = []
        self.__cursor.execute(sql, args)
        desc    = self.__cursor.description
        row     = self.__cursor.fetchone()
        while row:
            m   = {}
            for i in range(len(desc)):
                m[desc[i][0]] = row[i]
            ret.append(m)
            row = self.__cursor.fetchone()
        return ret


    def Execute(self, sql, args=None):
        if self.__debug:
            print >> sys.stderr, 'Debug Execute:', sql, ', args:', args
        affected_count = 0
        try:
            affected_count = self.__cursor.execute(sql, args)
            if self.__autocommit:
                self.__conn.commit()
        except Exception, e:
            print >> sys.stderr, 'Execute exception msg:', str(e)
            print >> sys.stderr, 'Execute exception sql:', sql, ', args:', args
            traceback.print_exc()
        return affected_count


    def _FormatData(self, data):
        skip_column = []
        for k,v in data.iteritems():
            if type(v) == types.NoneType:
                skip_column.append(k)

        for c in skip_column:
            data.pop(c)
        
        return data


    # data_columns: dict
    def ExecuteInsertDict(self, table, data_columns):
        if len(data_columns) == 0:
            return 0

        data_columns = self._FormatData(data_columns)

        tmp = []
        for i in range(len(data_columns)):
            tmp.append('%s')
        sql = 'insert into %s(%s) values(%s)' % (table, ','.join(data_columns.keys()), ','.join(tmp))
        return self.Execute(sql, data_columns.values())


    # data_columns
    def ExecuteUpdateDict(self, table, data_columns, data_parameters):
        data_columns = self._FormatData(data_columns)

        for k,v in data_parameters.iteritems():
            if not v:
                raise Exception, 'invalid parameter for key: %s' % k

        tmp = []
        for k in data_columns.keys():
            if k in data_parameters.keys():
                data_columns.pop(k)

        if len(data_columns) == 0 or len(data_parameters) == 0:
            return 0

        set_set     = []
        where_set   = []
        for k,v in data_columns.iteritems():
            set_set.append(k + '=%s')
        for k,v in data_parameters.iteritems():
            where_set.append(k + '=%s')
        sql = 'update %s set %s where %s'% (table, ','.join(set_set), ' and '.join(where_set))
        return self.Execute(sql, data_columns.values() + data_parameters.values())


    def ExecuteDelete(self, table, data_columns):
        for k,v in data_columns.iteritems():
            if not v:
                raise Exception, 'invalid parameter for key: %s' % k

        where_set   = []
        for i in data_columns.keys():
            where_set.append("%s=%%s" % i)
        sql = "delete from %s where %s" % (table, ' and '.join(where_set))
        return self.Execute(sql, data_columns.values())


    def Close(self):
        if self.__cursor:
            self.__cursor.close()
            self.__cursor = None
        if self.__conn:
            self.__conn.close()
            self.__conn = None


    def IsRowExists(self, table, dict_data):
        where_set = []
        for k,v in dict_data.iteritems():
            if not k or not v:
                err_str = 'invalid k: %s, v: %s' % (str(k), str(v))
                raise Exception, err_str
            where_set.append(k + '=%s')
        sql = "select count(*) from %s where %s" % (table, ' and '.join(where_set))
        result_set = self.Query(sql, dict_data.values())
        if result_set[0][0] > 0:
            return True
        return False


    # data is dict, keys is []
    def Upsert(self, table, data, upsert_keys):
        data = self._FormatData(data)

        for i in upsert_keys:
            if i not in data:
                raise Exception, 'upsert_key not in data'

        update_para     = {}
        update_column   = {}
        for i in data.keys():
            if i in upsert_keys:
                update_para[i] = data[i]
            else:
                if type(data[i]) != types.NoneType:
                    update_column[i] = data[i]

        if self.IsRowExists(table, update_para):
            return self.ExecuteUpdateDict(table, update_column, update_para)
        else:
            return self.ExecuteInsertDict(table, data)


class MySQLDataDict(MySQLOperator):
    '''
    process data dictionary
    '''
    def __init__(self, debug=False):
        MySQLOperator.__init__(self, debug)


    def __str__(self):
        return MySQLOperator.__str__(self)


    def GetDatabase(self, database):
        if database:
            return database

        result_set = self.Query("select database()")
        if len(result_set) != 1:
            print >> sys.stderr, "GetDatabase error"
            return None

        return result_set[0][0]


    def GetTableRowCount(self, table):
        sql = '''select count(*) cnt from %s''' % table
        row_count = self.Query(sql)
        return row_count[0][0]


    def GetTableRowCountWithCondition(self, table, clause):
        sql = '''select count(*) cnt from %s where %s ''' % (table,clause)
        row_count = self.Query(sql)
        return row_count[0][0]


    def GetAllTables(self, database=None):
        database = self.GetDatabase(database)
        ret = []
        sql = '''select table_name from information_schema.tables '''
        sql = sql + ''' where table_schema=\'%s\' and table_type=\'base table\' ''' % database;
        tables = self.Query(sql)
        for table in tables:
            ret.append(table[0])
        return ret


    def IsTableExist(self, table, database=None):
        database = self.GetDatabase(database)
        sql = 'select count(*) cnt from information_schema.tables where table_type=\'base table\' '
        sql = sql + ''' and table_schema=\'%s\' and table_name = \'%s\' ''' % (database,table);
        counts = self.Query(sql)
        if counts[0][0]:
            return True
        else:
            return False


    def GetAllColumns(self, table, database=None):
        ret = []
        database = self.GetDatabase(database)
        sql ='select column_name from information_schema.columns'
        sql = sql + ' where table_schema=\'%s\' and table_name=\'%s\' ' % (database, table);
        columns = self.Query(sql)
        for column in columns:
            ret.append(column[0])
        return ret


    def GetPrimaryKey(self, table, database=None):
        database = self.GetDatabase(database)
        ret = []
        sql = '''select column_name from information_schema.statistics '''
        sql = sql + ' where index_schema=\'%s\' and table_name=\'%s\' and index_name = \'PRIMARY\' '
        sql = sql + ''' order by seq_in_index asc '''
        sql = sql % (database, table)
        columns = self.Query(sql)
        for column in columns:
            ret.append(column[0])
        return ret


def Test1():
    db = MySQLDataDict()
    if db.Connect("192.168.0.23", "root", "kooxoo", "test", 3306, 'utf8') is False:
        exit(3)
    query_list = db.GetAllTables()
    print query_list
    query_list = db.GetAllColumns('documents')
    print query_list
    query_list = db.GetPrimaryKey('documents')
    print query_list

    db.Close()


if __name__ == '__main__':
    Test1()
