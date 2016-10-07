"""
    Implementation of a variational Convolutional Autoencoder

    Thrasyvoulos Karydis
    (c) Massachusetts Institute of Technology 2016

    This work may be reproduced, modified, distributed, performed, and
    displayed for any purpose, but must acknowledge the mods
    project. Copyright is retained and must be preserved. The work is
    provided as is; no warranty is provided, and users accept all
    liability.
"""
import lasagne
import theano
import theano.tensor as ten


class CoDER:
    def __init__(self, pad_size, filters, filter_size):
        self.inp = {'aa_seq': ten.tensor3('aa_seq', dtype=theano.config.floatX)}
        self.targets = {'aa_seq': ten.tensor3('aa_rec_seq', dtype=theano.config.floatX)}

        self.pad_size = pad_size
        self.filters = filters
        self.filter_size = filter_size

        self.layers = self.build_network()

        self.network = self.layers['output']

        self.handle = 'CoDER'

    def build_network(self):
        network = {'input': lasagne.layers.InputLayer(input_var=self.inp['aa_seq'],
                                                      shape=(None, 20, self.pad_size),
                                                      name='Input')}

        # Convolutional layer with M motifs of size m.
        network['conv'] = lasagne.layers.Conv1DLayer(network['input'],
                                                     num_filters=self.filters,
                                                     filter_size=self.filter_size,
                                                     flip_filters=False,
                                                     nonlinearity=None,
                                                     W=lasagne.init.GlorotUniform('relu'),
                                                     stride=1,
                                                     name='Conv1')

        network['conv_non_lin'] = lasagne.layers.NonlinearityLayer(network['conv'],
                                                                   nonlinearity=lasagne.nonlinearities.rectify,
                                                                   name='nonlin')

        # Max-pooling layer to select best motif score for each motif.

        network['maxpool'] = lasagne.layers.GlobalPoolLayer(network['conv_non_lin'],
                                                            pool_function=ten.max,
                                                            name='MaxPool')

        network['FC1'] = lasagne.layers.DenseLayer(network['maxpool'],
                                                   num_units=self.filters,
                                                   nonlinearity=lasagne.nonlinearities.sigmoid,
                                                   name='FC1')

        network['FC2'] = lasagne.layers.DenseLayer(network['FC1'],
                                                   num_units=self.filters,
                                                   nonlinearity=lasagne.nonlinearities.sigmoid,
                                                   name='FC2')

        network['inv_FC2'] = lasagne.layers.InverseLayer(network['FC2'], network['FC2'], name='inv_hidden')

        network['inv_FC1'] = lasagne.layers.InverseLayer(network['inv_FC2'], network['FC1'], name='inv_hidden')

        network['inv_pool'] = lasagne.layers.InverseLayer(network['inv_FC1'], network['maxpool'], name='inv_pool')

        network['output'] = lasagne.layers.InverseLayer(network['inv_pool'], network['conv'], name='inv_conv')

        return network

    def build_loss(self, deterministic=False):
        prediction = lasagne.layers.get_output(self.network, deterministic=deterministic)

        code_dist = prediction.dimshuffle((0, 2, 1)).reshape((prediction.shape[0] * prediction.shape[2], 20))

        true_dist = ten.argmax(
            self.targets['aa_seq'].dimshuffle((0, 2, 1))
                .reshape((self.targets['aa_seq'].shape[0] * self.targets['aa_seq'].shape[2], 20)), axis=1)

        # loss = lasagne.objectives.categorical_crossentropy(code_dist, true_dist)
        loss = lasagne.objectives.squared_error(prediction, self.targets['aa_seq'])

        loss = loss.mean()

        acc = lasagne.objectives.categorical_accuracy(code_dist, true_dist)

        acc = acc.mean()

        return loss, acc, prediction


