/*
 * Time: O(2^(m + n/2))
 * Space: O(m + n)
 */
class Solution {
public:
    bool isMatch(string s, string p) {
        return fn_match(s.c_str(),p.c_str());
    }
private:
    bool fn_match(const char *s, const char *p){
        if (*p == '\0'){
            return *s == '\0';
        }
        bool first = *s != '\0' && (*p == '.' || *p == *s);
        if (p[1] == '*'){
            return fn_match(s, p + 2) || (first && fn_match(s + 1, p));
        }
        return first && fn_match(s + 1, p + 1);
    }
};
