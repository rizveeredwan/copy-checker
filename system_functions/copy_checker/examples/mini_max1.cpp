#include <bits/stdc++.h>

bool _min(int A, int B){
    if(A < B) return true;
    return false;
}


bool _max(int A, int B){
    if(A > B) return true;
    return false;
}

int main(void){
    cout<<_min(10, 30)<<endl;
    cout<<_max(10, 30)<<endl;
    return 0;
}
