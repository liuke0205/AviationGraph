1. 修改preprocess.py文件中的categories
2. 根据/data文件夾下面的数据格式构造数据 -> 去DataProcess工程里面运行json2txt_classification.py
    2.1 sentence.txt 放train.txt的文本
    2.2 test.txt 放train.txt生成的
    2.3 train.txt 放test.txt生成的
    2.4 val.txt 放train.txt生成的
3. 运行txt2vocab.py文件，根据sentence.txt文件构造词表
4. 修改config.py  里面的"num_classes"的数值
5. 运行main.py 训练模型，同时根据sentence.txt文件生成前10% 20% 30% 40% 50% 60%的原始数据
6. 将生成的数据拷贝到DataProcess工程的对应数据集的activate文件夹下面
7. 运行generate_dataset.py 将原始数据转化为json数据
8. 运行json2label.py文件，将json生成带标签的训练数据。