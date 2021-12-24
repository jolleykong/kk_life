# 中级模式
'''
logging库提供了多个组件：Logger、Handler、Filter、Formatter。
    Logger对象提供应用程序可直接使用的接口，
    Handler发送日志到适当的目的地，
    Filter提供了过滤日志信息的方法，
    Formatter指定日志显示格式。
    另外，可以通过：
        logger.setLevel(logging.Debug)设置级别,
        当然，也可以通过
        fh.setLevel(logging.Debug)单对文件流设置某个级别。
'''

import logging

logger = logging.getLogger()
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('test.log',encoding='utf-8') 

# 再创建一个handler，用于输出到控制台 
ch = logging.StreamHandler() 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setLevel(logging.DEBUG)

fh.setFormatter(formatter) 
ch.setFormatter(formatter) 
logger.addHandler(fh) #logger对象可以添加多个fh和ch对象 
logger.addHandler(ch) 

logger.debug('logger debug message') 
logger.info('logger info message') 
logger.warning('logger warning message') 
logger.error('logger error message') 
logger.critical('logger critical message')
