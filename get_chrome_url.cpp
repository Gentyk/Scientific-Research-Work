// ConsoleApplication4.cpp: определяет точку входа для консольного приложения.
//

#include "stdafx.h"
#define UNICODE
#include <Windows.h>
#include <AtlBase.h>
#include <AtlCom.h>
#include <UIAutomation.h>	// работа с пользовательским интерфейсом??

int main()
{
	CoInitialize(NULL);		// необходимо для инициализации COM-потока
	HWND hwnd = NULL;		// hwnd - уникальный номер экземпляра окна программы
	while (true)
	{
		hwnd = FindWindowEx(		// функция поиска дочерних окон
			0,						// дескриптор родительского окна ( hwndParent - ПУСТО (NULL), функция использует окно рабочего стола как родительское окно.)
			hwnd,					// дескриптор дочернего окна (если и hwndParent и hwndChildAfter - ПУСТО (NULL), функция ищет все окна верхнего уровня)
			L"Chrome_WidgetWin_1",	// указатель имени класса
			NULL					// указатель имени окна (Если этот параметр ПУСТО (NULL), имена всех окон соответствующие.)
		);
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

		CComVariant url;
		edit->GetCurrentPropertyValue(UIA_ValueValuePropertyId, &url);
		MessageBox(0, url.bstrVal, 0, 0);
		break;
	}
	CoUninitialize();	// закрытие COM-потока
	return 0;
}
