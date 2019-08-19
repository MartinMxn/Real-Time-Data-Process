# need to read from kafka topic,
# need to write to cassandra table
# start: with python data-storage.py stock-analyzer 192.168.99.100

import json
import logging
import argparse
import atexit

from cassandra.cluster import Cluster
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-producer')

# mode: TRACE, DEBUG, INFO, WARNING
logger.setLevel(logging.DEBUG)


topic_name = 'stock-analyzer'
kafka_broker = '127.0.0.1"9092'
keyspace = 'stock'
data_table = ''
cassandra_broker = '127.0.0.1:9042'


def persist_data(stock_data, cassandra_session):
    """
    :param stock_data:
    :param cassandra_session: a session created with cassandra-driver
    :return:
    """
    logger.debug('Start to persist data to cassandra%s', stock_data)
    parsed = json.loads(stock_data)[0]
    symbol = parsed.get('StockSymbol')
    price = float(parsed.get('LastTradePrice'))
    tradetime = parsed.get('LastTradeDateTime')
    statement = "INSERT INTO %s (stock_symbol, trade_time, trade_price) VALUES ('%s', '%s', '%f')" % (data_able, symbol, tradetime, price)
    cassandra_session.execute(statement)
    logger.info('Persisted data into cassandra for symbol: %s, price %f, tradetime %s' % (symbol, price, tradetime))


def shutdown_hook(consumer, session):
    consumer.close()
    logger.info('Kafka consumer closed')
    session.shutdown()
    logger.info('Cassandra session closed')


if __name__ == '__main__':
    # setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help="the kafka topic")
    parser.add_argument('kafka_broker', help='the location of kafka broker')
    parser.add_argument('keyspace', help='the keyspace to be used in cassandra')
    parser.add_argument('data_able', help='data table to be used')
    # assume cassandra_broker is '127.0.0.1, 127.0.0.2' -> ['127.0.0.1', '127.0.0.2']
    parser.add_argument('cassandra_broker', help='the location of cassandra cluster')

    # parse argument
    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    keyspace = args.keyspace
    data_able = args.data_able
    cassandra_broker = args.cassandra_broker

    # setup a kafka consumer
    consumer = KafkaConsumer(topic_name, boostrap_servers=kafka_broker)

    # setup a cassandra session
    cassandra_cluster = Cluster(contact_points=cassandra_broker.split(','))
    session = cassandra_cluster.connect(keyspace)

    atexit.register(shutdown_hook, consumer, session)

    for msg in consumer:
        persist_data(msg.value, session)
