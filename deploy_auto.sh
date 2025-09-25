#!/usr/bin/expect -f

set timeout 30
set password "buddy278skincare"

# Upload app.py
spawn scp app.py budduskincarevn@gmail.com@files.pythonanywhere.com:/home/buddyskincare/websitemypham/app.py
expect "password:"
send "$password\r"
expect eof

# Upload main.js
spawn scp static/js/main.js budduskincarevn@gmail.com@files.pythonanywhere.com:/home/buddyskincare/websitemypham/static/js/main.js
expect "password:"
send "$password\r"
expect eof

# Upload views.py (Django)
spawn scp views.py budduskincarevn@gmail.com@files.pythonanywhere.com:/home/buddyskincare/websitemypham/views.py
expect "password:"
send "$password\r"
expect eof

puts "✅ All files deployed successfully!"
puts "🔄 Please reload your web app on PythonAnywhere"