# Real-Time-Data-Process

## Docker virtual machine init
```
docker-machine create --driver virtualbox --virtualbox-cpu-count 2 --virtualbox-memory 2048 bigdata

create a vm named bigdata, the following step is creating the different container
```
```
docker run -> to create a container
docker start -> to start a container
docker ps (-a) -> check all container
docker stop $CONTAINER_ID -> stop a container
docker rm $CONTAINER_ID -> delete a container
docker start/restart $CONTAINER_ID
docker-machine start bigdata # do this when long time no action
```

### Get vm ip
```
docker-machine ip bigdata
```

## eval $(docker-machine env bigdata)
```
!! Necessary
每一个新的terminal窗口都需要输入这个命令
zookeeper kafka都需要先打这个
connect docker client(command line) with server
```

## run the docker container
```
app1 = zookeeper
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 confluent/zookeeper # restart

docker images
docker ps 
# to check

app2 = kafka
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=`docker-machine ip bigdata` -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=`docker-machine ip bigdata` -e KAFKA_ADVERTISED_PORT=9092 confluent/kafka

app3 = cassandra
```

## Zookeeper
```
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper

docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 confluent/zookeeper (second time)

Download using shell commands (MacOS, Linux, Unix)
○ wget http://apache.mirrors.ionfish.org/zookeeper/....  # based on current version
○ tar xvf zookeeper-3.4.8.tar.gz
○ mv zookeeper-3.4.8 zookeeper
○ rm zookeeper-3.4.8.tar.gz

● cd zookeeper/bin (MacOS, Linux, Unix)
● ./zkCli.sh -server `docker-machine ip bigdata`:2181 # type enter after this 

[zk: 192.168.99.101:2181(CONNECTED) 0] ls /
[zookeeper]
[zk: 192.168.99.101:2181(CONNECTED) 1] ls /zookeeper
[quota]
[zk: 192.168.99.101:2181(CONNECTED) 2] get /zookeeper/quota
cZxid = 0x0 #时间序列id
ctime = Thu Jan 01 08:00:00 CST 1970
mZxid = 0x0
mtime = Thu Jan 01 08:00:00 CST 1970
pZxid = 0x0
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 0
numChildren = 0
一般把zookeeper和kafka放在不同集群防止同时crash

Create node
● create /workers "name"  # -e to create ephemeral node
● ls /
● ls /workers
● get /workers

Delete node
delete /workers

Set watcher
get /workers true
```

## Kafka
```
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=`docker-machine ip bigdata` -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka

docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=192.168.99.101 -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka

192.168.99.101

Create Kafka Topic
./kafka-topics.sh --create --zookeeper `docker-machine ip bigdata` --replication-factor 1 --partitions 1 --topic bigdata
./kafka-topics.sh --create --zookeeper `docker-machine ip bigdata` --replication-factor 1 --partitions 1 --topic stock-analyzer
check on zookeeper
● ./zkCli.sh -server `docker-machine ip bigdata`:2181
● ls /


Produce Messages
./kafka-console-producer.sh --broker-list `docker-machine ip bigdata`:9092 --topic bigdata


Consume Messages
./kafka-console-consumer.sh --bootstrap-server 192.168.99.101:9092 --topic bigdata
./kafka-console-consumer.sh --bootstrap-server 192.168.99.101:9092 --topic bigdata --from-beginning # read all message from beginning of producers

then type sth in producer terminal, message will appears in consume terminal


Check Kafka Broker
docker exec -it kafka bash
cd /var/lib/kafka
ls
# exit 退出docker container，command+c有时不行
```

## Cassandra
For data persist
```
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:3.11

docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 cassandra:3.11

./cqlsh `docker-machine ip bigdata` 9042

Create Keyspace -> like database
● ./cqlsh `docker-machine ip bigdata` 9042
CREATE KEYSPACE -> like table
● CREATE KEYSPACE “stock” WITH replication = {'class': 'SimpleStrategy', 'replication_factor':
1} AND durable_writes = 'true';
● USE stock;
● DESCRIBE KEYSPACE;

Create Table
● CREATE TABLE user ( first_name text, last_name text, PRIMARY KEY (first_name));
● DESCRIBE TABLE user;

Insert Data
● INSERT INTO user (first_name, last_name) VALUES ('martin', 'm');

Query Data
● SELECT COUNT (*) FROM USER;
● SELECT * FROM user WHERE first_name='martin'; 
● SELECT * FROM user WHERE last_name='barney';

Look Into Cassandra Node
● docker exec -it cassandra bash
● cd /var/lib/cassandra 
● ls

Delete Data
● DELETE last_name FROM user WHERE first_name='martin'; # only delete the last_name column
● DELETE FROM user WHERE first_name='uncle';

Remove Table
● TRUNCATE user; # clear the table
● DROP TABLE user;
```

# Docker structure
## client-server mode
client is command line, server is docker daemon, registry is to store images  

## Logging
```
log make your life goes smoothly
sometimes, logging is not enough in distributed system
-> tracing tool
```