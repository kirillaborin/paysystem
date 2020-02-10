## Запуск:
* установить переменные окружения в .env

* ```docker-compose up -d```

адрес API: http://127.0.0.1:8080/


## Особенности:
* В качестве механизма авторизации используется JWT, что позволяет не хранить токены на сервере.
* При первоначальном старте проекта накатывается data-миграция с системным пользователем
* Счета создаются в синхронных сигналах (billing.signals)
* Транзакции разбиты по типам. У транзакции есть привязка к счету получателя и к счету отправителя. Комиссия фиксируется отдельной операцией, получателем является системный аккаунт
* За логику переводов отвечает прокси-модель Transaction