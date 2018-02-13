import detections as dt
import os
import sys
import json
from time import sleep
from confluent_kafka import Consumer, Producer, KafkaError, avro, KafkaException, TopicPartition
from confluent_kafka.avro import AvroProducer
from requests.exceptions import ConnectionError as CE
import read
import urllib.request
import image_process


def process(image_url):

    filename = image_url.split('/')[-1]

    download_image(image_url)

    ### generate readable data format from image
    image_process.main(filename)

    ### detect face from image and save data
    dt.eval(t, f)

    ### detect the angle of each face
    dt.test_model(angle_model)
    ### remove tested image
    
    os.system("rm garconsdata/JPEGImages/%s" % filename)
    
    ### 2018.01 JAEHONG KIM

def download_image(image_url):

    filename = image_url.split('/')[-1]
    with open('./garconsdata/JPEGImages/{}'.format(filename), 'wb') as f:
        f.write(urllib.request.urlopen(image_url).read())

class KafkaServerConnector:
    def __init__(self):
        value_schema = avro.load('value.avsc')
        image_schema = avro.load('image.avsc')
        self.bootstrap_server = '10.33.44.185:29092, 10.33.44.185:39092, 10.33.44.185:19092'
        schema_url = 'http://10.33.44.185:8081'
        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_server,
            'client.id': 'image_consumer_1',
            'group.id': 'image_consumer_group_1',
            'auto.offset.reset': 'smallest'
        })
        self.consumer.subscribe(['face_detection'])
        
        self.face_producer = AvroProducer({
            'client.id':'face_producer_1',
            'bootstrap.servers': self.bootstrap_server,
            'schema.registry.url': schema_url
        }, default_value_schema=value_schema)
        
        self.image_producer = AvroProducer({
            'client.id':'image_producer_2',
            'bootstrap.servers': self.bootstrap_server,
            'schema.registry.url': schema_url
        }, default_value_schema=image_schema)

        for i in range(5):
            print(self.consumer.committed([TopicPartition('face_detection', i)]))

    def make_response(self, msg):
        msg_json = msg.value().decode('utf-8')
        data = json.loads(msg_json)
        for i in range(5):
             print(self.consumer.committed([TopicPartition('face_detection', i)]))
        print("Consumed message {}".format(msg_json))
        pk = data['pk']
        image_url = data['image']

        process(image_url)

        detection_list = read.read()
        result_faces = []

        for t in detection_list:
            result_face = {
                'image_id': pk,
                'status': 0,
                'x1': t[1][0],
                'y1': t[1][1],
                'x2': t[2][0],
                'y2': t[2][1],
                'x3': t[3][0],
                'y3': t[3][1],
                'angle': t[0]
            }
            result_faces.append(result_face)
        
        result_image = {
            'id': pk,
            'is_detected': True
        }

        for face in result_faces:
            self.face_producer.produce(topic='core_babyface', value=face)
        self.face_producer.flush()

        self.image_producer.produce(topic='core_babyimage', value=result_image)
        self.image_producer.flush()

        print("Produced Messages")


    def start(self):
        print('start')
        try:
            while True:
                print('Running....')
                msg = self.consumer.poll()
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue

                    elif msg.error():
                        raise KafkaException(msg.error())

                else:
                    response_msg_value = self.make_response(msg)

        except KeyboardInterrupt:
            pass
        
        self.consumer.close()

if __name__ == '__main__':
    t,f = dt.construct_model1()
    angle_model = dt.construct_model2()

    wrapper = KafkaServerConnector()
    wrapper.start()

