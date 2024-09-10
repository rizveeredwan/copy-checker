#include <bits/stdc++.h>
using namespace std;
#define MAX 100
#define INF 10000000


struct Dijkstra{
    int edge;
    int node;

    vector<int>graph[MAX+1]; // edge
    vector<int>weight[MAX+1]; //weight

    int dist[MAX+5]; //result
    int source;

    void init(){
        for(int i=0;i<MAX;i++){
            dist[i] = INF;
        }
    }

    void algorithm(){
        dist[source]=0;
        queue<int>Q;
        Q.push(source);

        while(Q.empty() != true) {
            int u =Q.front();
            Q.pop();
            for(int i=0;i<graph[u].size();i++){
                int v = graph[u][i];
                if(dist[v] > dist[u]+weight[u][i]) {
                    Q.push(v);
                    dist[v]=dist[u]+weight[u][i];
                }
            }
        }
        for(int i=1;i<=node;i++){
            cout<<dist[i]<<endl;
        }
    }
};

int main(void){

    freopen("in.txt","r",stdin);

    Dijkstra d;
    cin>>d.edge;
    cin>>d.node;
    for(int i=0;i<d.edge;i++){
        int a,b,c;
        cin>>a>>b>>c;
        d.graph[a].push_back(b);
        d.weight[a].push_back(c);

        d.graph[b].push_back(a);
        d.weight[b].push_back(c);
    }
    d.init();
    cin>>d.source;
    d.algorithm();
    return 0;
}
