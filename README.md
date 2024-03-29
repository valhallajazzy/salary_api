# Сравниваем вакансии программистов

Данный скрипт выводит в консоль таблицу со статистикой по вакансиям программистов в городе Москва основываясь на 
данных с сайтов [HEADHUNTER](https://hh.ru/) и [SUPERJOB](https://www.superjob.ru/).

![Screenshot](https://github.com/valhallajazzy/salary_api/blob/main/pic_readme/salary_api.png)

## Запуск скрипта

Для запуска скрипта потребуется зарегистрироваться на сайте [SUPERJOB](https://www.superjob.ru/) и получить `Secret key`
по ссылке https://api.superjob.ru/info/.

* Переходим в корневую директорию проекта.

* Cоздаем виртуальное окружение и устанавливаем требуемые библиотеки, запускаем виртуальное окружение:

```console
$ poetry install
$ poetry shell
```

* В корневой директории проекта создаем файл .env и обозначить в нем переменную окружения `TOKEN_SUPER_JOB`
  присвоив ей полученный `Secret key`.

![Screenshot](https://github.com/valhallajazzy/salary_api/blob/main/pic_readme/token_superjob.png)

* Запускаем скрипт командой:

```console
$ python3 main.py
```
