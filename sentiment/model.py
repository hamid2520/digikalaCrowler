from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf


def build_model(vocab_size):

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(vocab_size + 1, 128))
    model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2)))
    model.add(tf.keras.layers.Dense(2, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.summary()
    return model
