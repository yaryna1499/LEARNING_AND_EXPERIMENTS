def top_k_frequent_elements(arr: list[int], k: int) -> list[int]:
    # Time comp - O(3n + k) = O(n + k)
    # Space comp - O(2n + k) = O(n + k)
    count_el: dict[int, list[int]] = {k: [] for k in range(1, len(arr)+1)}
    el_count: dict[int, int] = {}
    for num in arr:
        el_count[num] = 1 + el_count.get(num, 0)

    for n, c in el_count.items():
        count_el[c].append(n)
    # bucket sort
    res = []
    i = len(arr)
    while i <= len(arr):
        res.extend(count_el[i]) if count_el[i] else None
        i -= 1
        if len(res) >= k:
            break
    return res[:k]

   
print(top_k_frequent_elements([1, 2,2,2], k=1))