

contents = []
with open("/AviationGraph/Text_Classification/data/entertainment/sentence.txt", "r", encoding='utf-8') as f:
    data = f.readlines()
    for line in data:
        res = line.strip()
        contents.append(res)
f.close()


word_set = set()
for data in contents:
    for word in data:
        word_set.add(word)

with open("/AviationGraph/Text_Classification/data/entertainment/vocab.txt", "w", encoding="utf8") as f:
    for data in word_set:
        f.write(data + "\n")
f.close()
print(len(word_set))
print(word_set)