import matplotlib.pyplot as plt

A_X = [20, 30, 40, 50, 60, 70, 80, 90, 100]
A_Y = [41, 51, 59, 63, 67, 72, 74, 76, 77]

B_X = [20, 30, 40, 50, 60, 70, 80, 90, 100]
B_Y = [53, 68, 79, 82.9, 82.7, 82.8, 83, 82.7, 82.49]
#
C_X = [20, 30, 40, 50, 60, 70, 80, 90, 100]
C_Y = [59, 75.4, 82.9, 83.4, 83.1, 82.9, 83.12, 82.97, 83.15]

plt.figure()
plt.xlim(20, 100)
plt.ylim(30, 100)
plt.plot(A_X, A_Y, label="BiLSTM-CRF", linestyle=":", marker='h', color='black')
plt.plot(B_X, B_Y, label="BERT-BiLSTM-CRF", linestyle="-.", marker='D', color='coral')
plt.plot(C_X, C_Y, label="ChineseBERT-BiLSTM-CRF", linestyle="--", marker='x', color='#276ab3')
# plt.legend(loc='lower right')
plt.legend()
# plt.title("度的分布折线图")
plt.xlabel("Training set ratio %")
plt.ylabel("F1-score %")
plt.show()
plt.savefig("line.jpg")  # 保存图
