# -*- coding:utf-8 -*-
'''
@Author: yanwii
@Date: 2018-10-31 10:00:03
'''
import pickle
import sys

import torch
import torch.optim as optim
import yaml

# from data_manager import DataManager
# from model import BiLSTMCRF
# from utils import f1_score, get_result


from AviationGraph.ChinsesNER.data_manager import DataManager
from AviationGraph.ChinsesNER.model import BiLSTMCRF
from AviationGraph.ChinsesNER.utils import f1_score, get_result


class ChineseNER(object):
    
    def __init__(self, entry="train"):
        self.load_config()
        self.__init_model(entry)

    def __init_model(self, entry):
        if entry == "train":
            self.train_manager = DataManager(batch_size=self.batch_size, tags=self.tags)
            self.total_size = len(self.train_manager.batch_data)
            data = {
                "batch_size": self.train_manager.batch_size,
                "input_size": self.train_manager.input_size,
                "vocab": self.train_manager.vocab,
                "tag_map": self.train_manager.tag_map,
            }
            self.save_params(data)
            dev_manager = DataManager(batch_size=30, data_type="dev")
            self.dev_batch = dev_manager.iteration()

            self.model = BiLSTMCRF(
                tag_map=self.train_manager.tag_map,
                batch_size=self.batch_size,
                vocab_size=len(self.train_manager.vocab),
                dropout=self.dropout,
                embedding_dim=self.embedding_size,
                hidden_dim=self.hidden_size,
            )
            self.restore_model()
        elif entry == "predict":
            data_map = self.load_params()
            input_size = data_map.get("input_size")
            self.tag_map = data_map.get("tag_map")
            self.vocab = data_map.get("vocab")

            self.model = BiLSTMCRF(
                tag_map=self.tag_map,
                vocab_size=input_size,
                embedding_dim=self.embedding_size,
                hidden_dim=self.hidden_size
            )
            self.restore_model()

    def load_config(self):
        try:
            fopen = open("AviationGraph/ChinsesNER/models/config.yml", encoding="utf8")
            config = yaml.load(fopen)
            fopen.close()
        except Exception as error:
            print("Load config failed, using default config {}".format(error))
            fopen = open("AviationGraph/ChinsesNER/models/config.yml", "w")
            config = {
                "embedding_size": 100,
                "hidden_size": 128,
                "batch_size": 20,
                "dropout": 0.5,
                "model_path": "AviationGraph/ChinsesNER/models/",
                "tasg": ["ORG", "PER"]
            }
            yaml.dump(config, fopen)
            fopen.close()
        self.embedding_size = config.get("embedding_size")
        self.hidden_size = config.get("hidden_size")
        self.batch_size = config.get("batch_size")
        self.model_path = config.get("model_path")
        self.tags = config.get("tags")
        self.dropout = config.get("dropout")

    def restore_model(self):
        try:
            self.model.load_state_dict(torch.load(self.model_path + "params.pkl"))
            print("model restore success!")
        except Exception as error:
            print("model restore faild! {}".format(error))

    def save_params(self, data):
        with open("AviationGraph/ChinsesNER/models/data.pkl", "wb") as fopen:
            pickle.dump(data, fopen)

    def load_params(self):
        with open("AviationGraph/ChinsesNER/models/data.pkl", "rb") as fopen:
            data_map = pickle.load(fopen)
        return data_map

    def train(self):
        optimizer = optim.Adam(self.model.parameters())
        # optimizer = optim.SGD(ner_model.parameters(), lr=0.01)
        for epoch in range(100):
            index = 0
            for batch in self.train_manager.get_batch():
                index += 1
                self.model.zero_grad()

                sentences, tags, length = zip(*batch)
                sentences_tensor = torch.tensor(sentences, dtype=torch.long)
                tags_tensor = torch.tensor(tags, dtype=torch.long)
                length_tensor = torch.tensor(length, dtype=torch.long)

                loss = self.model.neg_log_likelihood(sentences_tensor, tags_tensor, length_tensor)
                progress = ("█"*int(index * 25 / self.total_size)).ljust(25)
                print("""epoch [{}] |{}| {}/{}\n\tloss {:.2f}""".format(
                        epoch, progress, index, self.total_size, loss.cpu().tolist()[0]
                    )
                )
                self.evaluate()
                print("-"*50)
                loss.backward()
                optimizer.step()
                torch.save(self.model.state_dict(), self.model_path+'params.pkl')

    def evaluate(self, input_str="", input_BIO=None):
        '''
            以句子为单位进行验证
            :param input_str:
            :param input_BIO:
            :return:
        '''
        if input_BIO is None:
            input_BIO = list([])
        input_vec = [self.vocab.get(i, 0) for i in input_str]
        sentences = torch.tensor(input_vec).view(1, -1)
        _, paths = self.model(sentences)
        #预测的结果序列
        pre_result = get_result(paths[0], input_str, self.tag_map)
        #真实的结果序列
        rel_result = get_result(input_BIO, input_str, self.tag_map)
        f1_score(input_str, pre_result, rel_result)


    def predict(self, input_str=""):
        # 调试的时候从控制台输入
        if not input_str:
            input_str = input("请输入文本: ")

        input_vec = [self.vocab.get(i, 0) for i in input_str]
        # convert to tensor
        sentences = torch.tensor(input_vec).view(1, -1)
        _, paths = self.model(sentences)
        print(input_str)
        print(paths)
        entities = get_result(paths[0], input_str, self.tag_map)
        print(entities)
        print("="*20)
        # for tag in self.tags:
        #     tags = get_tags(paths[0], tag, self.tag_map)
        #     entities += format_result(tags, input_str, tag)


        return entities

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("menu:\n\ttrain\n\tpredict")
        exit()  
    if sys.argv[1] == "train":
        cn = ChineseNER("train")
        cn.train()
    elif sys.argv[1] == "predict":
        cn = ChineseNER("predict")
        print(cn.predict("可用性的概率度量亦称可用度5可信性Dependability产品在任务开始时可用性给定的情况下，在规定的任务剖面中的任一随机时刻，能使用且能完成规定功能的能力6固有能力capability产品在给定的内在条件下，满足给定的定量特征要求的自身的能力。	"))
    elif sys.argv[2] == "evaluate":
        cn = ChineseNER("evaluate")
        cn.evaluate("可用性的概率度量亦称可用度5可信性Dependability产品在任务开始时可用性给定的情况下，在规定的任务剖面中的任一随机时刻，能使用且能完成规定功能的能力6固有能力capability产品在给定的内在条件下，满足给定的定量特征要求的自身的能力。", [])