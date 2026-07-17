# Program: Linear Search

# Input number of elements
n = int(input("Enter the number of elements: "))

# Input array elements
arr = []
print("Enter the array elements:")
for i in range(n):
    arr.append(int(input()))

# Input element to search
key = int(input("Enter the element to search: "))

# Perform Linear Search
found = False

for i in range(n):
    if arr[i] == key:
        print("Element found at position:", i + 1)
        found = True
        break

# If element is not found
if not found:
    print("Element not found")
