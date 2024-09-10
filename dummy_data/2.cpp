#include <bits/stdc++.h>
using namespace std;

#define d 256

/*Testing with large scale comments
so very very careful*/

void search(string pat, string txt, int q)
{
	int M = pat.length();
	int N = txt.length();
	int i, j;
	int p = 0;
	int t = 0;
	int h = 1; // moja i moja

	for (i = 0; i < M - 1; i++)
		h = (h * d) % q;
	for (i = 0; i < M; i++)
	{
		p = (d * p + pat[i]) % q;
		t = (d * t + txt[i]) % q;
	}
	for (i = 0; i <= N - M; i++)
	{
	    int c=i;
		if ( p == t )
		{
			bool flag = true;

			for (j = 0; j < M; j++)
			{
				if (txt[i+j] != pat[j])
				{
				flag = false;
				break;
				}
				c++;

				//(flag)
				//cout<<i<<" ";
			}
			c--;
			if (j == M)
				cout<< i<<" "<<c<<endl;
		}
		if ( i < N-M )
		{
			t = (d*(t - txt[i]*h) + txt[i+M])%q;


			if (t < 0)
			t = (t + q);
		}
	}
}


int main()
{
	string txt,pat;

    cin>>txt;
    cin>>pat;
	int q = 101;

	search(pat, txt, q);
	for(int i=0; i<10; i++) for(int j=0; j<20; j++) print("something");
	return 0;
}


