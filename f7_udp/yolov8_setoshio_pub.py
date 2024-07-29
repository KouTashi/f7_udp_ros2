import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32MultiArray

import cv2
import numpy as np
from ultralytics import YOLO


# Load the YOLOv8 model
model = YOLO('/home/ubuntu/ros2_ws/src/f7_udp/f7_udp/bestv2.pt')#絶対パス
# Export the model
model.export(format="openvino")  # creates 'yolov8n_openvino_model/'
# Load the exported OpenVINO model
ov_model = YOLO("/home/ubuntu/ros2_ws/src/f7_udp/f7_udp/bestv2_openvino_model/")#絶対パス
# Open the video file
cap = cv2.VideoCapture(0)#builtin_cam:0 ext_cam:2

msg = Int32MultiArray()


class setoshio_pub(Node):

    def __init__(self):
        super().__init__('yolov8_setoshio')
        self.publisher_ = self.create_publisher(Int32MultiArray, 'setoshio_pub', 10)
        freq = 0.001  # seconds
        self.timer = self.create_timer(freq, self.timer_callback)
        #self.i = 0

    def timer_callback(self):#callback for publishing setoshio data
        
        #>>>>>>>>>>>>>>>>>>>>>>Write your code from here>>>>>>>>>>>>>>>>>>>>>>#
        #callbacked every freq[s]
        
        #-------------------------YOLOv8-------------------------#
        success, frame = cap.read()

        if success:
            #Run YOLOv8 inference on the frame
            results = ov_model.predict(frame,verbose=False)#verbose: Option for show output to terminal
            annotatedFrame = results[0].plot()
            
            '''
            # 後のオブジェクト名出力などのため
            names = results[0].names
            classes = results[0].boxes.cls
            boxes = results[0].boxes
            
            
            for box, cls in zip(boxes, classes):
                name = names[int(cls)]
                #x1 =  boxes[int[box]]
                x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
                #print(f"Box coordinates: {box}, Object: {class_name}")
                print(str(name)+str(x1))
            
            for box in boxes:
                print(str(box.xyxy[0]) + str(box.xyxy[1]))   
            # Display the annotated frame
            '''

            #cls_and_box = list(zip(np.int32(results[0].boxes.cls), np.int32(results[0].boxes.xyxy)))
            try:
                cls_and_x1 =  list(zip(np.int32(results[0].boxes.cls), np.int32(results[0].boxes.xyxy[0]))) 
                cls_and_x1_sorted = sorted(cls_and_x1, key=lambda x: x[1])#sort with x1
                print(cls_and_x1_sorted)
               
                
                #-------------------------Publish-------------------------#
                '''
                for i in range (len(cls_and_x1_sorted)):
                    msg.data[i] = np.int32(cls_and_x1_sorted[i][0])
                    print(msg.data)
                '''
                msg.data = [-1,-1,-1,-1,-1]
                
                for i in range(len(cls_and_x1_sorted)):
                    msg.data[i] = cls_and_x1_sorted[i][0]

                        
                '''
                msg.data[0] = cls_and_x1_sorted[0][0]
                msg.data[1] = cls_and_x1_sorted[1][0]
                msg.data[2] = cls_and_x1_sorted[2][0]
                msg.data[3] = cls_and_x1_sorted[3][0]
                msg.data[4] = cls_and_x1_sorted[4][0]
                '''
                #msg.data = cls_and_x1_sorted
                self.publisher_.publish(msg)
                
                #self.get_logger().info('Publishing: "%s"' % msg)
                
                #-------------------------End-------------------------#        
                
                #print(str(cls_and_x1_sorted))
            except IndexError as e:#To avoid IndexError stops program
                print(e)
                 
            
            cv2.imshow("YOLOv8", annotatedFrame)
            #print(str(results[0].boxes))
            
            #setoshio_pub.yolov8_callback() #callback to publish setoshio data

                    # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                    # Release the video capture object and close the display window
                cap.release()
                cv2.destroyAllWindows()
                #break
        
        #-------------------------End-------------------------#
        

        
        #>>>>>>>>>>>>>>>>>>>>>>End>>>>>>>>>>>>>>>>>>>>>>#
        
def main(args=None):
    rclpy.init(args=args)
    setoshio_publisher = setoshio_pub()
    rclpy.spin(setoshio_publisher)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    setoshio_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
