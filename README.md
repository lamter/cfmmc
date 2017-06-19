# cfmmc
1. 中国期货市场监控中心的浏览器模拟操作。
2. 使用了`selenium`和`Chromedrive`来实现。
3. 已经实现的功能：
    1. 下载每日结算单，默认保存为`csv`文件。根据已有的数据，可以接着下载。

## 准备
 - 安装`selenium-python`
 - 安装`chromedirve`
 - 安装`cfmmc`
```
pip install cfmmc # 从 pypi 安装
# OR
pip install -e . # 从本地项目目录安装
```

## 使用
期货结算中心的登录参见[这里](https://investorservice.cfmmc.com)。
账号密码详询自己的客户经理。

### 下载每日结算数据
```
import cfmmc
dic = {
    'userID':'
}
cfmmc.accounts()


