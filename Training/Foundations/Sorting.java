
import java.util.Random;
import java.util.Arrays;

/*
 * Selection Sort Algorithm
 * Date: 02/09/2024
 * Created by: Adewale Adenle
*/
public class Sorting {

    public static void SelectionSort(int[] array) {
        if (array.length <= 1) {
            return;
        }
        for (int i = 0; i < array.length - 1; i++) {
            int minIndex = i;
            for (int j = i + 1; j < array.length; j++) {
                if (array[j] < array[minIndex]) {
                    minIndex = j;
                }
            }
            selectionSwap(array, i, minIndex);
        }
    }

    public static void selectionSwap(int[] array, int i, int j) {
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }

    public static void main (String[] args){
        Random rand = new Random();
        int[] values = new int[1000];

        for (int i = 0; i < values.length; i++) {
            values[i] = rand.nextInt(10000);
        }

        System.out.println("Unsorted Array" + Arrays.toString(values));

        SelectionSort(values);
        System.out.println("SORTING...............................");
        System.out.println("Sorted Array" + Arrays.toString(values));
    }
}