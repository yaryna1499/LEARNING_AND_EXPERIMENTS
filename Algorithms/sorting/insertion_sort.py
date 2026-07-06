def insertion_sort(arr):
    """Complexity: O(n^2)"""
    for i in range(1, len(arr)):
        j=i
        while arr[j-1] > arr[j] and j > 0:
            arr[j], arr[j-1] = arr[j-1], arr[j]
            j-=1
    return arr


result = insertion_sort([2,6,74,5,7,8,1,2,4,8])
print(result)

