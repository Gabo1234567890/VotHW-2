# VotHW-2

## Описание

Това е система за управление на файлове, използваща Docker Compose, MinIO S3 storage и Keycloak за автентикация с JWT токени. Приложението предоставя REST API за качване, сваляне, обновяване и изтриване на файлове.

## Функционалности

\- Управление на файлове \(качване, сваляне, обновяване и изтриване\).  
\- Локален S3 storage \(MinIO\).  
\- JWT базирана автентикация \(Keycloak\).

## Изисквания

\- Docker и Docker Compose \(версия 3.8 или по\-нова\).  
\- Git.

## Инструкции за стартиране

### 1. Клониране на репозиторията

```bash

git clone https://github.com/Gabo1234567890/VotHw-2.git
cd VotHw-2

```

### 2. Стартиране с Docker Compose

Стартирайте инфраструктурата и приложението с Docker Compose:

```bash

docker-compose up --build

```

### 3. Достъп до услугите

\- **MinIO Console**: http://localhost:9000
\- Потребител: `admin`  
 \- Парола: `admin123`  
\- **Keycloak**: http://localhost:8080
\- Администраторски акаунт:  
 \- Потребител: `admin`  
 \- Парола: `admin123`  
\- **Приложение \(REST API\)**: http://localhost:5000

## REST API – Примерни заявки

### 1. Качване на файл

```bash

curl -X POST "http://localhost:5000/upload"
-H "Authorization: Bearer <JWT_TOKEN>"
-F "file=@test.txt"

```

### 2. Сваляне на файл

```bash

curl -X GET "http://localhost:5000/download/<file_id>"
-H "Authorization: Bearer <JWT_TOKEN>"
-o downloaded-test.txt

```

### 3. Обновяване на файл

```bash

curl -X PUT "http://localhost:5000/update/<file_id>"
-H "Authorization: Bearer <JWT_TOKEN>"
-F "file=@new_test.txt"

```

### 4. Изтриване на файл

```bash

curl -X DELETE "http://localhost:5000/delete/<file_id>"
-H "Authorization: Bearer <JWT_TOKEN>"

```

## Проблеми и отстраняване

\- **Портовете са заети**: Уверете се, че портовете 5000, 8080 и 9000 не се използват от други приложения.  
\- **Keycloak не стартира**: Проверете логовете за грешки и уверете се, че имате поне 2 GB свободна RAM.  
\- **Не мога да се свържа с MinIO**: Уверете се, че правилно сте въвели потребител и парола.

## Конфигурация на Keycloak

1. Влезте в Keycloak администраторския интерфейс: http://localhost:8080.
2. Създайте Realm: `VotHw`.
3. Добавете клиент `vothw-api-client` \(OpenID Connect\).
4. Конфигурирайте ролята: `user`.

## Структура на проекта

```
VotHw-2/
|
├── config/ # Конфигурационен файл за Keycloak.
├── src/ # Основен код на приложението.
├── docker-compose.yml
└── README.md
```
