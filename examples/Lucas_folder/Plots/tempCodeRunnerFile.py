epsilons = [2, 4, 6]
some_list = [8, 10, 12]

empty = [0] * 3

for i in range(len(some_list)):
    print(i)
    empty[i] = (i, some_list[i])

print(empty)
res = [0, 0, 0]
for j in range(len(some_list)):
    res[j] = empty[j][1] / epsilons[j]

print(res)