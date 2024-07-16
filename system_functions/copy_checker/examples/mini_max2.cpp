#include <bits/stdc++.h>

bool MAX(int a, int b){
    if(a > b) return true;
    return false;
}

bool MIN(int a, int b){
    if(a < b) return true;
    return false;
}


int main(void){
    cout<<MAX(10, 30)<<endl;
    cout<<MIN(10, 30)<<endl;
    return 0;
}
