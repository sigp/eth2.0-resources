def split(lst, N):
    return [lst[len(lst)*i//N: len(lst)*(i+1)//N] for i in range(N)]

lst = [0, 1, 3]
n = 2

result = split(lst, n)

print(result)
