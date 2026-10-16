/*
 * Time: O(n)
 * Space: O(1)
 */
class Solution {
public:
    vector<int> plusOne(vector<int>& digits) {
        int carry = 0;
        bool first = true;
        int size = digits.size();
        for(int i = size-1;i>0;i--){
            if(first){
                if(digits[i] == 9){
                    digits[i]=0;
                    carry = 1;
                    first = false;
                    continue;
                }
                else{
                    digits[i]+=1;
                    return digits;
                }
            }
            if(digits[i] != 9){
                digits[i]+=1;
                return digits;
            }
            digits[i]=0;
            carry = 1;
        }
        if(carry && digits[0] == 9){
            digits.resize(size+1);
            digits[size] = 0;
            digits[0]=1;
        } else if (digits[0] == 9){
            digits.resize(2);
            digits[0]=1;
            digits[1]=0;
        } else{
            digits[0]+=1;
        }
        return digits;
    }
};
