

contents = []
with open("F:\\01-科研资料\\03-项目工程\\Text_Classification-master\\data\\sentence.txt", "r", encoding='utf-8') as f:
    data = f.readlines()
    for line in data:
        res = line.strip()
        contents.append(res)
f.close()


word_set = set()
for data in contents:
    for word in data:
        word_set.add(word)

with open("F:/01-科研资料/03-项目工程/Text_Classification-master/data/vocab.txt", "w", encoding="utf8") as f:
    for data in word_set:
        f.write(data + "\n")
f.close()
print(len(word_set))
print(word_set)