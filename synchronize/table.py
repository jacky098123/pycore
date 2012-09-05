#!/usr/bin/python

__author__  = 'Jacky Yang <yangrq@kuxun.com>'
__date__    = '2012-09-04'

import os
import sys
import types
import StringIO
import logging

FILE_PATH   = os.path.dirname(os.path.realpath(__file__))
CORE_PATH   = os.path.join(FILE_PATH, '..')
if CORE_PATH not in sys.path:
    sys.path.append(CORE_PATH)

from db.mysqlv6 import MySQLOperator, MySQLDataDict

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s [%(filename)s:%(lineno)d](%(funcName)s)'
                    )

'''
firstly this is a project, and it is library for synchronize,
the problem is it is complex for dependency where using this.
now this becomes a module of library
'''

class UtilLog:
    def __init__(self):
        current_path    = os.path.dirname(os.path.realpath(__file__))
        self.data_path  = os.path.join(current_path, 'data')
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)


    def LogDictData(self, file_name, dict_data, prefix=None):
        file_obj = open(file_name, "a")

        o = StringIO.StringIO()
        if prefix:
            o.write(prefix + '\t')
        for j in dict_data.iterkeys():
            o.write(j)
            o.write('\t')
        o.write('\n')

        if prefix:
            o.write(prefix + '\t')
        for j in dict_data.itervalues():
            o.write(j)
            o.write('\t')
        o.write('\n')
        file_obj.write(o.getvalue())

        o.close()
        file_obj.close()


    def LogListData(self, file_name, list_data, prefix=None):
        file_obj = open(file_name, "a")

        o = StringIO.StringIO()
        if prefix:
            o.write(prefix + '\t')
        for j in list_data:
            o.write(j)
            o.write('\t')
        o.write('\n')
        file_obj.write(o.getvalue())

        o.close()
        file_obj.close()


    def ExitOnError(self, str):
        print >> sys.stderr, str
        sys.exit()


class Table(UtilLog):
    def __init__(self, table_name,  columns, primary_keys=None):
        UtilLog.__init__(self)
        self.table_name     = table_name
        self.fields         = columns
        self.primary_keys   = primary_keys
        self.title          = None
        self.connection     = None

        self.__total_rows   = 0
        self.__count_per_time   = 100000
        self.__offset       = 0


    def Initialize(self, connection):
        logging.info('Table Initialize')
        self.connection = connection
        self.title      = str(connection) + '.' + self.table_name

        # init primary_keys
        if not self.primary_keys:
            self.primary_keys   = self.connection.GetPrimaryKey(self.table_name)
            if not self.primary_keys:
                self.ExitOnError('table %s no primary key' % self.table_name)
        for i in self.primary_keys:
            if i not in self.fields:
                self.fields.append(i)

        # verify fields is correct
        full_table_fields   = connection.GetAllColumns(self.table_name)
        for field in self.fields:
            if field not in full_table_fields:
                self.ExitOnError('fields error: %s (%s)' % (field, self.title))

        # get total numbers
        self.__total_rows   = self.connection.GetTableRowCount(self.table_name)


    def LoadData(self, condition):
        if self.__offset > self.__total_rows:
            return None

        sql = ''
        if condition:
            sql = self.__GetConditionSQL(condition)
        else:
            sql = self.__GetCommonnSQL()
        self.__offset = self.__offset + self.__count_per_time
        logging.debug('sql: %s' % sql)
        return self.connection.QueryDict(sql)

    def __GetCommonnSQL(self):
        sql = "select %s from %s limit %d,%d" % (','.join(self.fields), self.table_name, self.__offset,
                                                self.__count_per_time)
        return sql

    def __GetConditionSQL(self, condition):
        sql = "select %s from %s where %s limit %d,%d" % (','.join(self.fields), self.table_name,
                                                condition, self.__offset, self.__count_per_time)
        return sql

    def GetByPrimaryKey(self, keys):
        tmp = []
        for key in keys.keys():
            tmp.append(key + '=%s')
        sql = "select %s from %s where %s" % (','.join(self.fields), self.table_name, ' and '.join(tmp))
        ret = self.connection.QueryDict(sql, keys.values())
        if ret:
            return ret[0]
        return None

    # orderd for compare
    def LoadPrimaryKeyData(self):
        sql = "select %s from %s order by %s" % (",".join(self.primary_keys),
                                                 self.table_name, ",".join(self.primary_keys));
        return self.connection.QueryDict(sql)

    def LogPrimaryKeyData(self, list_data):
        file_name = self.data_path + '/' + self.table_name + '.data';
        if os.access(file_name, os.F_OK):
            os.remove(file_name)

        if len(list_data) == 0:
            return

        logging.info('%s log %d rows to %s' % (self.title, len(list_data), file_name))
        self.LogListData(file_name, self.primary_keys)

        for i in range(len(list_data)):
            self.LogListData(file_name, list_data[i].itervalues())

    # data: dict
    def Update(self, data):
        para    = {}
        column  = {}
        for f in data.keys():
            if f in self.primary_keys:
                para[f] = data[f]
            else:
                column[f] = data[f]
        self.connection.ExecuteUpdateDict(self.table_name, column, para)

    # data: dict
    def Upsert(self, data):
        self.connection.Upsert(self.table_name, data, self.primary_keys)

    # data: dict
    def Insert(self, data):
        self.connection.ExecuteInsertDict(self.table_name, data)

    def Delete(self, primary_key_data):
        self.connection.ExecuteDelete(self.table_name, primary_key_data)


