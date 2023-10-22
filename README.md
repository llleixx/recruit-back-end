## Recruit

Run this project:

1. install dependencies (use `python -m venv` first)

    ```bash
    pip install -r requirements.txt
    ```

2. modify `.env` file

    You need to use your own `SECRET_KEY` and own `EMAIL`

3. create your database

    You need to create the database whose name is the val of the key `MYSQL_DBNAME` in `.env`

4. run this project

    ```bash
    python3 main.py
    ```

    or

    ```bash
    uvicorn app.app:app
    ```

5. see the interface documentation

    Open your browser and to this `http://127.0.0.1:8000/docs`

## Database

### users

Field|Type|Null|Key|Default|Extra
-|-|-|-|-|-
id|int|NO|PRI|NULL|auto_increment
name|varchar(16)|NO||NULL|
email|varchar(30)|YES||NULL|
password|varchar(60)|NO||NULL|
permission|int|NO||NULL|

`name` and `email` will be ensured unique by the logic of the code.

`password` is hashed and verified by `CryptContext(schemes=["bcrypt"], deprecated="auto")` in `passlib.context`.

`permission` can only be in $[0, 2]$. The less it is, you'll get more permissions.

### problems

Field|Type|Null|Key|Default|Extra
-|-|-|-|-|-
id|int|NO|PRI|NULL|auto-increment
owner_id|int|NO||NULL|
name|varchar(30)|NO||NULL|
description|varchar(2000)|YES||NULL|
answer|varchar(2000)|NO||NULL|
score_initial|int|NO||NULL|
score_now|int|NO||NULL|

`description` can be `Nullullullullullullullullull`.

`score_initial` should be greater than or equals to 10, and should be multiple of 10.

`score_now` initially equals to `score_initial`. If a person answre a question, it's score will decrease $\dfrac{1}{10}$ of `score_initial`. Its minimum is $\dfrac{1}{10}$ of `score_initial`.

### userproblemlink

Field|Type|Null|Key|Default|Extra
-|-|-|-|-|-
user_id|int|NO|PRI|NULL|
problem_id|int|NO|PRI|NULL|

If someone answer a problem which is not answered before, then a data will be added to this table.

The scores of users are calculated by this table.

If a user or problem is deleted, the table is also affected.

### confirmations

Field|Type|Null|Key|Default|Extra
-|-|-|-|-|-
email|varchar(30)|NO|PRI|NULL|
option|varchar(10)|NO|PRI|NULL|
token|varchar(6)|NO||NULL
create_time|datetime|NO||CURRENT_TIMESTAMP|DEFAULT_GENERATED

It's used to check the tokens about email to finish some operations like binding email, modifying password, modifying email and logging.

`option`'s value is in `("BIND", "LOGIN", "MODIFY)`.

`token` is a 6-digit string which is randomly generated.

## Flow

If you have question with this docs, I will use `curl` to see the complete flow for you. You can use `postman` to get better experience.

### Login

You can login with the username and password detailed in `.env`

```bash
curl \
-H "Content-Type: multipart/form-data" \
-X POST \
-F "username=root" \
-F "password=123" \
http://localhost:8000/token
```

Then you can get a token which will be expired after 30 minutes.

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjk3ODg0MzAxfQ.xM5W4N2wxpQy-4OAfOA5VEbfGArxzCkapk1ZQVz28DE",
    "token_type": "bearer"
}
```

Before do anything else below, you can store the token as environment variable for convenience.

```bash
TOKEN=...
```

You can get your information by:

```bash
curl \
-X GET \
-H "Authorization: Bearer $TOKEN" \
http://localhost:8000/me
```

### Bind

You can't do anything expcept getting the problem data or user data if you don't bind an email.

So you'd better bind an email first.

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-X POST \
-d '{"email": "xx@xx", "option": "BIND" }' \
http://localhost:8000/sendEmail
```

Note that `"BIND"` are uppercase.

If you successfully do it, you will get:

```json
{"detail": "SUCCESS"}
```

After that, check your email and get the token (which will be expired after 3 minutes), and do:

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-H "email-token: 828621" \
-X PUT \
-d '{"email": "xx@xx"}' \
http://localhost:8000/users/${your_user_id}
```

Then you can get the information after you update.

### CRUD about users and problems

Check this site: `http://127.0.0.1:8000/docs`

### Modify your email

Send your old email token with `"MODIFY"`, and sned your new email token with `"BIND"`

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-X POST \
-d '{"email": "old@email", "option": "MODIFY" }' \
http://localhost:8000/sendEmail
```

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-X POST \
-d '{"email": "new@email", "option": "BIND" }' \
http://localhost:8000/sendEmail
```

Then, do this:

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-H "email-token: theFormerToken" \
-H "email-token1: theLatterToken" \
-X PUT \
-d '{"email": "new@email"}' \
http://localhost:8000/users/${your_user_id}
```

### Answer problem

If you havd added problem, then you can answer.

```bash
curl \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-X POST \
-d '{"answer": "youranswer"}' \
http://localhost:8000/users/${user_id}/problems/${problem_id}
```

You will get this if your answer is right:

```json
{"detail": "ACCEPTED"}
```

Or you'll get:

```json
{"detail": "WRONG"}
```

### Get rank

You can get the rank of users who have score. (it's feature)

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
-X GET \
http://localhost:8000/users/rank
```