Yatube - соцсеть для публикации постов.
Стек: Python 3, Django, Django REST Framework, Unittest
В данной соцсети есть возможность публиковать посты с картинками, комментировать эти посты, а также подписываться на понравившихся авторов.

## Оглавление
<ul>
 <li><a href="#Описание">Описание</a> </li>
  <li><a href="#Стек">Стек</a> </li>
 <li>
   <a href="#Установка-интерпретатора-Python">Установка интерпретатора Python</a>
   <ul>
     <li><a href="#Windows">Windows</a></li>
     <li><a href="#MacOS">MacOS</a></li>
     <li><a href="#Linux">Linux</a></li>
   </ul>
 </li>
 <li>
   <a href="#Как-запустить-проект">Как запустить проект</a>
   <ul>
     <li><a href="#Проект-на-Windows">Проект на Windows</a></li>
     <li><a href="#Проект-на-MacOS">Проект на MacOS/Linux(Ubuntu)</a></li>
   </ul>
 </li>
</ul>



# Описание:

:wave:

*Yatube - соцсеть для публикации постов. :writing_hand: В данной соцсети есть возможность публиковать посты с картинками, комментировать эти посты, а также подписываться на понравившихся авторов.*

# Стек
Python 3, Django, Django REST Framework, Unittest

# Установка интерпретатора Python:
В проекте используется Python версии 3.9.10. 
# Windows

- Перейдите на [сайт Python, в раздел downloads](https://www.python.org/downloads/)
- Скачайте версию 3.9.10. (Выберите файл, подходящий для разрядности вашей операционной системы)
- Когда скачается, запустите установочный файл и когда откроется окно установки, обязательно поставьте галочку (!) возле пункта Add Python 3.9 to PATH и нажмите Install now.

# MacOS

- Откройте терминал. 
- Установите [Homebrew](https://brew.sh/)
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Добавьте пакетный менеджер Homebrew к переменным окружения. Последовательно введите в терминал и выполните команды:

```
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
- Проверьте, установлен ли Python версии 3.9.10
```
brew search python
```
- Если данная версия Python не установлена, введите команду:
```
brew install python@3.9 
```
- После установки проверьте, что Homebrew установил версию 3.9 версией по умолчанию для Python:
```
python3 --version
```
- Если это не так:
```
# Отвяжите текущую версию.
brew unlink python@3.текущая_версия
# Установите новую привязку.
brew link python@3.9
```

# Linux
- Чтобы узнать версию Python, введите команду:
```
python3 --version 
```

- Если текущая версия 3.9, у вас всё готово к работе. Если нет, нужно её установить. Будем следовать такому плану:
Обновим пакеты системы.
Установим нужную версию Python.
Убедимся, что установка прошла успешно.
Чтобы обновить пакеты системы, нужно использовать пакетный менеджер. Один из таких менеджеров — apt. Введите поочередно команды:
```
sudo apt update && sudo apt upgrade
sudo apt install python3.9 -y
sudo apt install python3.9-venv 
```
- Убедитесь, что установилась правильная версия Python:
```
python3.9 --version 
```

# Установка Git Bash для Windows:
[Скачайте](https://gitforwindows.org/) и установите Git Bash - приложение, которое поддерживает необходимую систему команд.

# Как запустить проект:

# Проект на Windows
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/infinitum6666/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
<p align="right">(<a href="#top">Наверх</a>)</p>

# Проект на MacOS
***Также можно использовать для Linux(Ubuntu).*** 

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/infinitum6666/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip3 install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

<p align="right">(<a href="#top">Наверх</a>)</p>
