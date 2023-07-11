For environment variable file, email ankit.sanghavi87@gmail.com
For running the project, we use Gunicorn. There are 2 steps
1. Install gunicorn
`sudo apt install gunicorn` 

2. Run the project
`gunicorn -w 4 -b 0.0.0.0:5000 app:app -D`