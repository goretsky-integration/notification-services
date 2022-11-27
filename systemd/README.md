# Использование systemd calendar для периодических задач

## Порядок установки:

### Файлы из директории [services](./services)

- Прописать команду запуска в поле ExecStart в `.service` файлах.
- Скопировать в директорию `/lib/systemd/system`.

### Файлы из директории [timers](./timers)

- При необходимости, настроить поле `OnCalendar`.
- Скопировать в директорию `/etc/systemd/system`

После этого нужно включить каждый сервис `systemctl enable *service_name*`.

В конце перезапустить демон `systemctl daemon-reload`.
