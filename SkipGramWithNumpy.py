import re
import random
import numpy as np
import math
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from SkipGramTokenizer import SkipGramTokenizer

import time

def softmax(inputs):
    total_sum = np.sum(np.exp(inputs))
    return np.exp(inputs) / total_sum


class SkipGramModel:
    def __init__(self, word_size, hidden_size):
        self.word_size = word_size
        self.hidden_size = hidden_size
        self.w1 = np.random.uniform(-1, 1, (word_size, hidden_size))
        self.w2 = np.random.uniform(-1, 1, (hidden_size, word_size))

    def feed_foreward(self, inputs):
        h = inputs @ self.w1
        u = h @ self.w2
        y = softmax(u)
        return y, h, u
    
    def predict(self, inputs):
        h = inputs @ self.w1
        u = h @ self.w2
        y = softmax(u)
        return y

    def fit(self, center_word, context_word, epochs, learning_rate = 0.01):
        self.w1 = np.random.uniform(-1, 1, (self.word_size, self.hidden_size))
        self.w2 = np.random.uniform(-1, 1, (self.hidden_size, self.word_size))
        self.learning_rate = learning_rate

        for i in range(epochs):
            # Intialise loss to 0
            self.loss = 0
            # Cycle through each training sample
            # w_t = vector for target word, w_c = the vector resulted from summing all the one hot encodings of the context words, thus if we sum it's elements it's gonna be %context_size%
            for w_t, w_c in zip(center_word, context_word):
                # Forward pass
                # 1. predicted y using softmax (y_pred) 2. matrix of hidden layer (h) 3. output layer before softmax (u)
                y_pred, h, u = self.feed_foreward(w_t)
                #########################################
                # print("Vector for target word:", w_t)	#
                # print("W1-before backprop", self.w1)	#
                # print("W2-before backprop", self.w2)	#
                #########################################

                # Calculate error
                # 1. For a target word, calculate difference between y_pred and each of the context words
                # 2. Sum up the differences using np.sum to give us the error for this particular target word
                EI = np.subtract(y_pred*np.sum(w_c), w_c)
                #########################
                # print("Error", EI)	#
                #########################

                # Backpropagation
                # We use SGD to backpropagate errors - calculate loss on the output layer
                self.backprop(EI, h, w_t)
                #########################################
                #print("W1-after backprop", self.w1)	#
                #print("W2-after backprop", self.w2)	#
                #########################################

                # Calculate loss
                # There are 2 parts to the loss function
                # Part 1: -ve sum of all the output +
                # Part 2: length of context words * log of sum for all elements (exponential-ed) in the output layer before softmax (u)
                # Note: word.index(1) returns the index in the context word vector with value 1
                # Note: u[word.index(1)] returns the value of the output layer before softmax

                #context_array = np.array(w_c[0])
                #for j in range(1, len(w_c)):
                #    context_array = context_array + np.array(w_c[j])

                # print(context_array)
                # print(context_array*u)
                self.loss += - np.sum(w_c*u) + np.sum(w_c) * np.log(np.sum(np.exp(u)))

                #############################################################
                # Break if you want to see weights after first target word 	#
                # break 													#
                #############################################################
            print('Epoch:', i, "Loss:", self.loss)

    def backprop(self, e, h, w_t):
        # Backpropagation:
        gradient_w2 = np.outer(h, e)
        gradient_w1 = np.outer(w_t, (self.w2 @ e.T))
        # Update
        self.w1 = self.w1 - self.learning_rate * gradient_w1
        self.w2 = self.w2 - self.learning_rate * gradient_w2
    
    def save_weights(self):
        np.save("w1", self.w1)
        np.save("w2", self.w2)
    
    def load_weights(self):
        self.w1 = np.load("w1.npy")
        self.w2 = np.load("w2.npy")


class SkipGram:
    def __init__(self, context_size) -> None:
        self.model = None
        self.context_size = context_size
        self.training_data = None
        self.words2index = None
        self.index2words = None

    def init_from_file(self, path: str):
        tokenizer = SkipGramTokenizer()
        with open(path, 'r') as training_text_file:
            raw_text = training_text_file.read()
            self.words2index, self.training_data = tokenizer.get_training_data(
                raw_text, self.context_size)
            self.index2words = {value: key for (
                key, value) in self.words2index.items()}

        word_count = len(self.words2index)
        self.model = SkipGramModel(word_count, 10)

    def init_from_string(self, raw_text: str):
        tokenizer = SkipGramTokenizer()
        self.words2index, self.training_data = tokenizer.get_training_data(
            raw_text, self.context_size)
        word_count = len(self.words2index)
        self.model = SkipGramModel(word_count, word_count//2)

    def train(self, epochs = 100):
        x = []
        y = []
        for pair in self.training_data:
            x.append(pair[0])
            y.append(pair[1])

        x = np.array(x)
        y = np.array(y)
        self.model.fit(x, y, epochs)

    def save_weights(self):
        self.model.save_weights()

    def load_weights(self):
        self.model.load_weights()

    def predict(self, input_word: str):
        word_count = len(self.words2index)

        input_vector = [1 if self.words2index[input_word] == i else 0 for i in range(word_count)]
        input_vector = np.array(input_vector)

        y = self.model.predict(input_vector)
        probability_vector = [(y[i], i) for i in range(len(y))]
        probability_vector = sorted(probability_vector, reverse=True)
        for j in range(self.context_size):
            probability = probability_vector[j][0]
            word_index = probability_vector[j][1]
            actual_word = self.index2words[word_index]

            print(actual_word, " ", probability)
    
    def plot_words(self):
        pass



if __name__ == "__main__":
    SG = SkipGram(4)
    SG.init_from_file("text.txt")
    SG.train(epochs= 700)
    SG.save_weights()
    SG.load_weights()
    print(SG.index2words)
    x = "0"
    while x != "quit":
        x = input("New Word: ")
        try:
            SG.predict(x)
        except:
            print("Inexistent word")

#h = test_oneHot @ w
#u = h @ w_prim
#y = softmax(u)
#
#nr = 5
#total = 0
#probabilityVect = sorted([(y[i], i) for i in range(V)], reverse=True)
#for myTup in probabilityVect[:4]:
#    for item in wordsIndex.items():
#        if myTup[1] == item[1]:
#            print("{} Prob: {}".format(item[0], y[myTup[1]]))
#
#
#tokens = []
#labels = []
#for word in wordsIndex.keys():
#    tokens.append(one_hot_words[wordsIndex[word]] @ w @ w_prim)  # encoding
#    labels.append(word)
#
#tsne_model = TSNE(perplexity=40, n_components=2,
#                  init='pca', n_iter=2500, random_state=23)
#new_values = tsne_model.fit_transform(tokens)
#
#x = []
#y = []
#for value in new_values:
#    x.append(value[0])
#    y.append(value[1])
#
#plt.figure(figsize=(16, 16))
#for i in range(len(x)):
#    plt.scatter(x[i], y[i])
#    plt.annotate(labels[i],
#                 xy=(x[i], y[i]),
#                 xytext=(5, 2),
#                 textcoords='offset points',
#                 ha='right',
#                 va='bottom')
#plt.show()
#