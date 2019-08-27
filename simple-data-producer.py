# -*- coding: utf-8 -*-

# 指定kafka集群和topic发送event
# 指定一个股票 每秒抓取一次股票信息
# python simple-data-producer.py AAPL

from kafka import KafkaProducer
from googlefinance import getQuotes
from kafka.errors import KafkaError, KafkaTimeoutError
from yfinance import Ticker

import argparse
import json
import time
import logging
import schedule  # better than set time
import atexit  # shut down hook, like runTimeExit in Java and process.exit in Node

# default kafka setting
# topic_name = 'stock-analyzer'
# kafka_broker = '192.168.99.101:9092'

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')

# mode: TRACE, DEBUG, INFO, WARNING
logger.setLevel(logging.DEBUG)


def fetch_price(producer, symbol):
    """
    helper function to get stock data and send to kafka
    :param producer: instance of kafka producer
    :param symbol: symbol of specific stock
    :return: None
    """
    logger.debug('Start to fetch stock price for %s', symbol)
    try:
        ticker_info = Ticker(symbol).info
        price = ticker_info.get('postMarketPrice')
        last_trade_time = ticker_info.get('postMarketTime')

        payload = ('[{"StockSymbol":"%s","LastTradePrice":%s,"LastTradeDateTime":"%s"}]' % (
        symbol, price, time.ctime(last_trade_time))).encode('utf-8')

        logger.debug('Retrieved stock info %s', payload)

        producer.send(topic=topic_name, value=payload, timestamp_ms=int(time.time()))
        logger.debug('Sent stock price for %s to kafka', symbol)
    except KafkaTimeoutError as timeout_error:
        logger.warning('Failed to send stock price for %s to kafka, cauase by %s',(symbol, timeout_error))
    except Exception:
        logger.warning('Failed to get stock price for %s', symbol)


def shutdown_hook(producer):
    try:
        producer.flush(10)  # some message may still not send, give 10s to send
        producer.close()
        logger.info('Finished flushing pending message')
    except KafkaError:
        logger.warning('Failed to flush pending message to kafka')
    finally:
        try:
            producer.close()
            logger.info('Kafka connection closed')
        except Exception as e:
            logger.warning('Failed to close kafka connection')


if __name__ == '__main__':
    # setup command line arguments
    parser = argparse.ArgumentParser()
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

    # test part
    # def test_fetch(symbol):
    #     print(time.ctime(Ticker('AAPL').info.get('postMarketTime')))
    #     print(Ticker('AAPL').info.get('postMarketPrice'))
    #
    # schedule.every(1).second.do(test_fetch, 'AAPL')
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # set up proper shutdown hook
    atexit.register(shutdown_hook, producer)

    # schedule to run every sec
    schedule.every(1).second.do(fetch_price, producer, symbol)

    while True:
        schedule.run_pending()
        time.sleep(1)