# -*- coding: utf-8 -*-

# 指定kafka集群和topic发送event
# 指定一个股票 每秒抓取一次股票信息
from kafka import KafkaProducer
from googlefinance import getQuotes
import argparse
import json
import time
import logging

# default kafka setting
topic_name = 'stock-analyzer'
kafka_broker = '127.0.0.1:9002'

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')
logger.setLevel(logging.DEBUG)


def fetch_price(producer, symbol):
    """
    helper function to get stock data and send to kafka
    :param producer: instance of kafka producer
    :param symbol: symbol of specific stock
    :return: None
    """
    logger.debug('Start to fetch stock price for %s', symbol)
    price = json.dumps(getQuotes(symbol))  # to py dict
    logger.debug('Get stock info %s', price)
    producer.send(topic = topic_name, value=price, timestamp_ms=time.time)
    logger.debug('Sent stock price for %s to kafka', symbol)

if __name__ == '__main__':
    # setup command line arguments
    parser = argparse.ArgumentParser()
    # 传参示例 symbol=1 topic_name=2 kafka_broker=3
    parser.add_argument('symbol', help='symbol of the stock') # stock symbol
    parser.add_argument('topic_name', help="the kafka topic")
    parser.add_argument('kafka_broker', help='the location of kafka broker')

    args = parser.parse_args()
    symbol = args.symbol
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker

    # initiate a kafka producer
    producer = KafkaProducer(
        bootstrap_servers=kafka_broker,
    )

    fetch_price(producer, symbol)