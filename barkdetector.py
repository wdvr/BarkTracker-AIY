#!/usr/bin/env python3

'''
A Bark detector. Analyzes an audio file to determine whether it is a bark or not. Uses a Tensorflow model based off https://www.tensorflow.org/tutorials/sequences/audio_recognition
'''

import time
import tensorflow as tf
import sound_input


class Barkdetector():
    def __init__(self, labels, graph, ambient_db, debug=False):
        self._labels = labels
        self._graph = graph
        self._ambient_db = ambient_db
        wav = '/home/pi/bark-ai/a5d485dc_nohash_1.wav'

        input_name = 'wav_data:0'
        output_name='labels_softmax:0'
        how_many_labels = 3
        
        labels_list = _load_labels(labels)

        # load graph, which is stored in the default session
        _load_graph(graph)
        
    def is_bark(self, wav):
        start = time.time()
#         with open(wav, 'rb') as wav_file:
#             wav_data = wav_file.read()
#             run_graph(wav_data, labels_list, input_name, output_name, how_many_labels)
        
        current_loudness = sound_input.get_peak_volume(wav)
        print("took {}s".format(time.time() - start))

        return current_loudness <= self._ambient_db
    

def _load_labels(filename):
    """Read in labels, one label per line."""
    return [line.rstrip() for line in tf.gfile.GFile(filename)]

def _load_graph(filename):
    """Unpersists graph from file as default graph."""
    with tf.gfile.FastGFile(filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

def _run_graph(wav_data, labels, input_layer_name, output_layer_name,
              num_top_predictions):
  """Runs the audio data through the graph and prints predictions."""
  with tf.Session() as sess:
    # Feed the audio data as input to the graph.
    #   predictions  will contain a two-dimensional array, where one
    #   dimension represents the input image count, and the other has
    #   predictions per class
    softmax_tensor = sess.graph.get_tensor_by_name(output_layer_name)
    predictions, = sess.run(softmax_tensor, {input_layer_name: wav_data})

    # Sort to show labels in order of confidence
    top_k = predictions.argsort()[-num_top_predictions:][::-1]
    for node_id in top_k:
      human_string = labels[node_id]
      score = predictions[node_id]
      print('%s (score = %.5f)' % (human_string, score))

    return 0