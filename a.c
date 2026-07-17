#include <stdio.h>
#include <time.h>

int main()
{
    int arr1[100], arr2[100], merge[200];
    int n1, n2;
    int i, pos, value, key, found = 0;
    clock_t start, end;
    double time_taken;

    printf("Enter number of elements in first array: ");
    scanf("%d", &n1);

    printf("Enter elements:\n");
    for(i = 0; i < n1; i++)
    {
        scanf("%d", &arr1[i]);
    }

    int choice;

    do
    {
        printf("\n----- ARRAY OPERATIONS -----\n");
        printf("1. Traversal\n");
        printf("2. Insertion\n");
        printf("3. Deletion\n");
        printf("4. Searching\n");
        printf("5. Updating\n");
        printf("6. Merging\n");
        printf("7. Exit\n");

        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch(choice)
        {
            case 1:

                start = clock();

                printf("Array Elements:\n");
                for(i = 0; i < n1; i++)
                    printf("%d ", arr1[i]);

                end = clock();

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("\nExecution Time = %lf seconds\n", time_taken);

                break;

            case 2:

                printf("Enter position: ");
                scanf("%d", &pos);

                printf("Enter value: ");
                scanf("%d", &value);

                start = clock();

                for(i = n1; i >= pos; i--)
                    arr1[i] = arr1[i-1];

                arr1[pos-1] = value;
                n1++;

                end = clock();

                printf("Array after insertion:\n");
                for(i = 0; i < n1; i++)
                    printf("%d ", arr1[i]);

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("\nExecution Time = %lf seconds\n", time_taken);

                break;

            case 3:

                printf("Enter position to delete: ");
                scanf("%d", &pos);

                start = clock();

                for(i = pos-1; i < n1-1; i++)
                    arr1[i] = arr1[i+1];

                n1--;

                end = clock();

                printf("Array after deletion:\n");
                for(i = 0; i < n1; i++)
                    printf("%d ", arr1[i]);

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("\nExecution Time = %lf seconds\n", time_taken);

                break;

            case 4:

                printf("Enter element to search: ");
                scanf("%d", &key);

                start = clock();

                found = 0;

                for(i = 0; i < n1; i++)
                {
                    if(arr1[i] == key)
                    {
                        found = 1;
                        printf("Element found at position %d\n", i + 1);
                        break;
                    }
                }

                if(found == 0)
                    printf("Element not found\n");

                end = clock();

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("Execution Time = %lf seconds\n", time_taken);

                break;

            case 5:

                printf("Enter position to update: ");
                scanf("%d", &pos);

                printf("Enter new value: ");
                scanf("%d", &value);

                start = clock();

                arr1[pos-1] = value;

                end = clock();

                printf("Updated Array:\n");
                for(i = 0; i < n1; i++)
                    printf("%d ", arr1[i]);

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("\nExecution Time = %lf seconds\n", time_taken);

                break;

            case 6:

                printf("Enter number of elements in second array: ");
                scanf("%d", &n2);

                printf("Enter elements:\n");
                for(i = 0; i < n2; i++)
                    scanf("%d", &arr2[i]);

                start = clock();

                for(i = 0; i < n1; i++)
                    merge[i] = arr1[i];

                for(i = 0; i < n2; i++)
                    merge[n1 + i] = arr2[i];

                end = clock();

                printf("Merged Array:\n");
                for(i = 0; i < n1 + n2; i++)
                    printf("%d ", merge[i]);

                time_taken = (double)(end - start) / CLOCKS_PER_SEC;
                printf("\nExecution Time = %lf seconds\n", time_taken);

                break;

            case 7:
                printf("Program Ended.\n");
                break;

            default:
                printf("Invalid Choice\n");
        }

    } while(choice != 7);

    return 0;
}