from pyspark.sql import SparkSession
from pyspark.sql.types import BinaryType, StructType, StructField
import cv2
import numpy as np

EDGES_OUTPUT_FILE='edges_output.mp4'
FPS = 30
TOPIC = 'video_topic'
BROKER = 'localhost:9092'
FRAME_WIDTH = 640 
FRAME_HEIGHT = 360  

def apply_filters(frame_bytes):
    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray_frame, 100, 200)


    return edges



def process_video_stream():
    spark = SparkSession.builder \
        .appName("VideoStreamProcessor") \
        .getOrCreate()

    schema = StructType([
        StructField("value", BinaryType(), True)
    ])

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", BROKER) \
        .option("subscribe", TOPIC) \
        .load() \
        .selectExpr("CAST(value AS BINARY)")


    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    edges_output_writer = cv2.VideoWriter(EDGES_OUTPUT_FILE, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT), isColor=False)

    def save_processed_frames(rows):
        for row in rows:
            frame_bytes = row['value']
            edge_frame = apply_filters(frame_bytes)

            
            edges_output_writer .write(edge_frame)


    query = df.writeStream \
        .foreachBatch(lambda batch_df, _: save_processed_frames(batch_df.collect())) \
        .start()

    query.awaitTermination()
    edges_output_writer.release()
    print(f"Processed video saved to {EDGES_OUTPUT_FILE}")


process_video_stream()
