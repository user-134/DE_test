## Описание
mc cp --version-id <OLD_VERSION_ID> \
  localminio/my-bucket/sales.csv \
  sales_old.csv
```

Подтверждение:

- Скрин списка версий объекта
<img width="764" height="90" alt="Снимок экрана 2026-02-01 в 19 22 29" src="https://github.com/user-attachments/assets/c4a8f28d-688b-4aae-b4c0-f2bf249bd0c0" />

Скрин скачивания старой версии
<img width="1346" height="54" alt="Снимок экрана 2026-02-01 в 19 24 46" src="https://github.com/user-attachments/assets/33f9a1f0-07a7-422e-9df8-58a3c6c599ab" />

---

## ЧАСТЬ 3. Lifecycle Policy (Auto Delete)

Требования
Автоматическое удаление объектов через 3 дня

Реализация
Lifecycle policy также настроена через MinIO Client (mc),
так как Web UI Community Edition не предоставляет интерфейс для ILM.

Добавление lifecycle-правила
```bash
mc ilm add --expire-days 3 localminio/my-bucket
```

Проверка правила
```bash
mc ilm ls localminio/my-bucket
```

Правило:

Status: Enabled

Expiration: 3 days

⚠️ Ожидание фактического удаления объектов не требуется —
достаточно наличия активного правила.

Подтверждение
Скрин вывода mc ilm ls

<img width="700" height="147" alt="Снимок экрана 2026-02-01 в 19 29 01" src="https://github.com/user-attachments/assets/ef8eaf59-5738-431a-a20f-ab39a9c57021" />

---

Итог
В ходе выполнения задания:
- Настроены политики доступа к бакету
- Реализована защита от перезаписи данных с помощью versioning
- Настроена автоматическая очистка хранилища через lifecycle policy

Все требования задания выполнены.
Использованы допустимые способы настройки: Web UI и S3-compatible API (MinIO Client).

---



