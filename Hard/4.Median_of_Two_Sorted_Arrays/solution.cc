class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {
        int m = nums1.size();
        int n = nums2.size();
        if (m > n) {
            return findMedianSortedArrays(nums2, nums1);
        }
        int totalLeft = (m + n + 1) / 2;
        int left = 0, right = m;
        int left1 = 0, right1 = 0, left2 = 0, right2 = 0;
        while (left <= right) {
            int dep = left + (right - left) / 2;
            int dep2 = totalLeft - dep;
            left1 = (dep == 0) ? INT_MIN : nums1[dep - 1];
            right1 = (dep == m) ? INT_MAX : nums1[dep];
            left2 = (dep2 == 0) ? INT_MIN : nums2[dep2 - 1];
            right2 = (dep2 == n) ? INT_MAX : nums2[dep2];

            if (left1 <= right2 && left2 <= right1) {
                break;
            } else if (left1 > right2) {
                right = dep - 1;
            } else {
                left = dep + 1;
            }
        }
        int leftMax = max(left1, left2);
        int rightMin = min(right1, right2);
        if ((m + n) % 2 == 1) {
            return (double)leftMax;
        }
        return ((double)leftMax + rightMin) / 2.0;
    }
};
