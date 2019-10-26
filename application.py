from flask import Flask, Response
from random import shuffle
import json
import boto3

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

# prepares s3 bucket
def getBucket():
    s3 = boto3.resource("s3")
    return s3.Bucket("elasticbeanstalk-us-east-2-046856019993")

# call with start and end integer. Produces permutated array and writes it to numbers.txt file
# includes start and end
@application.route("/gen_numbers/<start>/<end>")
def gen_numbers(start, end):
    bucket = getBucket()

    perm = list(range(int(start), int(end) + 1))
    shuffle(perm)
    text = "".join([str(x) + "\n" for x in perm])
    bucket.put_object(Key="numbers.txt", Body=text)
    return "Generated numbers from " + start + " to " + end

@application.route("/pop_number")
def pop_number():
    bucket = getBucket()
    for obj in bucket.objects.all():
        if obj.key == "numbers.txt":
            numbers = obj.get()["Body"].read().split()
            # aws returns us bytes
            numbers = [int(x) for x in numbers]


    if len(numbers) == 0:
        return "We have no numbers left. Please contact the maintainer of this survey."

    return_number = numbers[0]
    if len(numbers) > 1:
        rest = [str(x) for x in numbers[1:]]

    bucket.put_object(Key="numbers.txt", Body="\n".join(rest))

    return "We received: " + str(return_number)

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
