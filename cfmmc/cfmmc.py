import datetime

import time
import traceback
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from .code import *
from .table import *

# 中国期货监控中心-投资者查询服务系统
cfmmcUrl = 'https://investorservice.cfmmc.com'


class NotRegistered(Exception):
    pass


class DailySettlementQueryError(Exception):
    pass


class CfmmcBrowser(object):
    def __init__(self, userID, password, saveto='./'):
        super(CfmmcBrowser, self).__init__()

        self.userID = userID
        self.password = password
        self.saveto = saveto

        # 浏览器实例
        self.browser = webdriver.Chrome()

        # 表格
        self.dailySettlementBalanceTable = DailySettlementBalanceTable(self.userID, self.saveto)

    def login(self):
        """
        进行登陆
        :return: bool(是否登录成功)
        """

        # 打开页面
        self.browser.get(cfmmcUrl)
        # 输入账号密码
        userID = self.browser.find_element_by_name('userID')
        userID.clear()
        userID.send_keys(self.userID)
        self.browser.find_element_by_name('password').send_keys(self.password)

        # 手动输入验证码
        vericode = input('请手动输入验证码:')
        self.browser.find_element_by_name('vericode').send_keys(vericode)

        # 登陆
        self.browser.find_element_by_name('imageField2').submit()

        # 登陆成功
        try:
            title = self.browser.find_element_by_class_name('page-title-text').text
            return '客户交易结算日报' in title
        except:
            return False

    @classmethod
    def downloadDailySettlement(cls, userID, password, saveto):
        """

        :param userID:
        :param password:
        :return:
        """
        ds = cls(userID, password, saveto=saveto)
        # 登陆
        while True:
            if ds.login():
                break
            else:
                print('验证码错误，重新输入')

        # 下载
        ds._downloadDailySettlement()

    def _downloadDailySettlement(self):
        """
        执行下载每日结算
        :return:
        """
        # 从前一天开始回溯查询
        startDate = datetime.date.today()
        now = datetime.datetime.now()

        if now.time() > datetime.time(17):
            # 下午5点就可以查询当天数据了
            pass
        else:
            # 否则只能从前一天开始查询
            startDate -= datetime.timedelta(days=1)

        def dates():
            preDays = 0
            while True:
                yield startDate - datetime.timedelta(days=preDays)
                preDays += 1

        try:
            for d in dates():
                # 逐天下载
                if d == self.dailySettlementBalanceTable.lastDate:
                    # 已经是最新的数据量
                    break
                self.dailySettlementBalanceTable.setCurrentDate(d)
                self.downloadSettlementByDate(d)
                time.sleep(0.2)
        except NotRegistered:
            # 查询结束
            pass
        except DailySettlementQueryError:
            traceback.print_exc()
            raise

        # 将数据进行保存
        self.dailySettlementBalanceTable.dump()

    def downloadSettlementByDate(self, date):
        """

        :param date:
        :return:
        """
        # 提交查询
        customerForm = self.browser.find_element_by_name('customerForm')
        tradeDate = customerForm.find_element_by_name('tradeDate')
        tradeDate.clear()
        assert isinstance(date, datetime.date)
        tradeDate.send_keys(date.strftime('%Y-%m-%d'))
        tradeDate.submit()

        # 检查错误提示
        code = self.checkDailySettlementQueryNotice()
        # 查询每日交易的返回状态
        if code == DAILY_SETTLEMENT_RESULT_CODE_OK:
            pass  # 正常，继续查询
        elif code == DAILY_SETTLEMENT_RESULT_CODE_UNKNOW:
            raise DailySettlementQueryError()  # 未知错误
        elif code == DAILY_SETTLEMENT_RESULT_CODE_NOT_TRADE:
            return  # 非交易日，返回查询另一个交易日
        elif code == DAILY_SETTLEMENT_RESULT_CODE_NOT_REGISTER:
            raise NotRegistered()  # 注册日

        # 获取查询数据
        self.filterDailySettlementsQueryResult()

    def checkDailySettlementQueryNotice(self):
        """
        检查错误提示
        :return:
        """
        try:
            noticeEle = self.browser.find_element_by_id('waitBody').find_element_by_tag_name('li')
            if '的交易结算报告，原因是期货公司未向监控中心报送该日数据' in noticeEle.text:
                code = DAILY_SETTLEMENT_RESULT_CODE_NOT_REGISTER
            elif '为非交易日，请重新选择交易日期' in noticeEle.text:
                code = DAILY_SETTLEMENT_RESULT_CODE_NOT_TRADE
            else:
                # 未知异常
                code = DAILY_SETTLEMENT_RESULT_CODE_UNKNOW
            print(noticeEle.text)
        except NoSuchElementException:
            # 无公告
            code = DAILY_SETTLEMENT_RESULT_CODE_OK
        return code

    def filterDailySettlementsQueryResult(self):
        """
        筛选出查询结果
        :return:
        """
        tbodies = self.browser.find_elements_by_tag_name('tbody')
        for tbody in tbodies:
            try:
                if not self.dailySettlementBalanceTable.isThisTable(tbody):
                    continue
            except NoSuchElementException:
                continue

            # 加载表格中的数据
            self.dailySettlementBalanceTable.load(tbody)
