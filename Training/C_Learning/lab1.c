
#include <stdio.h>

/* Author: put your name here */
int main(void)
{
    unsigned int maxEntries;
    int getchar_return_value; /* note manual page says getchar() returns an integer
    value */
    char keyboard_value[25];  /* declare space to hold the keyboard values */
    int i;                    /* declare i to track amount of times through loop */
    printf("This program reads in a number, then a series of keyboard characters. The number\n");
    printf("indicates how many characters follow. The number can be no higher than 25.\n");
    printf("Then the specified number of characters follows. These characters can be any\n");
    printf("key on a regular keyboard.\n");
    /* Read the first number entered to know how many entries will follow */
    printf("Please enter the number of entries, followed by the enter/return key: ");
    scanf("%u", &maxEntries);

    if (maxEntries > 25)
    {
        printf("Specified number of characters is invalid. It must be between 0 and 25.\n");
        return 0;
    }
    getchar(); /* trash the '\n' */

    printf("enter the %u characters: ", maxEntries);
    for (i = 0; i < maxEntries; i++)
    {
        getchar_return_value = getchar();
        printf("The value is %c. \n", getchar_return_value);
        if (getchar_return_value != EOF)
        {                                                   /* we got a valid value */
            keyboard_value[i] = (char)getchar_return_value; /* truncate to a char so it fits */
        }
        else
        {
            printf("fewer than %u characters entered, number of characters set to %d\n",
                   maxEntries, i);
            maxEntries = i;
            break;
        }
    }
    printf("The keyboard values are: \n");
    for (i = 0; i < maxEntries; i++)
    { /* print them out */
        putchar(keyboard_value[i]);
        putchar('\n');
    }
}
