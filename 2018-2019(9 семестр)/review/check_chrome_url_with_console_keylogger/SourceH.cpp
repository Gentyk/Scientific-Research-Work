#include "stdafx.h"
#include "atltypes.h"
#include "atlstr.h"
#include <string>
#include <psapi.h>
#include <commdlg.h>
#include <AtlBase.h>
#include <AtlCom.h>
#include <UIAutomation.h>	// работа с пользовательским интерфейсом
#include "Header.h"

#define UNICODE

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
		}
		/*else	// здесь пытался работать с мазилой -по неизвествной причине не работает
		{
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

		CComPtr<IUIAutomationElement> edit; // редактор
		if (FAILED(root->FindFirst(TreeScope_Descendants, condition, &edit))
			|| !edit)
			continue; //maybe we don't have the right tab, continue...
		CComVariant url;
		edit->GetCurrentPropertyValue(UIA_ValueValuePropertyId, &url);
		url1 = url.bstrVal;
		str_url = OLE2CA(url1);
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
