# ChinsesNER-pytorch

### train

setp 1: edit **models/config.yml**

    embedding_size: 100
    hidden_size: 128
    model_path: models/
    batch_size: 20
    dropout: 0.5
    tags:
      - ORG
      - PER

step 2: train

    python3 main.py train
    or
    cn = ChineseNER("train")
    cn.train()

    ...
    epoch [4] |██████                   | 154/591
            loss 0.46
            evaluation
            ORG     recall 1.00     precision 1.00  f1 1.00
    --------------------------------------------------
    epoch [4] |██████                   | 155/591
            loss 1.47
            evaluation
            ORG     recall 0.92     precision 0.92  f1 0.92
    --------------------------------------------------
    epoch [4] |██████                   | 156/591
            loss 0.46
            evaluation
            ORG     recall 0.94     precision 1.00  f1 0.97

### predict

    python3 main.py predict
    or 
    cn = ChineseNER("predict")
    cn.predict()

    请输入文本: 海利装饰材料有限公司
    [{'start': 0, 'stop': 10, 'word': '海利装饰材料有限公司', 'type': 'ORG'}]

### REFERENCES
- [Log-Linear Models, MEMMs, and CRFs](http://www.cs.columbia.edu/~mcollins/crf.pdf)
- [Neural Architectures for Named Entity Recognition](https://arxiv.org/pdf/1603.01360.pdf)


{'O': 0, 'START': 1, 'STOP': 2, 'B-ALI-H': 3, 'I-ALI-H': 4, 'B-ALI-T': 5, 'I-ALI-T': 6, 'B-FOI-H': 7, 'I-FOI-H': 8, 'B-FOI-T': 9, 'I-FOI-T': 10, 'B-OVE-T': 11, 'I-OVE-T': 12, 'B-OVE-H': 13, 'I-OVE-H': 14, 'B-DEF-T': 15, 'I-DEF-T': 1
6, 'B-DEF-H': 17, 'I-DEF-H': 18, 'B-SAI-H': 19, 'I-SAI-H': 20, 'B-SAI-T': 21, 'I-SAI-T': 22, 'B-USE-H': 23, 'I-USE-H': 24, 'B-USE-T': 25, 'I-USE-T': 26, 'B-PRR-H': 27, 'I-PRR-H': 28, 'B-PRR-T': 29, 'I-PRR-T': 30, 'B-LOC-T': 31, 'I-L
OC-T': 32, 'B-SEL-H': 33, 'I-SEL-H': 34, 'B-SEL-T': 35, 'I-SEL-T': 36, 'B-CON-H': 37, 'I-CON-H': 38, 'B-CON-T': 39, 'I-CON-T': 40, 'B-LOC-H': 41, 'I-LOC-H': 42, 'B-REF-T': 43, 'I-REF-T': 44, 'B-PPR-T': 45, 'I-PPR-T': 46, 'B-REF-H':
47, 'I-REF-H': 48, 'B-PPR-H': 49, 'I-PPR-H': 50}
