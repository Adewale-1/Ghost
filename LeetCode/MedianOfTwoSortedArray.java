import java.util.Arrays;

class MedianOfTwoSortedArray {

    public static void main(String[] args) {
        int[] nums1 = { 1, 2 };
        int[] nums2 = { 3, 4 };

        double median = findMedianSortedArrays(nums1, nums2);
        System.out.println(median);
    }

    public static double findMedianSortedArrays(int[] nums1, int[] nums2) {
        int length = nums1.length + nums2.length;
        int finalArray[] = new int[length];
        double median = 0.0;

        for (int i = 0; i < nums1.length; i++) {
            finalArray[i] = nums1[i];
        }
        int currIndex = nums1.length;
        for (int j = 0; j < nums2.length; j++) {
            finalArray[currIndex] = nums2[j];
            currIndex++;
        }

        Arrays.sort(finalArray);
        int value = (finalArray.length / 2);

        if (finalArray.length % 2 > 0) {
            median = (double) finalArray[value];
        } else {
            median = (double) (finalArray[value] + finalArray[value - 1]) / 2;

        }

        return median;

    }
}