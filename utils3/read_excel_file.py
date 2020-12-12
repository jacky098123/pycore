# coding: utf8
import xlrd

'''
column_row_index: 第一行是否为列名
sheet_index: excel 表中 sheet 的索引
返回: list(dict{})
'''

def read_excel_file(filename, column_row_index=0, sheet_index=0):
    try:
        excel_data = xlrd.open_workbook(filename)
    except Exception, e:
        print str(e)
        return []

    print 'total sheet count', len(excel_data.sheets())

    sheet_table = excel_data.sheets()[sheet_index]
    nrows = sheet_table.nrows #行数
    ncols = sheet_table.ncols #列数
    if column_row_index == 0:
        colnames =  sheet_table.row_values(column_row_index) #某一行数据
        data_start_index = 1
    else:
        colnames = ['col%d' % i for i in range(ncols)]
        data_start_index = 0

    data_list =[]
    for index in range(data_start_index,nrows):
         row = sheet_table.row_values(index)
         if row:
             app = {}
             for i in range(len(colnames)):
                app[colnames[i]] = row[i]
             data_list.append(app)
    return data_list
