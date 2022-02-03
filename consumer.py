import os
import requests
import json
from pykafka import KafkaClient
import logging.config
import yaml

with open('consumer_log.yaml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger('consumer')

password = os.getenv('FASTAPI_PASSWORD')
client = KafkaClient(hosts="10.1.0.111:9092")

consumer = client.topics["topic-notice", "topic-trade"].get_simple_consumer(
    consumer_group="mygroup",
    reset_offset_on_start=False)

for idx, message in enumerate(consumer):
    logger.debug('received %s' % (message))
    dec_trade = message.decode()
    decoded_trade = json.loads(dec_trade)
    logger.info('the consumer has successfully received trade: %s' % (decoded_trade))
    response_post = requests.post(
        "http://fastapi:8080/send_trade_info",
        json={
            "trade": decoded_trade,
            "password": password
        })

    logger.info('send result decoded_trade: %s, index: %s, status_code: %s, text: %s' % (decoded_trade, idx, response_post.status_code, response_post.text))
    if response_post.ok:
        consumer.commit_offsets()
    else:
        logger.fatal('cannot send result decoded_trade: %s, index: %s, status_code: %s, text: %s' % (decoded_trade, idx, response_post.status_code, response_post.text))
