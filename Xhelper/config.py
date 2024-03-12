import sys

# Test equipment serial number
serials = ["98241FFAZ000NH", "99231FFAZ003FN", "98EBB23602201354"]

CONFIG = {
    "serial": None,
    "phone_no": None,
    "app_no": None,  # Which APP to choose as the test object
    "auto_authentication": False,
    "always_detection": True,
    "optimization": True,
    "special_detect": False,
    "ui_wait_timeout": 10.0,  # Implicit wait time (seconds)
    "max_retry_times": 0,  # Maximum attempts
    "sim_threshold": 0.8,
    "no_page_retry": 0,  # The number of times a page waits without a root node
    "no_data_retry": 1,  # Waiting times with too little page content
}

# Log Configuration
LOG_CONFIG = {
    "handlers": [
        dict(sink=sys.stdout, level="DEBUG"),
        dict(sink='logs/{time}.log', retention=10, level="DEBUG"),
    ],
    "levels": [dict(name="STACK", no=13, color="<yellow>")],
    "activation": [
        ("Scanner", True),
        ("APPRunner", True),
        ("STElement", True),
        ("Detector", True),
        ("PageStorage", True),
        ("CompareUtil", True)
    ],
}



# 日志配置(不记录日志文件)
LOG_CONFIG_NO_FILE = {
    "handlers": [
        dict(sink=sys.stdout, level="DEBUG"),
    ],
    "levels": [dict(name="STACK", no=13, color="<yellow>")],
}

white_list = ["我的", "信息", "个人", "订单", "常用信息", "联系人", "支付设置", "实名", "账单", ]

appList = [

    {
        "package": "com.pingan.papd", "activity": "com.pingan.papd.ui.activities.main.MainActivityNew",
        "black_texts": ["退出", "切换", "注销", "版本切换", "提交订单", "随刻视频", "会员中心", "发现", "呼叫", "预约", "协议", "退出登录", "首页", "行程",
                        "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号管理", "账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人",
                        "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡", "地址"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },

]

APP = None

# def union_list(key,flag=True):
#     if not flag:
#         l = []
#         for i in appList:
#             if key in i:
#                 l+=i[key]
#         for i in appList:
#             i[key] = l
#         return
#
#     s = set()
#     for i in appList:
#         if key in i:
#             # print(set(i["white_texts"]))
#             s = s.union(set(i[key]))
#     l = list(s)
#     for i in appList:
#         i[key] = l

# union_list("white_texts")
# union_list("black_texts")
# union_list("black_pages", False)
