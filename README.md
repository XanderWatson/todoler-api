# TODOLER - Take Your First Baby Steps Towards Productivity

Assignment for Wobot internship

## Steps to run

- First clone the repo
```
git clone https://github.com/XanderWatson/todoler-api.git
```

- Then change your current directory to the project directory (in this case, todoler-api)
```
cd todoler-api/
```

- Now run the following command to install the dependencies
```
pipenv install
```

- Once the dependencies are installed, set the `SECRET_KEY` environment variable in the .env file after running
```
cp .env.example .env
```

- Finally run the application
```
uvicorn todoler.main:app --reload
```

This will run the server at http://localhost:8000

To try out the API, go to http://localhost:8000/docs, create a new user at the `/users/` endpoint and then authorize with the API using your username and password. You'll then be able to access all other secured endpoints.

## Techstack used
- Python 3.10 with pipenv
- FastAPI framework
- SQLAlchemy with sqlite database
- Uvicorn to run the ASGI server
