from flask import Flask, Response
from random import shuffle
import json


# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: "placeholder"))

# call with start and end integer. Produces permutated array and writes it to numbers.txt file
# includes start and end
@application.route("/gen_numbers/<start>/<end>")
def gen_numbers(start, end):
    with open("numbers.txt", "w+") as file:
        perm = list(range(int(start), int(end + 1)))
        shuffle(perm)
        file.write("".join([str(x) + "\n" for x in perm]))
    return "Generated numbers from " + start + " to " + end

@application.route("/pop_number")
def pop_number():
    with open("numbers.txt", "r+") as file:
        number = file.readline().strip("\n")
        rest = file.read()

    # truncates to rest of file
    with open("numbers.txt", "w+") as file:
        file.write(rest)

    if number == "":
        return "No numbers left. Please report to the creator of the survey."
    return "We received: " + str(number)

@application.route('/get_hello', methods = ['GET'])
def api_hello():
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'

    return resp

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
