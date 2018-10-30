#!/usr/bin/env python3

'''
A Bark detector. Analyzes an audio file to determine whether it is a bark or not. Uses a Tensorflow model based off https://www.tensorflow.org/tutorials/sequences/audio_recognition
'''

import time
import tensorflow as tf
import sound_input


class Barkdetector():
    def __init__(self, labels, graph_file, ambient_db, debug=False):
        self._ambient_db = ambient_db

        if graph_file and labels:
            self._labels = labels
            self._input_name = 'wav_data:0'
            self._output_name='labels_softmax:0'
            self._how_many_labels = 3

            self._labels_list = _load_labels(labels)
            self._graph = _load_graph(graph_file)
            self._softmax_tensor = self._graph.get_tensor_by_name(self._output_name)
        
    def is_loud(self, wav):
        """Analyses if the passed audio fragment is considered 'loud'. Returns True if it is higher than the ambient_db"""
        with open(wav, 'rb') as wav_file:
            current_loudness = sound_input.get_peak_volume(wav)
            return current_loudness >= self._ambient_db

    def is_bark(self, wav):
        """Analyses if the passed audio fragment is a bark. Returns True if the probability is > 25%.
        Right now this is a dumb implementation, since there is no sliding window for detection 
        (also, it detects the word 'yes', not a bark).
        """
        with open(wav, 'rb') as wav_file:
            wav_data = wav_file.read()

            start = time.time()
            with tf.Session(graph=self._graph) as sess:
                predictions, = sess.run(self._softmax_tensor, {self._input_name: wav_data})

                top_k = predictions.argsort()[-1:][::-1]
                human_string = self._labels_list[top_k[0]]
                score = predictions[top_k[0]]

                print('{} (score = {:.2f}) - took {:.2f}'.format(human_string, score, time.time() - start))

                return human_string == 'yes' and score > 0.25

def _load_labels(filename):
    """Read in labels, one label per line."""
    return [line.rstrip() for line in tf.gfile.GFile(filename)]

def _load_graph(filename):
    """Unpersists graph from file as default graph."""
    with tf.gfile.FastGFile(filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
    return graph