class DeepCoDER:
    def __init__(self, pad_size, filters, filter_size):
        self.inp = {'aa_seq': ten.tensor3('aa_seq', dtype=theano.config.floatX)}
        self.targets = {'aa_seq': ten.tensor3('aa_rec_seq', dtype=theano.config.floatX)}

        self.pad_size = pad_size
        self.filters = filters
        self.filter_size = filter_size

        self.layers = self.build_network()

        self.network = self.layers['output']

        self.handle = 'CoDER_test'

    def build_network(self):
        network = {'input': lasagne.layers.InputLayer(input_var=self.inp['aa_seq'],
                                                      shape=(None, 20, self.pad_size),
                                                      name='Input')}

        # Convolutional layer with M motifs of size m.
        network['conv1'] = lasagne.layers.Conv1DLayer(network['input'],
                                                      num_filters=self.filters,
                                                      filter_size=self.filter_size,
                                                      flip_filters=False,
                                                      nonlinearity=None,
                                                      W=lasagne.init.GlorotUniform('relu'),
                                                      stride=self.filter_size - 2,
                                                      pad='valid',
                                                      name='Conv1')

        network['conv2'] = lasagne.layers.Conv1DLayer(network['conv1'],
                                                      num_filters=self.filters,
                                                      filter_size=self.filter_size,
                                                      flip_filters=False,
                                                      nonlinearity=None,
                                                      W=lasagne.init.GlorotUniform('relu'),
                                                      stride=self.filter_size - 2,
                                                      pad='valid',
                                                      name='Conv2')

        network['conv3'] = lasagne.layers.Conv1DLayer(network['conv2'],
                                                      num_filters=self.filters,
                                                      filter_size=self.filter_size,
                                                      flip_filters=False,
                                                      nonlinearity=None,
                                                      W=lasagne.init.GlorotUniform('relu'),
                                                      stride=self.filter_size - 2,
                                                      pad='valid',
                                                      name='Conv3')

        network['conv_non_lin'] = lasagne.layers.NonlinearityLayer(network['conv3'],
                                                                   nonlinearity=lasagne.nonlinearities.rectify,
                                                                   name='nonlin')

        # Max-pooling layer to select best motif score for each motif.

        # network['maxpool'] = lasagne.layers.MaxPool1DLayer(network['conv'],
        #                                                    pool_size=100,
        #                                                    stride=1,
        #                                                    name='MaxPool')
        network['maxpool'] = lasagne.layers.GlobalPoolLayer(network['conv_non_lin'],
                                                            pool_function=ten.max,
                                                            name='MaxPool')

        network['FC1'] = lasagne.layers.DenseLayer(network['maxpool'],
                                                   num_units=self.filters,
                                                   nonlinearity=lasagne.nonlinearities.sigmoid,
                                                   name='FC1')

        network['inv_FC1'] = lasagne.layers.InverseLayer(network['FC1'], network['FC1'], name='inv_hidden')

        network['inv_pool'] = lasagne.layers.InverseLayer(network['inv_FC1'], network['maxpool'], name='inv_pool')

        network['inv_conv3'] = lasagne.layers.InverseLayer(network['inv_pool'], network['conv3'], name='inv_conv3')

        network['inv_conv2'] = lasagne.layers.InverseLayer(network['inv_conv3'], network['conv2'], name='inv_conv2')

        network['inv_conv1'] = lasagne.layers.InverseLayer(network['inv_conv2'], network['conv1'], name='inv_conv1')

        network['output'] = network['inv_conv1']

        return network

    def build_loss(self, deterministic=False):
        prediction = lasagne.layers.get_output(self.network, deterministic=deterministic)

        code_dist = prediction.dimshuffle((0, 2, 1)).reshape((prediction.shape[0] * prediction.shape[2], 20))

        true_dist = ten.argmax(
            self.targets['aa_seq'].dimshuffle((0, 2, 1))
                .reshape((self.targets['aa_seq'].shape[0] * self.targets['aa_seq'].shape[2], 20)), axis=1)

        # loss = lasagne.objectives.categorical_crossentropy(code_dist, true_dist)
        loss = lasagne.objectives.squared_error(prediction, self.targets['aa_seq'])
        # lasagne.regularization.regularize_layer_params(self.layers['conv'], lasagne.regularization.l2)

        loss = loss.mean()

        # acc = lasagne.objectives.categorical_accuracy(code_dist, true_dist)

        # acc = acc.mean()
        acc = loss.mean()
        return loss, acc, prediction


