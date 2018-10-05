#include <string>
#include <fstream>
#include <windows.h>

using namespace std;

// то, благодаря чему у нас не вываливается консоль каждый раз
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
	LPSTR lpszCmdLine, int nCmdShow)
{
	string   s;
	int i = 0;
	ifstream is(".txt");
	ofstream os("out.txt");
	while (!(is.good())) {
		i++;
		Sleep(1000);
		os << i << endl;
		is.open("in1.txt");
	}
	return 0;
}
