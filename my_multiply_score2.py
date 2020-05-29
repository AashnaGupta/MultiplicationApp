import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import random

connection = sqlite3.connect('users.db')
stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if (r == []):
    exp = 'CREATE TABLE users (username,password)'
    connection.execute(exp)


def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None

    if path == '/':
        page = '''<!DOCTYPE html>
        <html>
        <head><title>Simple Form</title></head>
        <body>
        <h1>Multiply with Score</h1>
        <form>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit"value="Log in" formaction = "/login"> 
            <input type="submit"value="Register" formaction = "/register">
        </form>
        <hr>
        </body></html>'''
        printDB()
        start_response('200 OK', headers)
        return [page.encode()]


    elif path == '/login':
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <p><a href="/account">Account</a></p>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password.<br><br>Register if you are not registered. <p><a href="/"> Retry Log in</a></p>'.encode()]


        #start_response('200 OK', headers)
        #return [page.encode()]


    elif path == '/register':
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken <p><a href="/"> Retry Register</a></p>'.format(un).encode()]
        else:
            connection.execute('INSERT INTO users VALUES (?, ?)', [un, pw])
            connection.commit()

            start_response('200 OK', headers)
            return ['Username {} successfully created.<p><a href="/"> Log in Now </a></p>'.format(un).encode()]


        #start_response('200 OK', headers)
        #return [page.encode()]

    elif path == '/account':
        message = '<p style="background-color: white"> <font size="8" color="black"> Welcome to Multiply with Score</font>'
        start_response('200 OK', headers)

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            correct = 0
            wrong = 0

            if 'HTTP_COOKIE' in environ:
                cookies = http.cookies.SimpleCookie()
                cookies.load(environ['HTTP_COOKIE'])
                if 'score' in cookies:
                    correct = int(cookies['score'].value.split(':')[0])
                    wrong = int(cookies['score'].value.split(':')[1])

            if 'factor1' in params and 'factor2' in params and 'answer_choices' in params:
                f1= (params['factor1'][0])
                f2= (params['factor2'][0])
                clicked_answer = int((params['answer_choices'][0]))
                answer = int(f1) * int(f2)
                if answer == clicked_answer:
                    correct = correct + 1
                    message = '<p style="background-color: lightgreen"> <font size="8">Correct, {} x {} = {}</font>'\
                        .format(f1,f2,answer)
                else:
                    wrong = wrong + 1
                    message = '<p style="background-color: red"> <font size="8">Wrong, {} x {} = {}</font>'\
                        .format(f1,f2,answer)

            elif 'reset' in params:
                correct = 0
                wrong = 0

            headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))

            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1
            a1 = f1 * 5 + 4
            answer = f1 * f2
            a3 = f2 * 4 + 11
            a4 = f1 + 2 * 3

            answer_choices = [a1, answer, a3, a4]
            random.shuffle(answer_choices)

            random.shuffle(answer_choices)

            hyperlink1 = '<a href= "/account?factor1={}&amp;factor2={}&amp;answer_choices={}" </a>'.format(f1,f2, answer_choices[0])
            hyperlink2 = '<a href= "/account?factor1={}&amp;factor2={}&amp;answer_choices={}" </a>'.format(f1, f2,answer_choices[1])
            hyperlink3 = '<a href= "/account?factor1={}&amp;factor2={}&amp;answer_choices={}" </a>'.format(f1, f2,answer_choices[2])
            hyperlink4 = '<a href= "/account?factor1={}&amp;factor2={}&amp;answer_choices={}" </a>'.format(f1, f2,answer_choices[3])

            page = '<h1>{}</h1> <h1>What is {} x {}?</h1> <p> <h1>A: {} {}</a> </h1> </p>'\
                   '<p> <h1>B: {} {}</a> </h1> </p> <p> <h1>C: {} {}</a> </h1> </p>'\
                   '<p> <h1>D: {} {}</a> </h1> </p>'\
                .format(message, f1, f2, hyperlink1, answer_choices[0],hyperlink2 , answer_choices[1],
                        hyperlink3 , answer_choices[2],hyperlink4, answer_choices[3])

            page += ''' <hr>
                        <h2>Score</h2>
                        Correct: {}<br>
                        Wrong: {}<br>
                        <a href="/account?reset=true">Reset</a>
                        <br>
                        <hr>
                        <br>
                        <a href="/logout">Logout</a>
                        </body></html>'''.format(correct, wrong)

            return [page.encode()]


        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/"><br><br>Login</a>'.encode()]
    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]



def printDB():
    user_cursor = cursor.execute('SELECT * FROM users')
    user_list = user_cursor.fetchall()

    for user in user_list:
        print(user)

httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()