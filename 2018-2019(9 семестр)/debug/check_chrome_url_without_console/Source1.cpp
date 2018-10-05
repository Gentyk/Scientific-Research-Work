#include "atltypes.h"
#include "atlstr.h"
#include <string>
#include <psapi.h>
#include <commdlg.h>
#include <AtlBase.h>
#include <AtlCom.h>
#include <UIAutomation.h>	// ������ � ���������������� �����������
#include "Header.h"

#define UNICODE

string get_url(string windows_name)
{
	USES_CONVERSION;
	CoInitialize(NULL);		// ���������� ��� ������������� COM-������
	HWND hwnd = NULL;		// hwnd - ���������� ����� ���������� ���� ���������
	BSTR url1 = NULL;
	string str_url;
	while (true)
	{
		if (windows_name.find("chrome") != string::npos)
		{
			hwnd = FindWindowEx(		// ������� ������ �������� ����
				0,						// ���������� ������������� ���� ( hwndParent - ����� (NULL), ������� ���������� ���� �������� ����� ��� ������������ ����.)
				hwnd,					// ���������� ��������� ���� (���� � hwndParent � hwndChildAfter - ����� (NULL), ������� ���� ��� ���� �������� ������)
				"Chrome_WidgetWin_1",	// ��������� ����� ������
				NULL					// ��������� ����� ���� (���� ���� �������� ����� (NULL), ����� ���� ���� ���������������.)
			);
		}
		/*else	// ����� ������� �������� � ������� -�� ������������ ������� �� ��������
		{
		hwnd = FindWindowEx(0, hwnd, "MozillaWindowClass", NULL);
		}*/
		if (!hwnd)
			break;
		if (!IsWindowVisible(hwnd))	// ������� ������ � ��������� ��������� ��������� ����
			continue;

		CComQIPtr<IUIAutomation> uia;	// CComQIPtr - ��������������� ��������� ��� COM-��������
										// IUIAutomation - ������������� ������, ����������� ���������� �����������
										// Microsoft UI Automation ������������, �������� ������ � ����������� 
										// �������� ������������� ����������������� ����������
		if (FAILED(uia.CoCreateInstance(CLSID_CUIAutomation)) || !uia)
			break;

		CComPtr<IUIAutomationElement> root;		// IUIAutomationElement - ���� ������� ����������������� ���������� 
		if (FAILED(uia->ElementFromHandle(hwnd, &root)) || !root)
			break;


		CComPtr<IUIAutomationCondition> condition;	// ���������

													// ������������� URL-������ ����� 0xC354 ��� ������������ UIA_EditControlTypeId ��� ������� ���� ��������������
		uia->CreatePropertyCondition(		// ������� �������, ������� �������� ��������, � ������� ���� �������� � ��������� ���������
			UIA_ControlTypePropertyId,		// ������������� ��������
			CComVariant(0xC354),			// �������� ��������
			&condition						// ��������� �� ����� �������
		);

		CComPtr<IUIAutomationElement> edit; // ��������
		if (FAILED(root->FindFirst(TreeScope_Descendants, condition, &edit))
			|| !edit)
			continue; //maybe we don't have the right tab, continue...
		CComVariant url;
		edit->GetCurrentPropertyValue(UIA_ValueValuePropertyId, &url);
		url1 = url.bstrVal;
		str_url = OLE2CA(url1);
		break;
	}
	CoUninitialize();	// �������� COM-������
	return str_url;
}

string get_active_window()
{
	/*
	* �������, ������������ ������������ ��������� ����
	*/
	DWORD pid;
	GetWindowThreadProcessId(GetForegroundWindow(), &pid);		// �������� ������������� ��������, �������� ����������� �������� ����
	HANDLE hProc = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,	// �������� ��������� (����������, �����) ��������
		FALSE, pid);														// ��� �������� �������� ���������� ������� ����� �� PROCESS_QUERY_INFORMATION � ��������� ������������ ���������� � ��������.

	if (hProc)
	{
		TCHAR szPath[MAX_PATH];
		GetProcessImageFileName(hProc, szPath, sizeof(szPath));
		CloseHandle(hProc);

		// �������� ������� ��� �����. ���� GetProcessImageFileName �� �����-��
		// �������� ����������� �� ����, � ������ ���, ���������� ������ ���.
		TCHAR szTitle[MAX_PATH];
		if (GetFileTitle(szPath, szTitle, sizeof(szTitle)) == 0)
			return string(szTitle);
		else
			return string(szPath);
		CloseHandle(hProc);
	}
	else
	{
		// ������ ��� �������� ��������. �� ������������� � � GetLastError()
		return string();
	}
}