# -*- coding:utf-8 -*-
import argparse
import os
import sys
import numpy as np
import chainer
from chainer import optimizers
import chainer.functions as F
import chainer.links as L
import pickle
# import dill
# import serializers
import cupy


n_units = 500 # 隠れ層のユニット数
class LSTM(chainer.Chain):

    def __init__(self, n_vocab, n_units):
        print(n_vocab, n_units)
        emb = L.EmbedID(n_vocab, n_units,ignore_label=-1)
        line = L.Linear(n_units, 4 * n_units)
        super(LSTM, self).__init__(
            l1_embed = emb, l1_x = line, l1_h = line,
            l2_embed = emb, l2_x = line, l2_h = line,
            l3_embed = emb, l3_x = line, l3_h = line,
            l4_embed = emb, l4_x = line, l4_h = line,
            l5_embed = emb, l5_x = line, l5_h = line,
            l_umembed = L.Linear(n_units, n_vocab)
        )


    def __str__(self):
        return "{}".format(self.chainer.Chain)


    def forward(self, x1, x2, x3, x4, x5, t, xp, dropout_ratio=0.2):
        cv = chainer.Variable
        h1 = self.l1_embed(cv(xp.asarray([x1], dtype=xp.int32)))
        c1, y1 = F.lstm(cv(xp.zeros((1, n_units), dtype=xp.float32)), F.dropout(self.l1_x(h1), ratio=dropout_ratio) + self.l1_h(self.state['y1']))
        h2 = self.l2_embed(cv(xp.asarray([x2])))
        c2, y2 = F.lstm(self.state['c1'], F.dropout(self.l2_x(h2), ratio=dropout_ratio) + self.l2_h(self.state['y2']))
        h3 = self.l3_embed(cv(xp.asarray([x3])))
        c3, y3 = F.lstm(self.state['c2'], F.dropout(self.l3_x(h3), ratio=dropout_ratio) + self.l3_h(self.state['y3']))
        h4 = self.l4_embed(cv(xp.asarray([x4])))
        c4, y4 = F.lstm(self.state['c3'], F.dropout(self.l4_x(h4), ratio=dropout_ratio) + self.l4_h(self.state['y4']))
        h5 = self.l5_embed(cv(xp.asarray([x5])))
        c5, y5 = F.lstm(self.state['c4'], F.dropout(self.l5_x(h5), ratio=dropout_ratio) + self.l5_h(self.state['y5']))
        self.state = {'c1': c1, 'y1': y1, 'h1': h1, 'c2': c2, 'y2': y2, 'h2': h2, 'c3': c3, 'y3': y3, 'h3': h3, 'c4': c4, 'y4': y4, 'h4': h4, 'c5': c5, 'y5': y5, 'h5': h5}
        y = self.l_umembed(y5)

        return F.softmax(y5), y5.data


    def initialize_state(self, n_units, batchsize=1, xp=cupy ,train=False):
        for name in ('c1', 'y1', 'h1', 'c2', 'y2', 'h2', 'c3', 'y3', 'h3', 'c4', 'y4', 'h4', 'c5', 'y5', 'h5'):
            self.state[name] = chainer.Variable(xp.zeros((batchsize, n_units), dtype=xp.float32))


def load_data(filename, vocab, inv_vocab, xp):
    #global vocab, inv_vocab
    # 全文について改行を<eos>に変換し、単語毎に区切る
    # 日本語の場合は、<eos> の両側にスペースを入れるreplace('\n', ' <eos> ')
    l = len
    if not os.path.isfile('{}vocab.bin'.format(filename)) or not os.path.isfile('{}inv_vocab.bin'.format(filename)) or not os.path.isfile('{}dataset.bin'.format(filename)):
        dum = pickle.dump
        words = open(filename, encoding='utf-8').read().replace('\n', ' <eos> ').strip().split()
        dataset = xp.ndarray((l(words),), dtype=xp.int32)
        for i, word in enumerate(words):
            if word not in vocab:
                vocab[word] = l(vocab)
                inv_vocab[l(vocab)-1] = word
            dataset[i] = vocab[word]
        with open('{}vocab.bin'.format(filename), 'wb') as voc:
            dum(vocab, voc)
        with open('{}inv_vocab.bin'.format(filename), 'wb') as ivoc:
            dum(inv_vocab, ivoc)
        with open('{}dataset.bin'.format(filename), 'wb') as data:
            dum(dataset, data)
    else:
       d = open('{}vocab.bin'.format(filename), 'rb')
       vocab = pickle.load(d)
       fi = open('{}inv_vocab.bin'.format(filename), 'rb')
       inv_vocab = pickle.load(fi)
       t = open('{}dataset.bin'.format(filename), 'rb')
       dataset = pickle.load(t)

    return dataset,vocab,inv_vocab