class TablePair(UtilLog):
    '''
    table pair must has the same primary keys
    '''
    def __init__(self, source_table, **args):
        UtilLog.__init__(self)
        self.source_table   = None
        self.dest_table     = None
        self.field_mapping  = None # dict
        self._parameters    = args
        self._source_table  = source_table


    def Initialize(self, source_conn, dest_conn):
        logging.info('TablePair Initialize')
        if not isinstance(source_conn, MySQLDataDict) or not isinstance(dest_conn, MySQLDataDict):
            self.ExitOnError('invalid connection instance')

        # get columns
        src_table_field = source_conn.GetAllColumns(self._source_table)
        if len(src_table_field) == 0:
            self.ExitOnError("src_table_field is zero: %s" % self._source_table)

        # get src columns
        include         = None
        exclude         = None
        src_columns     = None
        if 'include_fields' in self._parameters:
            include = self._parameters['include_fields']
        if 'exclude_fields' in self._parameters:
            exclude = self._parameters['exclude_fields']
        if include and exclude:
            self.ExitOnError('include and exclude conflit')
        if include:
            for field in include:
                if field not in src_table_field:
                    logging.error('src_table_field: %s', str(src_table_field))
                    self.ExitOnError('invalid include option: %s' % field)
            src_columns = include
        if exclude:
            for field in exclude:
                if field not in src_table_field:
                    logging.error('src_table_field: %s', str(src_table_field))
                    self.ExitOnError('invalid exclude option %s' % field)
                # TODO
                src_table_field.remove(field)
            src_columns = src_table_field
        if not include and not exclude:
            src_columns = src_table_field

        # get dst columns
        dst_columns = src_columns
        if 'field_mapping' in self._parameters:
            self.field_mapping = self._parameters['field_mapping']
            dst_columns = list(set(src_columns) - set(self.field_mapping.keys()) | set(self.field_mapping.values()))

        # get primary_key
        primary_keys = None
        if 'primary_keys' in self._parameters:
            primary_keys = self._parameters['primary_keys']

        # create table obj
        self.source_table   = Table(self._source_table, src_columns, primary_keys)
        if 'dest_table' in self._parameters:
            self.dest_table     = Table(self._parameters['dest_table'], dst_columns, primary_keys)
        else:
            self.dest_table     = Table(self._source_table, dst_columns, primary_keys)

        # table obj init
        self.source_table.Initialize(source_conn)
        self.dest_table.Initialize(dest_conn)

        # verify init is fine
        self.title = self.source_table.title + ' ====> ' + self.dest_table.title
        if self.source_table.primary_keys != self.dest_table.primary_keys:
            self.ExitOnError('table pair has different primary keys')


    def ConvertData(self, input):
        if not self.field_mapping:
            return input

        output = {}
        for field in input.keys():
            if field in self.field_mapping:
                output[self.field_mapping[field]] = input[field]
            else:
                output[field] = input[field]
        return output

    def Compare(self, s, d, keys, index): 
        if len(s) <= index: 
            return 0; 
        if s[keys[index]] < d[keys[index]]: 
            return -1;
        if s[keys[index]] > d[keys[index]]:
            return 1;
        return self.Compare(s, d, keys, index + 1)

    def _Diff(self):
        source_primary_key_data = self.source_table.LoadPrimaryKeyData()
        dest_primary_key_data   = self.dest_table.LoadPrimaryKeyData()
        unique_primary_key  = self.source_table.primary_keys
        diff_source_data    = []
        diff_dest_data      = []
        diff_equal_data     = []
        idx_source          = 0
        idx_dest            = 0

        while idx_source < len(source_primary_key_data) and idx_dest < len(dest_primary_key_data):
            # compare 
            s   = source_primary_key_data[idx_source]
            d   = dest_primary_key_data[idx_dest]
            ret = self.Compare(s, d, unique_primary_key, 0)
            if ret == 0:
                diff_equal_data.append(d)
                idx_source  = idx_source + 1
                idx_dest    = idx_dest + 1
            elif ret < 0:
                diff_source_data.append(s)
                idx_source  = idx_source + 1
            else:
                diff_dest_data.append(d)
                idx_dest    = idx_dest + 1
        while idx_source < len(source_primary_key_data):
            diff_source_data.append(source_primary_key_data[idx_source])
            idx_source  = idx_source + 1
        while idx_dest < len(dest_primary_key_data):
            diff_dest_data.append(dest_primary_key_data[idx_dest])
            idx_dest    = idx_dest + 1

        return (diff_source_data, diff_dest_data, diff_equal_data)


    def Diff(self, compare_equal_flag=False):
        logging.info(self.title + ' Begin Diff ...')
        logging.info('source table fields: %s' % str(self.source_table.fields))

        (diff_source_data, diff_dest_data, diff_equal_data) = self._Diff()

        self.source_table.LogPrimaryKeyData(diff_source_data)
        self.dest_table.LogPrimaryKeyData(diff_dest_data)

        logging.info('%d rows are equal(primary key)' % len(diff_equal_data))

        primary_file_name = self.data_path + '/' + self.source_table.table_name + ".equal.primary"
        if os.access(primary_file_name, os.F_OK):
            os.remove(primary_file_name)

        nocompare_file_name = self.data_path + '/' + self.source_table.table_name + ".equal.nocompare"
        if os.access(nocompare_file_name, os.F_OK):
            os.remove(nocompare_file_name)

        full_file_name = self.data_path + '/' + self.source_table.table_name + ".equal.full"
        if os.access(full_file_name, os.F_OK):
            os.remove(full_file_name)

        # equal flag
        if not compare_equal_flag:
            self.LogListData(nocompare_file_name, self.source_table.primary_keys)
            for i in range(len(diff_equal_data)):
                self.LogListData(nocompare_file_name, diff_equal_data[i].itervalues())
            return

        self.LogListData(primary_file_name, self.source_table.primary_keys)
        self.LogListData(full_file_name, self.source_table.primary_keys)

        diff_equal_log_count    = 0
        log_key_flag            = True
        for i in range(len(diff_equal_data)):
            source = self.source_table.GetByPrimaryKey(diff_equal_data[i])
            source = self.ConvertData(source)
            dest = self.dest_table.GetByPrimaryKey(diff_equal_data[i])
            equal_flag = True
            for field in self.dest_table.fields:
                if source[field] != dest[field]:
                    equal_flag = False
                    break
            if equal_flag:
                diff_equal_log_count = diff_equal_log_count + 1
                self.LogListData(full_file_name, diff_equal_data[i].itervalues())
            else:
                self.LogListData(primary_file_name, diff_equal_data[i].itervalues())

        logging.info('%d rows are primary equal, %d rows are full equal' % (
                    len(diff_equal_data) - diff_equal_log_count, diff_equal_log_count))


    def Synchronize(self, condition=None):
        logging.info(self.title + ' Synchronize ...')
        logging.info('source table fields: %s', str(self.source_table.fields))

        process_flag = True
        while process_flag:
            result_set = self.source_table.LoadData(condition)
            if not result_set:
                process_flag = False
                logging.info('synchronize finished')
                return

            logging.info('do synchronize %d rows' % len(result_set))

            for row_dict in result_set:
                data = self.ConvertData(row_dict)
                self.dest_table.Upsert(data)


    def DestDelete(self, dry_run_flag=True):
        logging.info(self.title, 'DestDelete ...')
        
        (diff_source_data, diff_dest_data, diff_equal_data) = self._Diff() 

        if len(diff_dest_data) == 0:
            logging.info('no result to dest in dest table')
            return

        if dry_run_flag:
            file_name = self.data_path + '/' + self.dest_table.table_name + ".equal"
            logging.info('this is dry run, it does no delete anything')
            logging.info('please refer to %s' % file_name)
            self.LogListData(file_name, self.primary_keys)
            for i in range(len(diff_dest_data)):
                self.LogListData(file_name, diff_dest_data[i].itervalues())
            return

        for primary_key_data in diff_dest_data:
            self.dest_table.Delete(primary_key_data)


    def StartTransaction(self):
        self.dest_table.connection.StartTransaction()


    def Rollback(self):
        self.dest_table.connection.Rollback()


    def Commit(self):
        self.dest_table.connection.Commit()


    def Dump(self):
        print self.title


def simple_test():
    source_conn     = MySQLDataDict()
    dest_conn       = MySQLDataDict()

    if not source_conn.Connect("192.168.0.23", "root", "kooxoo", "test"):
        exit()
    if not dest_conn.Connect("192.168.0.23", "root", "kooxoo", "test2"):
        exit()

    table_pair1 = TablePair("documents",
                            dest_table="documents2",
                            include_fields=['title', 'group_id', 'group_id2', 'content'],
                            field_mapping={'title': 'title_2'},
                            primary_keys=['id',])
    table_pair1.Initialize(source_conn, dest_conn)
#    table_pair1.Dump()

    condition = "id=3"
#    table_pair1.Synchronize()
    table_pair1.Diff(True)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    simple_test()
