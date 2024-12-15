from kafka import KafkaProducer
import cv2
import time

BROKER = 'localhost:9092'
TOPIC = 'video_topic'
VIDEO_FILE = 'input_video.mp4'

def video_stream_to_kafka(video_path):
    producer = KafkaProducer(bootstrap_servers=BROKER)
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        producer.send(TOPIC, buffer.tobytes())
        time.sleep(0.03)
    cap.release()
    producer.close()

video_stream_to_kafka(VIDEO_FILE)
