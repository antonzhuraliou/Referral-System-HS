#  Referral System API

##  Описание

Проект реализует систему авторизации по номеру телефона с поддержкой:
- Подтверждения 4-значным кодом (OTP),
- Присвоения 6-значного инвайт-кода новому пользователю,
- Возможности ввести чужой инвайт-код (один раз),
- Просмотра списка пользователей, которые использовали ваш инвайт-код.

##  Стек технологий

- Python
- Django / Django REST Framework
- DRF Spectacular 
- PostgreSQL
- Redis (для хранения OTP)
- Docker / Docker Compose
- JWT (SimpleJWT)
- Postman collection

## Установка и запуск

### 1. Клонируй проект
```bash
git clone git@github.com:antonzhuraliou/Referral-System-HS.git
cd refsys
```
### 2. Создай .env файл
```bash
DEBUG=1
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=refsys_db
POSTGRES_USER=refsys_user
POSTGRES_PASSWORD=strongpassword
```
### 3. Запусти проект
```bash
docker-compose up --build
```

## API Endpoints

### 1. Отправка кода (POST /login/send_code/)
```commandline
Request:

{
  "phone": "+375333478282"
}

Response:

{
  "message": "Verification code has been sent successfully."
}
```

### 2. Верификация кода (POST /login/verify_code/)
```bash
Request:
{
  "phone": "+375333478282",
  "code": "1234"
}

Response:

{
  'refresh': xxxxx,
  'access': yyyyy,
  'user_id': 1
}
```

### 3. Профиль (GET /get_profile/)
Требуется JWT токен. Показывает информацию о пользователе, активированный инвайт-код и список приглашённых пользователей.
```
Authorization: Bearer JWT_ACCESS
```
```bash
Response:

{
  "phone": "+1234567890",
  "own_invite_code": "X4F9ZQ",
  "activated_invite_code": "K5J3RW",
  "invited_users": [
    "+1231231234",
    "+3213213210"
  ]
}
```

### 4. Активация инвайт-кода (POST /use_invite_code/)
```bash
Request:
{
  "invite_code": "ALG242",
}

Response:

{
  "message": "Invite code applied successfully. Welcome!"
}
```

## JWT Аутентификация
Проект использует JWT (JSON Web Token) для аутентификации пользователей. Все защищённые маршруты требуют заголовка Authorization с access-токеном.
```commandline
Authorization: Bearer <access_token>
```

## Обновление токена
```commandline
POST /api/token/refresh/
Используйте refresh токен, чтобы получить новый access токен
```
## Postman Collection
Полная коллекция API запросов доступна в виде Postman-файла в формате JSON
.
