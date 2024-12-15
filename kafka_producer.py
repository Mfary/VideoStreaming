from kafka import KafkaProducer
import base64
import cv2
import time

BROKER = 'localhost:9092'
TOPIC = 'video_topic'
VIDEO_FILE = 'input_video.mp4'

def video_stream_to_kafka(video_path):
    producer = KafkaProducer(bootstrap_servers=BROKER, value_serializer=lambda v: str(v).encode('utf-8'))
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        producer.send(TOPIC, base64.b64encode(buffer).decode('utf-8'))
        time.sleep(0.03)
    cap.release()
    producer.close()

video_stream_to_kafka(VIDEO_FILE)
