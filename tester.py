actual = 3600
tester = 240

for i in range(0,5):
    print(f"{min(60*(2 ** i), 480)} Sekunden")
    ## , {(2 ** i)} Minuten"