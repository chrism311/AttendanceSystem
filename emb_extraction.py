from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
from scipy import misc
from six.moves import xrange
from detect_and_align import prewhiten, detect_face, create_mtcnn
import tensorflow as tf
import numpy as np
import sys
import os
import main
import glob


def Main(args):
    train_set = get_dataset(args.data_dir)
    image_list, label_list = get_image_paths_and_labels(train_set)
    # fetch the classes (labels as strings) exactly as it's done in get_dataset
    path_exp = os.path.expanduser(args.data_dir)
    classes = [path for path in os.listdir(path_exp) \
               if os.path.isdir(os.path.join(path_exp, path))]
    classes.sort()
    # get the label strings
    label_strings = [name for name in classes if \
       os.path.isdir(os.path.join(path_exp, name))]

    with tf.Graph().as_default():

        with tf.Session() as sess:

            # Load the model
            main.load_model(args.model_dir)

            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

            # Run forward pass to calculate embeddings
            nrof_images = len(image_list)
            print('Number of images: ', nrof_images)
            batch_size = 50 
            if nrof_images % batch_size == 0:
                nrof_batches = nrof_images // batch_size
            else:
                nrof_batches = (nrof_images // batch_size) + 1
            print('Number of batches: ', nrof_batches)
            embedding_size = embeddings.get_shape()[1]
            emb_array = np.zeros((nrof_images, embedding_size))
            start_time = time.time()

            for i in range(nrof_batches):
                if i == nrof_batches -1:
                    n = nrof_images
                else:
                    n = i*batch_size + batch_size
                # Get images for the batch
                images = load_and_align_data(image_list[i*batch_size:n], 160, 44, 1.0)
                feed_dict = { images_placeholder: images, phase_train_placeholder:False }
                # Use the facenet model to calcualte embeddings
                embed = sess.run(embeddings, feed_dict=feed_dict)
                emb_array[i*batch_size:n, :] = embed
                print('Completed batch', i+1, 'of', nrof_batches)

            run_time = time.time() - start_time
            print('Run time: ', run_time)

            #   export emedings and labels
            label_list  = np.array(label_list)

            np.save(os.path.join(args.data_dir, args.embeddings_name), emb_array)
            np.save(os.path.join(args.data_dir, args.labels_name), label_list)
            label_strings = np.array(label_strings)
            np.save(os.path.join(args.data_dir, args.labels_strings_name), label_strings[label_list])

def get_image_paths(images_dir):
    image_paths = []
    if os.path.isdir(images_dir):
        images = os.listdir(images_dir)
        image_paths = [os.path.join(images_dir, img) for img in images]
    return image_paths

def get_dataset(path):
    dataset = []
    path_exp = os.path.expanduser(path)
    classes = [path for path in os.listdir(path_exp) if os.path.isdir(os.path.join(path_exp, path))]
    classes.sort()
    n_of_classes = len(classes)
    for i in range(n_of_classes):
        class_name = classes[i]
        facedir = os.path.join(path_exp, class_name)
        image_paths = get_image_paths(facedir)
        dataset.append(ImageClass(class_name, image_paths))
    return dataset

def get_image_paths_and_labels(dataset):
    image_paths_flat = []
    labels_flat = []
    for i in range(len(dataset)):
        image_paths_flat += dataset[i].image_paths
        labels_flat += [i] * len(dataset[i].image_paths)
    return image_paths_flat, labels_flat

def load_and_align_data(image_paths, image_size, margin, gpu_memory_fraction):

    print('Creating networks and loading parameters')
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=1.0)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            mtcnn = create_mtcnn(sess, None)

    nrof_samples = len(image_paths)
    img_list = [None] * nrof_samples
    for i in xrange(nrof_samples):
        print(image_paths[i])
        img = misc.imread(os.path.expanduser(image_paths[i]), mode='RGB')
        img_size = np.asarray(img.shape)[0:2]       
        bounding_boxes, _ = detect_face(img, mtcnn['pnet'], mtcnn['rnet'], mtcnn['onet'])
        det = np.squeeze(bounding_boxes[0,0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0]-margin/2, 0)
        bb[1] = np.maximum(det[1]-margin/2, 0)
        bb[2] = np.minimum(det[2]+margin/2, img_size[1])
        bb[3] = np.minimum(det[3]+margin/2, img_size[0])
        cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
        aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        prewhitened = prewhiten(aligned)
        img_list[i] = prewhitened
    images = np.stack(img_list)
    return images

class ImageClass():
    #Stores the paths to images for a given class
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths
  
    def __str__(self):
        return self.name + ', ' + str(len(self.image_paths)) + ' images'
  
    def __len__(self):
        return len(self.image_paths)

class emb_args():
    def __init__(self, model_dir, data_dir, embeddings_name, labels_name, labels_strings_name):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.embeddings_name = embeddings_name
        self.labels_name = labels_name
        self.labels_strings_name = labels_strings_name


if __name__ == '__main__':
    args = emb_args('./model/20170512-110547.pb', './ids/EENG_4315/', 'embeddings', 'labels', 'labels_strings')
    Main(args)
