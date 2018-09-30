﻿# Scientific-Research-Work
Научно-исследовательская работа

Тема: 
Система аутентификации пользователя пользователя по поведению при просмотре веб-страниц

Составные части:
1. Кейлоггер, который считывает при каждом клике положение мыши и проверяет не произошел ли клик в браузере. Если так, то в лог пишется время, положение мыши, корординаты окна браузера и URL(строго говоря URI) активной вкладки. 
2. Строго говоря необходимо запилить модуль для перехвата get-запросов. Я использую Wireshark. Но есть несколько проблем: во-первых, не удалось расшифровать HTTPS (HTTP - удалось), на котором большинство запросов; во-вторых, wireshark очень сильно грузит систему - многие не смогут работать с ним.
3. Модуль принятия решения.


Папка "2017-2018" содержит кейлоггер на python. Но он не работает с хромом и медленный: каждый раз при клике в браузере появляется колечко загрузки.
Папка "2018-2019(1)" содержит законченный кейлоггер для хрома на C++.

Источники информации:
работа с url chrome - http://qaru.site/questions/7302957/get-active-tab-url-in-chrome-with-c
