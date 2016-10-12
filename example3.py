# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from scipy import ndimage
import tensorflow as tf
from stn import TPSTransformer
import numpy as np
import scipy.misc

# %% Create a batch of three images (1600 x 1200)
# %% Image retrieved from:
# %% https://raw.githubusercontent.com/skaae/transformer_network/master/cat.jpg
im = ndimage.imread('data/cat.jpg')
im = im / 255.
im = im.reshape(1, 1200, 1600, 3)
im = im.astype('float32')

# %% Let the output size of the affine transformer be half the image size.
out_size = (600, 800)

# %% Simulate batch
num_batch = 3
batch = im
for i in range(num_batch-1):
  batch = np.append(batch, im, axis=0)

x = tf.placeholder(tf.float32, [None, 1200, 1600, 3])
x = tf.cast(batch, 'float32')
n_fc = 16*2

# %% Run session
with tf.Session() as sess:
  with tf.device("/cpu:0"):
    stl = TPSTransformer(x.get_shape().as_list(), n_fc/2, out_size)
    # %% Create localisation network and convolutional layer
    with tf.variable_scope('spatial_transformer_0'):
    
        # %% Create a fully-connected layer with 16*2 output nodes
        W_fc1 = tf.Variable(tf.zeros([1200*1600*3, n_fc]), name='W_fc1')
    
        # %% identity transformation
        initial = np.zeros([n_fc]).astype('float32')
        b_fc1 = tf.Variable(initial_value=initial, name='b_fc1')

        h_fc1 = tf.matmul(tf.zeros([num_batch, 1200*1600*3]), W_fc1) + b_fc1 + 0.1*tf.random_normal([num_batch, n_fc])
        h_trans = stl.transform(x, h_fc1)

    # %% Run session
    sess.run(tf.initialize_all_variables())
    y = sess.run(h_trans, feed_dict={x: batch})

# save our result
for i in range(num_batch):
  scipy.misc.imsave('example3_stn' + str(i) + '.png', y[i])

