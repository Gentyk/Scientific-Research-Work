﻿

Сервис windows можно создать с помощью C#, однако из сервиса невозможно запустить exe (возможно инфа отсюда поможет: https://www.codeproject.com/Articles/35773/Subverting-Vista-UAC-in-Both-and-bit-Archite). Однако было решено добавить файл в автозагрузку, что спасло положение. На данный момент решено каждые 60+ секунд сохранять файл(во имя безопасности) в случае активности: если клики в браузере были, то мы закрываем файл, а потом снова открываем на запись. Зарытие происходит, когда служба в папке нашего файла создает файл "status.txt". 

Сервис, кейлоггер и лог будут храниться в одном файле.

На данный момент ЦП ест 0,2% при активной работе; памяти - 4Мб.. 
