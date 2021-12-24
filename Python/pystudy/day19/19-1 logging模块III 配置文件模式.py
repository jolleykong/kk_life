# 高级方法 logging配置文件
'''
有的同学习惯通过logger的对象配置去完成日志的功能，没问题，
但是上面这种方式需要创建各种对象，比如logger对象，
fileHandler对象，ScreamHandler对象等等，比较麻烦，

那么下面提供一种字典的方式，创建logger配置文件，这种才是工作中经常使用的实现日志功能的方法，真正的做到   ----- 拿来即用（简单改改）。
'''
"""
logging配置
"""

import os
import logging.config

# 定义三种日志输出格式 开始

standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                  '[%(levelname)s][%(message)s]' #其中name为getlogger指定的名字

simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'

id_simple_format = '[%(levelname)s][%(asctime)s] %(message)s'

# 定义日志输出格式 结束

logfile_dir = os.path.dirname(os.path.abspath(__file__))  # log文件的目录

logfile_name = 'all2.log'  # log文件名

# 如果不存在定义的日志目录就创建一个
if not os.path.isdir(logfile_dir):
    os.mkdir(logfile_dir)

# log文件的全路径
logfile_path = os.path.join(logfile_dir, logfile_name)

# log配置字典
LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format
        },
        'simple': {
            'format': simple_format
        },
    },
    'filters': {},
    'handlers': {
        #打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'simple'
        },
        #打印到文件的日志,收集info及以上的日志
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'formatter': 'standard',
            'filename': logfile_path,  # 日志文件
            'maxBytes': 1024*1024*5,  # 日志大小 5M
            'backupCount': 5,
            'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
        },
    },
    'loggers': {
        #logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['default', 'console'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
            'level': 'DEBUG',
            'propagate': True,  # 向上（更高level的logger）传递
        },
    },
}


def load_my_logging_cfg():
    logging.config.dictConfig(LOGGING_DIC)  # 导入上面定义的logging配置
    logger = logging.getLogger(__name__)  # 生成一个log实例
    logger.info('It works!')  # 记录该文件的运行状态

if __name__ == '__main__':
    load_my_logging_cfg()

# 如何拿到logger对象的详细解释
'''
注意注意注意：


#1、有了上述方式我们的好处是：所有与logging模块有关的配置都写到字典中就可以了，更加清晰，方便管理


#2、我们需要解决的问题是：
    1、从字典加载配置：logging.config.dictConfig(settings.LOGGING_DIC)

    2、拿到logger对象来产生日志
    logger对象都是配置到字典的loggers 键对应的子字典中的
    按照我们对logging模块的理解，要想获取某个东西都是通过名字，也就是key来获取的
    于是我们要获取不同的logger对象就是
    logger=logging.getLogger('loggers子字典的key名')

    
    但问题是：如果我们想要不同logger名的logger对象都共用一段配置，那么肯定不能在loggers子字典中定义n个key   
 'loggers': {    
        'l1': {
            'handlers': ['default', 'console'],  #
            'level': 'DEBUG',
            'propagate': True,  # 向上（更高level的logger）传递
        },
        'l2: {
            'handlers': ['default', 'console' ], 
            'level': 'DEBUG',
            'propagate': False,  # 向上（更高level的logger）传递
        },
        'l3': {
            'handlers': ['default', 'console'],  #
            'level': 'DEBUG',
            'propagate': True,  # 向上（更高level的logger）传递
        },

}

    
#我们的解决方式是，定义一个空的key
    'loggers': {
        '': {
            'handlers': ['default', 'console'], 
            'level': 'DEBUG',
            'propagate': True, 
        },

}

这样我们再取logger对象时
logging.getLogger(__name__)，不同的文件__name__不同，这保证了打印日志时标识信息不同，但是拿着该名字去loggers里找key名时却发现找不到，于是默认使用key=''的配置


'''