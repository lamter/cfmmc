"""
对应的表格实例
"""
import os
import csv
import datetime
from collections import OrderedDict, deque


class DailySettlementBaseTable(object):
    """

    """
    title = ''
    fields = []

    def __init__(self, userID, saveto):
        self.saveto = saveto
        self.userID = userID
        self.currentDate = None
        self.data = deque()  # [{data}, {}]

        self.csvFileName = '{}_{}.csv'.format(self.userID, self.title)
        self.csvFilePath = os.path.join(self.saveto, self.csvFileName)

        # 尝试加载已有的数据
        self.lastDate = datetime.date.today()
        self.loadCsv()

    @classmethod
    def isThisTable(cls, tbody):
        """

        :return:
        """
        title = tbody.find_element_by_class_name('header-row').text
        return title == cls.title

    def setCurrentDate(self, date):
        """

        :param date:
        :return:
        """
        assert isinstance(date, datetime.date)
        self.currentDate = date.strftime('%Y-%m-%d')

    def dump(self):
        """

        :param saveto:
        :return:
        """
        filePath = self.csvFilePath

        isCsvExists = os.path.exists(filePath)
        data = self.data
        fields = self.fields

        with open(filePath, 'a') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            if not isCsvExists:
                # 新文件，需要写入表头
                wr.writerow(fields)
            for d in data:
                # 写入数据
                wr.writerow(d.values())

    def loadCsv(self):
        """

        :return:
        """
        if not os.path.exists(self.csvFilePath):
            # 没有已经存在的数据
            return
        with open(self.csvFilePath, 'r') as f:
            csvReader = csv.reader(f, delimiter=',')
            fields = next(csvReader)
            dates = []
            for row in csvReader:
                dates.append(row['交易日期'])
            lastDateStr = dates.sort()
            self.lastDate = datetime.datetime.strptime(lastDateStr, '%Y-%m-%d')


class DailySettlementBalanceTable(DailySettlementBaseTable):
    title = '期货期权账户资金状况'

    fields = (
        '交易日期',
        '上日结存',
        '客户权益',
        '当日存取合计',
        '实有货币资金',
        '平仓盈亏',
        '非货币充抵金额',
        '当日总权利金',
        '货币充抵金额',
        '当日手续费',
        '冻结资金',
        '当日结存',
        '保证金占用',
        '浮动盈亏',
        '可用资金',
        '风险度',
        '追加保证金',
    )

    def load(self, tbody):
        """
        从 tobody 中加载数据
        :return:
        """

        dic = OrderedDict()
        for k in self.fields:
            dic[k] = ''
        self.data.appendleft(dic)

        dic['交易日期'] = self.currentDate

        _units = tbody.find_elements_by_tag_name('td')

        def foo():
            for u in _units:
                yield u

        units = foo()
        title = next(units).text
        while True:
            try:
                k = next(units).text.strip()
                v = next(units).text.strip()
                if not k:
                    # 空行
                    continue
                dic[k] = v
            except StopIteration:
                # 结束
                break
