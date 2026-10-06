/*
 * Time: O(n)
 * Space: O(min(m, n))
 */
class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        std::unordered_map<char, int> hashmap;
        int maxlen = 0;
        int left = 0;
        int len = s.size();
        for (int right = 0; right < len; right++) {
            if(hashmap.find(s[right]) == hashmap.end()){
                hashmap[s[right]] = right;
            } else {
                left = max(left, hashmap[s[right]]+1);
                hashmap[s[right]]=right;
            }
            maxlen = max(maxlen,right-left+1);
        }
        return maxlen;
    }
};
