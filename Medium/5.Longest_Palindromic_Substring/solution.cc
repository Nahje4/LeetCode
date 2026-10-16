/*
 * Time: O(n)
 * Space: O(n)
 */
class Solution {
public:
    string longestPalindrome(string s) {
        string bis = "#";
        for(auto c : s){
            bis += c;
            bis += "#";
        }
        int n = bis.size();
        int center = 0;
        int right = 0;
        std::vector<int> W(n,0);
        for(int i = 0; i < n; ++i){
            if(i < right){
                W[i] = std::min(right - i, W[2*center-i]);
            }
            while(i - W[i] - 1 >= 0 && i + W[i] + 1 < n && bis[i - W[i] - 1] == bis[i + W[i] + 1]){
                ++W[i];
            }
            if(i + W[i] > right){
                center = i;
                right = i + W[i];
            }
        }
        int best = std::max_element(W.begin(),W.end()) - W.begin();
        return s.substr((best - W[best])/2,W[best]);
    }
};