class CoMET:
    def __init__(self, pad_size, filters, filter_size):
        # Input is the protein sequence in one-hot representation
        # shape: (minibatch_size, 20, sequence_length)
        self.inp = ten.tensor3('data', dtype=theano.config.floatX)

        # Targets for unsupervised learning, which are the same as input
        self.targetsUS = ten.tensor3('targets', dtype=theano.config.floatX)

        # Targets for supervised learning, which is a vector of labels
        self.targets = ten.matrix('targets', dtype=theano.config.floatX)

        self.pad_size = pad_size
        self.filters = filters
        self.filter_size = filter_size

        self.layers = self.build_network()

        self.network = self.layers['output']

        self.handle = 'CoDER'

    def build_network(self):
        network = {'input': lasagne.layers.InputLayer(input_var=self.inp,
                                                      shape=(None, 20, self.pad_size),
                                                      name='Input')}

        # Convolutional layer with M motifs of size m.
        network['conv'] = lasagne.layers.Conv1DLayer(network['input'],
                                                     num_filters=self.filters,
                                                     filter_size=self.filter_size,
                                                     flip_filters=False,
                                                     nonlinearity=None,
                                                     W=lasagne.init.GlorotUniform('relu'),
                                                     stride=1,
                                                     name='Conv1')

        network['conv_non_lin'] = lasagne.layers.NonlinearityLayer(network['conv'],
                                                                   nonlinearity=lasagne.nonlinearities.rectify,
                                                                   name='nonlin')

        # Max-pooling layer to select best motif score for each motif.

        network['maxpool'] = lasagne.layers.GlobalPoolLayer(network['conv_non_lin'],
                                                            pool_function=ten.max,
                                                            name='MaxPool')

        network['FC1'] = lasagne.layers.DenseLayer(network['maxpool'],
                                                   num_units=self.filters,
                                                   nonlinearity=lasagne.nonlinearities.sigmoid,
                                                   name='FC1')

        network['FC2'] = lasagne.layers.DenseLayer(network['FC1'],
                                                   num_units=self.filters,
                                                   nonlinearity=lasagne.nonlinearities.sigmoid,
                                                   name='FC2')

        network['inv_FC2'] = lasagne.layers.InverseLayer(network['FC2'], network['FC2'], name='inv_hidden')

        network['inv_FC1'] = lasagne.layers.InverseLayer(network['inv_FC2'], network['FC1'], name='inv_hidden')

        network['inv_pool'] = lasagne.layers.InverseLayer(network['inv_FC1'], network['maxpool'], name='inv_pool')

        network['output1'] = lasagne.layers.InverseLayer(network['inv_pool'], network['conv'], name='inv_conv')

        network['output2'] = lasagne.layers.DenseLayer(network['FC2'],
                                                       num_units=1,
                                                       nonlinearity=lasagne.nonlinearities.sigmoid,
                                                       W=lasagne.init.GlorotUniform(),
                                                       name='Output')

        network['output'] = (network['output1'], network['output2'])

        return network

    def build_loss(self, deterministic=False):
        prediction = lasagne.layers.get_output(self.network, deterministic=deterministic)

        code_dist = prediction.dimshuffle((0, 2, 1)).reshape((prediction.shape[0] * prediction.shape[2], 20))

        true_dist = ten.argmax(
            self.targets.dimshuffle((0, 2, 1)).reshape((self.targets.shape[0] * self.targets.shape[2], 20)), axis=1)

        # loss = lasagne.objectives.categorical_crossentropy(code_dist, true_dist)
        loss = lasagne.objectives.squared_error(prediction, self.targets)

        loss = loss.mean()

        acc = lasagne.objectives.categorical_accuracy(code_dist, true_dist)

        acc = acc.mean()

        return loss, acc, prediction