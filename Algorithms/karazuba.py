def karazuba(x: int, y: int) -> int:
    if x < 10 and y < 10:
        return x * y
    n = max(len(str(x)), len(str(y)))
    m = n // 2

    a, b = divmod(x, 10**m)
    c, d = divmod(y, 10**m)

    z0 = karazuba(a, c)
    z1 = karazuba((a + b), (c + d))
    z2 = karazuba(b, d)
    if (z1 - z2 - z0) == 12:
        print("!")
    return (z0 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z2

print(karazuba(1685287499328328297814655639278583667919355849391453456921116729, 7114192848577754587969744626558571536728983167954552999895348492))