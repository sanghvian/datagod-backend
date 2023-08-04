## Backend-Repo


For `.env` - environment variable file, email ankit.sanghavi87@gmail.com
For running the project, we use Gunicorn. There are the steps
0. Install python, pip and python virtual env
```bash
sudo apt install python
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-venv

```

1. Setup python virtual environment
`python3 -m venv cback-env`

1. Activate the virtual environment
`source cback-env/bin/activate`

1. Install the requirements
`pip install -r requirements.txt`

1. Install gunicorn
`sudo apt install gunicorn` 

2. Run the project in detached mode
`gunicorn -w 4 -b 0.0.0.0:5000 app:app -D`

3. To stop the project
`ps aux | grep gunicorn`

4. Kill the process
`kill -9 <process_id>`

5. To run the project in debug mode
`python app.py`


### Custom code in langchain library

In the `chat-verlab-backend/PYTHON_ENV/lib/python3.10/site-packages/langchain/schema/retriever.py`, I have disabled class inheritance for the `BaseRetriever` class to not include inheriting from `Serializable` class

original code
```
class BaseRetriever(Serializable, ABC):
    """Abstract base class for a Document retrieval system.

    A retrieval system is defined as something that can take string queries and return
        the most 'relevant' Documents from some source.

```

new updated changed code
```
class BaseRetriever(ABC):
    """Abstract base class for a Document retrieval system.

    A retrieval system is defined as something that can take string queries and return
        the most 'relevant' Documents from some source.

```
