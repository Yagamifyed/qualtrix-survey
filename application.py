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
    # sanity checks
    # checks for abnormally large range
    range_size = abs(int(start) - int(end)) 
    if range_size > 10000:
        return "Abnormally large range entered. Not generating anything."

    if not int(end) > int(start):
        return "Please enter an end number that is bigger than the starting number. Not generating anything."

    if int(end) < 0 or int(start) < 0:
        return "Please enter positive numbers. Not generating anything."

    bucket = getBucket()

    perm = list(range(int(start), int(end) + 1))
    shuffle(perm)
    text = "".join([str(x) + "\n" for x in perm])
    bucket.put_object(Key="numbers.txt", Body=text)
    return "Generated numbers from " + start + " to " + end

@application.route("/pop_number_debug")
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

    return str(return_number)

@application.route('/pop_number', methods = ['GET'])
def api_hello():
    data = {
        'user_id'  : pop_number,
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')

    return resp

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
