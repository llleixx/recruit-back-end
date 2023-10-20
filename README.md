## Recruit

Run this project:

1. install dependencies

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

5. see the interface documentation

    Open your browser and to this `http://127.0.0.1:8000/docs`

## Flow

If you have question with this docs, I will use `curl` to see the complete flow for you. You can use `postman` to get better experience.
