from sklearn.metrics.pairwise import pairwise_distances
from tensorflow.python.platform import gfile
from scipy import misc
from collections import defaultdict
from datetime import datetime
import tensorflow as tf
import numpy as np
import detect_and_align
import time
import cv2
import csv
import os

#New branch

class IdData():
    """Keeps track of known identities and calculates id matches"""

    def __init__(self, id_folder, sess, embeddings, images_placeholder,
                 phase_train_placeholder, distance_treshold):
        print('Loading Embeddings: ')
        self.distance_treshold = distance_treshold
        self.id_folder = id_folder
        self.embeddings = np.load(self.id_folder + '/' +  'embeddings.npy')
        self.id_names = list(np.load(self.id_folder + '/' + 'labels_strings.npy'))

    def find_matching_ids(self, embs):
        matching_ids = []
        matching_distances = []
        distance_matrix = pairwise_distances(embs, self.embeddings)
        for distance_row in distance_matrix:
            min_index = np.argmin(distance_row)
            if distance_row[min_index] < self.distance_treshold:
                matching_ids.append(self.id_names[min_index])
                matching_distances.append(distance_row[min_index])
            else:
                matching_ids.append(None)
                matching_distances.append(None)
        return matching_ids, matching_distances


class arguments():
    def __init__(self, model, id_folder, threshold):
        self.model = model
        self.id_folder = id_folder
        self.threshold = threshold


def load_model(model):
    model_exp = os.path.expanduser(model)
    if (os.path.isfile(model_exp)):
        print('Loading model filename: %s' % model_exp)
        with gfile.FastGFile(model_exp, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')
    else:
        raise ValueError('Specify model file, not directory!')


def main(args):
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Graph().as_default():
        with tf.Session(config=config) as sess:

            # Setup models
            mtcnn = detect_and_align.create_mtcnn(sess, None)

            load_model(args.model)
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

            # Load anchor IDs
            id_data = IdData(args.id_folder, sess, embeddings, images_placeholder, phase_train_placeholder, float(args.threshold))

            video = 'output1.avi'
            gst_tx2 ="nvarguscamerasrc !video/x-raw(memory:NVMM), width=(int)640, height=(int)360, format=(string)I420, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
            gst_usb ="v4l2src device=/dev/video1 ! video/x-raw, width=(int)1280, height=(int)720, format=(string)RGB ! videoconvert ! appsink"
            cap = cv2.VideoCapture("/dev/video0")
            frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            show_landmarks = False
            show_bb = False
            show_id = True
            show_fps = False

            present = defaultdict(int)

            while(True):
                start = time.time()
                _, frame = cap.read()
                
                # Locate faces and landmarks in frame
                face_patches, padded_bounding_boxes, landmarks = detect_and_align.detect_faces(frame, mtcnn)

                if len(face_patches) > 0:
                    face_patches = np.stack(face_patches)
                    feed_dict = {images_placeholder: face_patches, phase_train_placeholder: False}
                    embs = sess.run(embeddings, feed_dict=feed_dict)

                    print('Matches in frame:')
                    matching_ids, matching_distances = id_data.find_matching_ids(embs)

                    for bb, landmark, matching_id, dist in zip(padded_bounding_boxes, landmarks, matching_ids, matching_distances):
                        if matching_id is None:
                            matching_id = 'Unknown'
                            print('Unknown! Couldn\'t find match.')
                        else:
                            print('Hi %s! Distance: %1.4f' % (matching_id, dist))
                            present[matching_id] += 1

                        if show_id:
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(frame, matching_id, (bb[0], bb[3]), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        if show_bb:
                            cv2.rectangle(frame, (bb[0], bb[1]), (bb[2], bb[3]), (255, 0, 0), 2)
                        if show_landmarks:
                            for j in range(5):
                                size = 1
                                top_left = (int(landmark[j]) - size, int(landmark[j + 5]) - size)
                                bottom_right = (int(landmark[j]) + size, int(landmark[j + 5]) + size)
                                cv2.rectangle(frame, top_left, bottom_right, (255, 0, 255), 2)
                else:
                    print('Couldn\'t find a face')

                end = time.time()

                seconds = end - start
                fps = round(1 / seconds, 2)

                if show_fps:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, str(fps), (0, int(frame_height) - 5), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

                cv2.imshow('Frame', frame)

                key = cv2.waitKey(1)
                if key == ord('q'):
                    with open(str(args.id_folder.split('/')[-1])+'_'+str(datetime.now())+'.csv', 'w') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Class: '+str(args.id_folder.split('/')[-1])+'    ', 'Date and Time: '+str(datetime.now())])
                        for i in present.keys():
                            writer.writerow([i])
                    f.close()
                    break
                elif key == ord('l'):
                    show_landmarks = not show_landmarks
                elif key == ord('b'):
                    show_bb = not show_bb
                elif key == ord('i'):
                    show_id = not show_id
                elif key == ord('f'):
                    show_fps = not show_fps

            cap.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    args = arguments('./model/20170512-110547/20170512-110547.pb', './ids/', '1.0')
    main(args)
