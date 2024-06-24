#include <stdio.h>

#define ROWS 3
#define COLS 2


int getCol(int (*matrix)[2]){
    return *matrix[2];
}

int getCol_2(int (*matrix)){
    return sizeof(matrix);
}

int getCol_3(int (*matrix),size_t size){
    printf("n cols: %lu",(sizeof(matrix))/sizeof(matrix[0]));
    printf("n rows: %lu",size/sizeof(matrix));
    return 0;
}

int main (void) {

    int a[ROWS][COLS]= {{ 1, 2 }, { 3, 4 },{5,6}};
    int b[6]={10,20,30,40,50,60};
    //float b[COLS][ROWS] = {{ 1, 2 }, { 3, 4 },{5,6}};
    int *p = *a;
    int (*pp)[COLS]=a; //A pointer to a two dimensional integers with COLS element per row
    int *pb=b;

    printf("%d",*p);
    putchar('\n');
    printf("%d",*(pp[2]+1));
    putchar('\n');
    printf("%d",*(pb+2));
    putchar('\n');
    printf("%d",getCol(a));
    putchar('\n');
    printf("%d",getCol_2(*a));
    putchar('\n');
    printf("%lu",sizeof(a));
    getCol_3(*a,sizeof(a));
    /* using a pointer to access the values */
    // for (i = 0; i < ROWS * COLS;p++,i++)
    //     printf (" %f", *p);
    putchar ('\n');

    return 0;
}