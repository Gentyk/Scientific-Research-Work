// ConsoleApplication5.cpp: определяет точку входа для консольного приложения.
// кейлогер - выдает координаты мышки при клике и имя активного окна
// код сырой и промежуточный

#include "stdafx.h"
#include "atltypes.h"
#include "atlstr.h"
#include <iostream>
#include <string>
#include <Windows.h>
#include <psapi.h>
#include <commdlg.h>

std::string get_active_window()
{
	/* Функция, возвращающая активное окно
	*/

	DWORD pid;
	GetWindowThreadProcessId(GetForegroundWindow(), &pid);		// получаем идентификатор процесса, которому принадлежит активное окно
	HANDLE hProc = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,	// получаем описатель (дескриптор, хендл) процесса
		FALSE, pid);														// При открытии процесса достаточно указать право на PROCESS_QUERY_INFORMATION — получение ограниченной информации о процессе.
	
	if (hProc)
	{
		TCHAR szPath[MAX_PATH];
		GetProcessImageFileName(hProc, szPath, sizeof(szPath));
		CloseHandle(hProc);

		// Пытаемся извлечь имя файла. Если GetProcessImageFileName по каким-то
		// причинам предоставил не путь, а просто имя, возвращаем именно его.
		TCHAR szTitle[MAX_PATH];
		if (GetFileTitle(szPath, szTitle, sizeof(szTitle)) == 0)
			return std::string(szTitle);
		else
			return std::string(szPath);
		CloseHandle(hProc);
	}
	else
	{
		// Ошибка при открытии процесса. За подробностями — к GetLastError()
		return std::string();
	}
}

int main()
{
	/* кейлоггер */
	int i;
	CPoint pt;
	CRect rect;
	HWND hWnd;
	std::string str;
	for (i = 1; i < 500; i++)
	{
		Sleep(100);
		if ((GetAsyncKeyState(VK_LBUTTON) != 0) || (GetAsyncKeyState(VK_RBUTTON) != 0) || (GetAsyncKeyState(VK_MBUTTON) != 0))
		{
			
			GetCursorPos(&pt);
			hWnd = GetForegroundWindow();
			GetWindowRect(hWnd, &rect);
			std::cout << "x = " << pt.x << "; x' = " << pt.x - rect.left << "\n";
			std::cout << "y = " << pt.y << "; y' = " << pt.y - rect.top << "\n\n";
			std::cout << get_active_window();
		}

	}
	return 0;
}

