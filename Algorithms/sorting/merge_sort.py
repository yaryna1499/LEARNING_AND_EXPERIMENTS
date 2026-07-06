def MergeSort(list):
    if len(list)>1:
        mid = len(list)//2 #splits list in half
        left = list[:mid]
        right = list[mid:]

        MergeSort(left) #repeats until length of each list is 1
        MergeSort(right)

        a = 0
        b = 0
        c = 0
        while a < len(left) and b < len(right):
            if left[a] < right[b]:
                list[c]=left[a]
                a = a + 1
            else:
                list[c]=right[b]
                b = b + 1
            c = c + 1
        while a < len(left):
            list[c]=left[a]
            a = a + 1
            c = c + 1

        while b < len(right):
            list[c]=right[b]
            b = b + 1
            c = c + 1
    return list