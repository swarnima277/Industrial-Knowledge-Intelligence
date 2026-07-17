#include <stdio.h>
#include <time.h>
int main(){
    int arr[100], choice, n, p, value, i, key, m, arr2[100], merg[100];
    clock_t start, end;
    double time_taken;
    printf("Enter number of elements in array:");
    scanf("%d",&n);
    printf("enter array elements:");
    for (i=0;i<n;i++){
      scanf("%d",&arr[i]);
    }
    do{
    printf("  Menu: ");
    printf("1.) Traversal");
    printf("2.) Insertion");
    printf("3.) Deletion");
    printf("4.) Searching");
    printf("5.) updating");
    printf("6.) merging");
    printf("7.) Exit");
    printf("Enter the choice:");
    scanf("%d",&choice);
    switch(choice)
    {
        case 1:
        start = clock();
        printf("Array elements are:");
        for(i=0;i<n;i++)
        {
            printf("%d",arr[i]);
        }
        end = clock();
        time_taken = (double)(end-start) / CLOCKS_PER_SEC;
        printf("\nExecution Time = %lf seconds\n", time_taken);
        break;

        case 2:
        printf("Enter position:");
        scanf("%d",&p);
        printf("Enter the value:");
        scanf("%d",&value);
        start = clock();
        for(i=0;i>=p;i--)
        {
            arr[i]=arr[i-n];
        }
        arr[p-1]=value;
        n++;
        end = clock();
        time_taken = (double)(end - start) / CLOCKS_PER_SEC;
        printf("\nExecution Time = %lf seconds\n", time_taken);

        break;
        case 3:
        printf("Enter the position:");
        scanf("%d",&p);
        start = clock();
        for(i=p-1;i<n-1;i++)
        {
            arr[i]=arr[i+1];
        }
        n--;
        end = clock();
        time_taken = (double)(end - start) / CLOCKS_PER_SEC;
        printf("\nExecution Time = %lf seconds\n", time_taken);
        break;
        case 4:
        printf("Enter the value to be searched:");
        scanf("%d",&value);
        start = clock();
        for(i=0;i<=n;i++)    
        {
          if(arr[i]==key)
          {
            printf("Element found at position %d",i+1);
            break;
          }
        }
        if(i==n)
        {
            printf("element not found");
        }
        end = clock();

        time_taken = (double)(end - start) / CLOCKS_PER_SEC;
        printf("Execution Time = %lf seconds\n", time_taken);
        break;

        case 5:
        printf("Enter the postion to be updated:");
        scanf("%d",&p);
        printf("enter the value:");
        scanf("%d",&value);
        start = clock();
        arr[p-1]=value;
        end = clock();
        printf("Updated array:");
        for(i=0;i<n;i++)
        {
            printf("%d",arr[i]);
        }
        time_taken = (double)(end - start) / CLOCKS_PER_SEC;
        printf("\nExecution Time = %lf seconds\n", time_taken);
        break;

        case 6:
        printf("Enter the number of elements in second array:");
        scanf("%d",&m);
        printf("Enter the elements:");
        for(i=0;i<m;i++)
        {
            scanf("%d",arr2[i]);
        }
        start = clock();
        for(i=0;i<n;i++)
        {
           merg[i]=arr[i];
        }
        for(i=0;i<m;i++)
        {
            merg[n+i]=arr[i];
        }
        end = clock();
        printf("The merged array is:");
        for(i=0;i<n+m;i++)
        {
            printf("%d",merg[i]);
        }
        time_taken = (double)(end - start) / CLOCKS_PER_SEC;
        printf("\nExecution Time = %lf seconds\n", time_taken);
        break;
        case 7:
           printf("Program ended");
           break;



        
    }
    }
    while(choice!=7);
    

    return 0; 

}