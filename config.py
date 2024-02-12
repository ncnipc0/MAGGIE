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
    # 第1个APP  “北京挂号网V2.0.5”
    {"package": "com.dengtadoctor.bjyuyue", "activity": "com.dengtadoctor.bjyuyue.MainActivity",
     "black_texts": ["确认预约"], "black_ids": [], "black_pages": [["QQ", "微信", "微信朋友圈"]]},
    # 第2个APP  “中国人保V5.27.1”
    {"package": "com.cloudpower.netsale.activity", "activity": "com.picc.aasipods.common.MainActivity",
     "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "联系人"],
     "black_texts": ["添加联系人", "保存"], "black_ids": ["tv_searchTxt", "ll_chat"], "black_pages": [["人保客服", "发送"]]},
    # 第3个APP  “soul V4.24.1”
    {"package": "cn.soulapp.android", "activity": ".h5.activity.H5Activity",
     "black_texts": ["星球", "广场", "发布瞬间", "聊天", "捏脸头像", "怀旧头像"],
     "black_ids": [], "black_pages": []},
    # 第4个 去哪儿网
    {
        "package": "com.Qunar", "activity": "com.mqunar.atom.alexhome.ui.activity.MainActivity",
        "black_texts": ["退出登录", "个人信息导出", "获取验证码", "首页", "旅行攻略", "厦门", "订单", "签到", "我的钱包", "财富赚钱", "拿去花", "信用贷", "白金卡",
                        "立即领取", "验证码"],  # 从“我的”开始测试
        "white_texts": ["订单", "我的", "信息", "个人", "联系人", "信息", "支付设置", "实名", "账单"],  #
        "black_ids": [], "black_pages": [["去哪儿官方客服"], ["个人信息导出", "确认发送"], ["看世界"], ["消息中心"], ["新增常用旅客", "输入"]]},
    # 完整信息
    # 第5个 携程
    {
        "package": "ctrip.android.view", "activity": "ctrip.android.publicproduct.home.view.CtripHomeActivity",
        "black_texts": ["首页", "社区", "消息", "注销账户", "财富赚钱", "创建路线", "获取验证码", "会员", "隐私设置", "个人信息导出", "拿去花",
                        "信用贷", "拿去花", "财富赚钱", "信用卡", "去开通", "商城", "借", "贷", "抵押",
                        "个人主页", "信用贷", "白金卡", "添加", "删除", "银行卡认证", "证件照片", "修改实名"],  # 从我的页面开始测试
        "white_texts": ["现金", "银行卡", "订单", "我的", "信息", "个人", "联系人", "信息", "实名", "账单", "订单", "用户"],  #
        "black_ids": [],
        "black_pages": [["领券中心"], ["我的行程", "关注航班"], ["账号注销"], ["手机号查单"], ["我的积分"], ["浏览历史", "清空"],
                        ["酒店", "机票", "火车票"], ["程信分"], ["您已实名认证"]],
        "order": ["首页", "#机票", "#查 询", ":", "知道", "订"]  # 特殊流程
    },
    # 第6个 云闪付
    {
        "package": "com.unionpay", "activity": "com.unionpay.activity.UPActivityMain",
        "black_texts": ["退出登录", "金融", "消息", "生活", "首页", "积分", "奖励", "信贷", "管家"],
        "black_ids": [], "black_pages": [["中国银联在线客服"]]
    },
    # 第7个 alipay
    {
        "package": "com.eg.android.AlipayGphone", "activity": "com.eg.android.AlipayGphone.AlipayLogin",
        "black_texts": ["退出登录", "长辈模式", "首页", "理财", "生活", "消息", "余额宝", "花呗", "蚂蚁保", "相互宝", "客服"],
        "black_ids": [""], "black_pages": [["我的客服", "发送"], ["蚂蚁保"], ["花呗"], ["安全中心"]]
    },
    # 第8个 airchina
    {
        "package": "com.rytong.airchina", "activity": "com.rytong.airchina.unility.home.activity.HomeActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心", "搜索", "我的低价", "提交", "发票抬头"],
        "white_texts": ["银行卡", "我", "保险", "邮寄地址", "我的", "信息", "个人", "订单", "购买", "修改", "设置"],
        "black_ids": [""], "black_pages": [["搜索"], ["日期选择"], ["全球服务热线"], ["添加常用乘机人"]],
        "start_point": "我的"
    },  # 删除了“查询” black页面
    # 9 南航
    {
        "package": "com.csair.mbp", "activity": "com.csair.mbp.launcher.hybrid.CommonHybridActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "朋友"
                              "进入会议"
                              "设备管理",
                        "安装",
                        "下载",
                        "我的小程序"],  # 百度网盘设备管理页面有bug
        "white_texts": [],
        "black_ids": [""], "black_pages": [],
    },
    # 10花小猪
    {
        "package": "com.huaxiaozhu.rider", "activity": "com.huaxiaozhu.sdk.app.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "朋友"
                              "进入会议"
                              "设备管理",
                        "安装",
                        "下载",
                        "我的小程序"],  # 百度网盘设备管理页面有bug
        "white_texts": [],
        "black_ids": [""], "black_pages": [["隐私号码保护", "守护人", "一键报警"]],
    },
    # 11淘宝
    {
        "package": "com.taobao.taobao", "activity": "com.taobao.tao.welcome.Welcome",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "朋友"
                              "进入会议"
                              "设备管理",
                        "安装",
                        "下载",
                        "我的小程序"],  # 百度网盘设备管理页面有bug
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "联系人"],
        "black_ids": [""], "black_pages": [],
    },
    # 12 应用宝
    {
        "package": "com.tencent.android.qqdownloader", "activity": "com.tencent.assistantv2.activity.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送",
                        "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"
                        ],  # 百度网盘设备管理页面有bug
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
    },
    # 13 滴答出行 com.didapinche.booking
    {
        "package": "com.didapinche.booking", "activity": "com.didapinche.booking.home.activity.IndexNewActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送",
                        "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"
                        ],  # 百度网盘设备管理页面有bug
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
    },
    # 14 高德 com.autonavi.minimap/com.autonavi.map.activity.NewMapActivity
    {
        "package": "com.autonavi.minimap", "activity": "com.autonavi.map.activity.NewMapActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"
                        ],
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": [("我的", 2)]
    },
    # 15 e le me
    {
        "package": "me.ele", "activity": "me.ele.Launcher",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"
                        ],
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 16 菜鸟 com.cainiao.wireless/com.cainiao.wireless.homepage.view.activity.HomePageActivity
    {
        "package": "com.cainiao.wireless", "activity": "com.cainiao.wireless.homepage.view.activity.HomePageActivity",
        "black_texts": ["长辈模式", "版本切换", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"
                        ],
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全", "设置"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 17  12306 com.MobileTicket/com.MobileTicket.ui.activity.MainActivity
    {
        "package": "com.MobileTicket", "activity": "com.MobileTicket.ui.activity.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # com.jd.jrapp / com.jd.jrapp.bm.mainbox.main.MainActivity
    # 18 京东金融
    # com.jd.jrapp/com.jd.jrapp.bm.mainbox.main.MainActivity}
    {
        "package": "com.jd.jrapp", "activity": "com.jd.jrapp.bm.mainbox.main.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["", "我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 19 58
    {
        "package": "com.wuba", "activity": "com.wuba.home.activity.HomeActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 20 weibo com.sina.weibo/com.sina.weibo.MainTabActivity
    {
        "package": "com.sina.weibo", "activity": "com.sina.weibo.MainTabActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["我", "证件", "我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡", "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 21 qunaer com.Qunar/com.mqunar.atom.alexhome.ui.activity.MainActivity
    {
        "package": "com.Qunar", "activity": "com.mqunar.atom.alexhome.ui.activity.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["常用信息", "用户", "我", "证件", "我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡",
                        "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 22 taopiaopiao com.taobao.movie.android/com.taobao.movie.android.app.home.activity.MainActivity
    {
        "package": "com.taobao.movie.android", "activity": "com.taobao.movie.android.app.home.activity.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["常用信息", "用户", "我", "证件", "我的", "信息", "个人", "订单", "常用信息", "编辑", "联系人", "实名", "钱包", "银行卡",
                        "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 23 com.baidu.searchbox/com.baidu.searchbox.MainActivity
    {
        "package": "com.baidu.searchbox", "activity": "com.baidu.searchbox.MainActivity",
        "black_texts": ["退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑", "联系人", "实名", "钱包",
                        "银行卡",
                        "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 24 番茄阅读 com.dragon.read/com.dragon.read.pages.main.MainFragmentActivity
    {
        "package": "com.dragon.read", "activity": "com.dragon.read.pages.main.MainFragmentActivity",
        "black_texts": ["协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑", "联系人", "实名",
                        "钱包", "银行卡",
                        "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 25 booking com.booking/com.booking.profile.presentation.EditProfileActivity
    {
        "package": "com.booking", "activity": "com.booking.profile.presentation.EditProfileActivity",
        "black_texts": ["协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑", "联系人", "实名",
                        "钱包", "银行卡",
                        "账号与安全"],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 26 com.lingan.seeyou/com.lingan.seeyou.ui.activity.main.SeeyouActivity
    {
        "package": "com.lingan.seeyou", "activity": "com.lingan.seeyou.ui.activity.main.SeeyouActivity",
        "black_texts": ["协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },

    # 27 com.lingan.seeyou/com.lingan.seeyou.ui.activity.main.SeeyouActivity
    {
        "package": "com.lingan.seeyou", "activity": "com.lingan.seeyou.ui.activity.main.SeeyouActivity",
        "black_texts": ["呼叫", "预约", "协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 28  com.qiyi.video/com.qiyi.video.WelcomeActivity
    {
        "package": "com.qiyi.video", "activity": "com.qiyi.video.WelcomeActivity",
        "black_texts": ["随刻视频", "会员中心", "发现", "呼叫", "预约", "协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 29 hello com.jingyao.easybike/com.hellobike.atlas.business.portal.PortalActivity
    {
        "package": "com.jingyao.easybike", "activity": "com.hellobike.atlas.business.portal.PortalActivity",
        "black_texts": ["提交订单", "随刻视频", "会员中心", "发现", "呼叫", "预约", "协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["租车", "账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息",
                        "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 30  com.ss.android.article.news/com.ss.android.article.news.activity.MainActivity
    {
        "package": "com.ss.android.article.news", "activity": "com.ss.android.article.news.activity.MainActivity",
        "black_texts": ["提交订单", "随刻视频", "会员中心", "发现", "呼叫", "预约", "协议", "退出登录", "首页", "行程", "发现", "凤凰知音", "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 31 com.pingan.lifeinsurance/com.pingan.lifeinsurance.shell.activity.HomePageActivity
    {
        "package": "com.pingan.lifeinsurance", "activity": "com.pingan.lifeinsurance.shell.activity.HomePageActivity",
        "black_texts": ["版本切换", "提交订单", "随刻视频", "会员中心", "发现", "呼叫", "预约", "协议", "退出登录", "首页", "行程", "发现", "凤凰知音",
                        "金币中心",
                        "消息", "发送", "安装",
                        "下载", "进入", "试玩", "预约", "秒玩", "安装", "打开", "110", "报警"],
        "white_texts": ["账号与安全", "实名", "支付管理", "#我#", "订单", "常用信息", "用户", "证件", "设置", "#我的#", "信息", "个人", "常用信息", "编辑",
                        "联系人", "实名", "钱包", "银行卡",
                        ],
        "black_ids": [""], "black_pages": [],
        "init_oper": []
    },
    # 32 美图 com.mt.mtxx.mtxx/com.mt.mtxx.mtxx.MainActivity
    {
        "package": "com.mt.mtxx.mtxx", "activity": "com.mt.mtxx.mtxx.MainActivity",
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
    # 33 平安健康 com.pingan.papd/com.pingan.papd.ui.activities.main.MainActivityNew
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
