For environment variable file, email ankit.sanghavi87@gmail.com
For running the project, we use Gunicorn. There are 2 steps
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