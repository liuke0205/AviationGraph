# -*- coding: utf-8 -*-

from AviationGraph.Text_Classification.src.model import TextCNN, LSTM


if __name__ == '__main__':
    CNN_model = TextCNN()
    # CNN_model.train(200)
    CNN_model.test()