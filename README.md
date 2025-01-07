**Приложение для определения избыточного давления по аналоговому манометру с последующей передачей информации на верхний уровень.**  
Разработка приложения состоит из нескольких этапов:
1. Создание приложения с детекцией круга/манометра, фиксация кадра с манометром и последущая отправка кадра в базу данных.
2. Разработка и использование в приложении модуля для определения избыточного давления по зафикисрованному кадру.
3. Адаптация приложения для смартфона на ОС Android.  
4. Опытно-промышленная эксплуатация прилоежения.
5. Анализ и доработка приложения.
Для углубленного курса по программированию на Python планируется выполнить 1 этап разработки.

Состояние проекта на 07.01.2024:  
* добавлены параметры для управления задержкой детектирования и сохранения кадра для повышения/стабилизации качества сохраняемого кадра  
* добавлена обрезка кадра с областью круга для снижения размера кадра
* кадры с кругом сохраняются в цвете и ч/б, после анализа на эффективность определения значения давления останется только один вариант

Состояние проекта на 06.01.2024:  
* добавлен параметр задержки в детектировании
* добавлен паттерн декоратор
* добавлена логика для сохранения кадра с кругом в файле
* пока не получилось добавить кадр с кругом в репозиторий приложения 


Состояние проекта на 04.01.2024:
* разработана диаграмма последовательности и прецендентов,
* создан репозиторий с двумя ветвями (главная - разработка по ноутбуку/шаблону, вторая - целевая),
* адаптирован код в главном скрипте main,
* реализовано детектирование круга,
* адаптированы паттерны: factory, observer, repository.
  
