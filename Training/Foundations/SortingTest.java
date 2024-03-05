import org.junit.Test;
import static org.junit.Assert.*;

public class SortingTest {

    /**
     * Test for Selection Sort with an Empty Array
     */
    @Test
    public void testSelectionSortEmptyArray() {
        int[] array =  new int[0];
        Sorting.SelectionSort(array);
        assertArrayEquals(array, new int[0]);
    }

    /**
     * Test for Selection Sort with a single value in the Array
     */
    @Test
    public void testSelectionSortSingleValueArray() {
        int[] array =  {2};
        Sorting.SelectionSort(array);
        int[] expected =  {2};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with a two values in the Array
     */
    @Test
    public void testSelectionSortTwoValueArray() {
        int[] array =  {10,2};
        Sorting.SelectionSort(array);
        int[] expected =  {2,10};
        assertArrayEquals(array, expected);
    }

    /**
     * Test for Selection Sort with a two similar values in the Array
     */
    @Test
    public void testSelectionSortTwoSimilarValueArray() {
        int[] array =  {2,2};
        Sorting.SelectionSort(array);
        int[] expected =  {2,2};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with an already Sorted Array
     */
    @Test
    public void testSelectionSortOnSortedArray() {
        int[] array =  {2,5,9,13,28,63};
        Sorting.SelectionSort(array);
        int[] expected =  {2,5,9,13,28,63};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with an reverse Sorted Array
     */
    @Test
    public void testSelectionSortOnReverseSortedArray() {
        int[] array =  {63,28,13,9,5,2};
        Sorting.SelectionSort(array);
        int[] expected =  {2,5,9,13,28,63};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with an Random Array
     */
    @Test
    public void testSelectionSortOnRandomArray() {
        int[] array =  {5, 3, 8, 6, 2, 7, 1, 4, 9, 0};
        Sorting.SelectionSort(array);
        int[] expected =  {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with an large dupliactes Array
     */
    @Test
    public void testSelectionSortWithMoreDuplicatesArray() {
        int[] array =  {5, 5, 5, 5, 22, 5, 1, 5, 5, 5};
        Sorting.SelectionSort(array);
        int[] expected =  {1, 5, 5, 5, 5, 5, 5, 5, 5, 22};
        assertArrayEquals(array, expected);
    }
    /**
     * Test for Selection Sort with Negative Values Array
     */
    @Test
    public void testSelectionSortWithNegativeValuesArray() {
        int[] array =  {-5, -3, -8, -6, -2, -7, -1, -4, -9, -0, 16, 12, 14, 11, 10};
        Sorting.SelectionSort(array);
        int[] expected =  {-9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 10, 11, 12, 14, 16};
        assertArrayEquals(array, expected);
    }
}



