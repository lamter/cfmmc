from selenium import webdriver

# 中国期货监控中心-投资者查询服务系统
cfmmcUrl = 'https://investorservice.cfmmc.com'

# 登陆
class DailySettlement(object):
    def __init__(self):
        super(DailySettlement, self).__init__()

        # 浏览器实例
        self.brower = webdriver.Chrome()

    def login(self):
        brower.get(cfmmcUrl)