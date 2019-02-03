
l = None
with open("requirements.txt") as f:
    l = sorted(list(set(f.readlines())))

with open("requirements.txt", "w") as f:
    f.write("".join(l))

