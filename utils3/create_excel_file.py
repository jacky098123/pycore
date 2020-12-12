# encoding: utf8

from xlwt import *

'''@param fileName:文件名
   @param dataDict:数据
   dataDict格式 {"_sheetName":[u'a',u'b',u'c'],
                "_sheetData":{"a":[['1','2','3'],['a','b','c']],
                              "b":[['11','22','33'],['aa','bb','cc']],
                              "c":[['111','222','333'],['aaa','bbb','ccc']]
                             },
                "_sheetTitle":{"a":[[u'日期',u'visits数量',u'leads数量']]}
                "_sheetStyle":{"a":{0:XFStyleobject,1:XFStyleobject}}
                }
'''
def create_excel_file(file_name, sheetNameList=[], sheetDataDict={}, sheetTitleDict={}, sheetStyleDict={}):
    excelfile = Workbook()
    for sheetName in sheetNameList:
        ws = excelfile.add_sheet(sheetName)
        titleList = sheetTitleDict.get(sheetName,[])
        styleDict = sheetStyleDict.get(sheetName,{})
        dataList = sheetDataDict.get(sheetName,[])
        rowIdx = 0
        for title in titleList:
            write_row(ws,rowIdx,title)
            rowIdx +=1
        for data in dataList:
            write_row(ws,rowIdx,data,styleDict)
            rowIdx +=1
    excelfile.save(file_name)


''' 对excel增加行 '''
def write_row(tableObj,rowNum,tmpList,xlsStyleDict={}):
    for num,o in enumerate(tmpList):
        if num in xlsStyleDict:
            style = xlsStyleDict.get(num)
            tableObj.write(rowNum,num,o,style)
        else:
            tableObj.write(rowNum,num,o)

