actual = 3600
tester = 240

for i in range(0,5):
    print(f"{min(300 * (3 ** i), 3600)// 60} Minuten")