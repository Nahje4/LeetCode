/*
 * Time: O(n)
 * Space: O(n)
 */
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        std::unordered_map<int,int> hashmap;
        for(int i = 0;i < nums.size();i++){
            int comp = target - nums[i];
            if(hashmap.find(comp) != hashmap.end()){
                return {hashmap[comp],i};
            }
            hashmap[nums[i]]=i;
        }
        return {};
    }
};