def main():
    ''' main関数 '''
    p = 5 # 文字列長
    w = 2 # 前後の単語の数
    total_loss = 0  # 誤差関数の値を入れる変数
    inv_vocab={} #逆引き辞書
    word_count = 0
    count = 0
    ch = os.chdir
    l = len
    r = range
    test_vocab = {'<$>':0, '<s>':1, '<eos>':2}
    train_vocab = {'<$>':0, '<s>':1, '<eos>':2}
    test_inv_vocab = {0:'<$>', 1:'<s>', 2:'<eos>'}  #逆引き辞書
    train_inv_vocab = {0:'<$>', 1:'<s>', 2:'<eos>'}  #逆引き辞書




    # 引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', '-g', default=0, type=int,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--dictionary', '-d', default='abc_utf3.dat',
                        help='トレーニングで用いた辞書に使うデータを選んでください。')
    parser.add_argument('--test', '-t', default='117-train-dicform.dat',
                        help='テストで用いる文章データを選んでください。')

    args = parser.parse_args()

    os.chdir('/home/ubuntu/nsteplstm')


   # cuda環境では以下のようにすればよい
    if args.gpu >= 0:
        xp = cupy
    else:
        xp = np

    train_dataset, train_vocab, train_inv_vocab = load_data(args.dictionary,train_vocab,train_inv_vocab, xp)
    ch('/home/ubuntu/train-dicform')
    test_dataset, test_vocab, test_inv_vocab = load_data(args.test,test_vocab,test_inv_vocab, xp)
    print(args.test)
    n_vocab = l(train_vocab)
    print('#vocab =', n_vocab)
    test_name = args.test.split(".")
    result_filename = '{}_{}.txt'.format(test_name[0], n_vocab)
    if not os.path.isdir('./prediction_result'):
        os.mkdir('prediction_result')
        print("folder made")
    ch("./prediction_result")
    length = l(test_dataset)
    print("file is opened")

    #with open('vocab.bin', 'rb') as fv:
    # fv = open('vocab.bin', 'rb')
    # vocab = pickle.load(fv)
    # print("vocab")
    # print(len(vocab))

    # with open('inv_vocab.bin', 'rb') as fi:
    # fi = open('inv_vocab.bin', 'rb')
    # inv_vocab = pickle.load(fi)
    # print("inv_vocab")
    # print(len(inv_vocab))
    # 訓練データ、評価データ、テストデータの読み込み
    ch('/home/ubuntu/train-dicform')
    # test_data = load_data('117-test-dicform2.dat', vocab, inv_vocab, xp)
    # test_data = load_data('117-train-dicform.dat', vocab, inv_vocab, xp)

    # モデルの準備
    # 入力は単語数、中間層はmain関数冒頭で定義
    lstm = LSTM(n_vocab,n_units)
    # model.compute_accuracy = False
    model = L.Classifier(lstm) # こことpickleのところで違いがあるのでだめ
    # :model.predictor.initialize_state(n_units)
    # print("model")
    ch('/home/ubuntu/traindata')
    with open('LSTMmodel.pkl', 'rb') as fm:
        model = pickle.load(fm)
    with open('LSTMlstm.pkl', 'rb') as fl:
        lstm = pickle.load(fl)

    if args.gpu >= 0:
        cupy.cuda.Device(args.gpu).use()
        model.to_gpu()
    f = open(result_filename, 'w')
    x = 0
    seq = []; # seq: 周辺単語のリスト
    seq_append = seq.append
    print("length:",length)
    for t in range(2, length):
        # seq = []
        for k in range(t-w,t+w+1):
            if k < t+w-2:
                 print(k)
                 print(test_dataset[k])
            # print(test_vocab[k])
            if k >= 0 and k <= t+w-1:
                if k == t:
                    seq_append(test_vocab['<$>'])
                elif k > len(test_dataset)-1:
                    seq_append(test_vocab['<s>'])
                else:
                    seq_append(test_dataset[k].tolist())
            else:
                seq_append(test_vocab['<s>'])
        seq_append(test_dataset[t].tolist())
        print('t =', t,', seq :', seq)
        tmp = np.asarray(seq, dtype=np.int32)
        pr, y = lstm.forward(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], xp)
        prediction = list(zip(y[0].tolist(), train_inv_vocab.values()))
        prediction.sort()
        prediction.reverse()
        # test_dataset[t] = display_word
        # print(prediction)
        #print("not ターゲットは「", test_inv_vocab[t], "」")
        #for t, (score, word) in enumerate(prediction):
        #    # print('{},{}'.format(word, score))
        #    word_count += 1
        #    f.write('{}\n'.format(word))
        #    print(word)
        #    word_count += 1
        #    # if word not in dictionary:
        #    #    dictionary[word] = len(dictionary)
        #    if word_count >= 10:
        #        word_count = 0
        #        break  # 上位１０個を出力
        # print("test_inv_vocab[t]:",train_inv_vocab[t])
        if seq[2]==0:
            x += 1
            print('\nターゲットは「{}」\n'.format(test_inv_vocab[seq[2]]))
            count += 1
            f.write('\n{}番目の<$>\n'.format(count))
            print('\n{}番目の<$>\n'.format(count))
            for t, (score, word) in enumerate(prediction):
                f.write('{}\n'.format(word))
                print(word)
                word_count += 1
                if word_count >= 10:
                    word_count = 0
                    break  # 上位１０個を出力



if __name__ == '__main__':
    main()
