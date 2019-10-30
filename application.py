from flask import Flask, Response
from random import shuffle
import json
import boto3

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule(
    '/', 'index', (lambda: "Please append /gen_numbers to generate numbers or /pop_number to receive a random, unique user id"))

# prepares s3 bucket


def getBucket():
    s3 = boto3.resource("s3")
    return s3.Bucket("elasticbeanstalk-us-east-2-046856019993")

# call with start and end integer. Produces permutated array and writes it to numbers.txt file
# includes start and end
@application.route("/gen_numbers/<start>/<end>/<unique_identifier>")
def gen_numbers(start, end, unique_identifier):
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
    bucket.put_object(Key="numbers" + unique_identifier + ".txt", Body=text)
    return "Generated numbers from " + start + " to " + end + ". You can visit /pop_number to verify it is working (caution, this of course invalidates one id)."


@application.route("/gen_numbers")
def hint_gen_numbers():
    return "Hint: You probably try to generate numbers. Please append at the end of your path \"/start/end/unique_identifier\", replacing with your desired start and end range for user IDs. Please also append a unique identifier. This is used to make multiple surveys run in parallel."


@application.route("/pop_number_debug/<unique_identifier>")
def pop_number(unique_identifier):
    file_name = "numbers" + unique_identifier + ".txt"
    bucket = getBucket()
    for obj in bucket.objects.all():
        if obj.key == file_name:
            numbers = obj.get()["Body"].read().split()
            # aws returns us bytes
            numbers = [int(x) for x in numbers]

    if len(numbers) == 0:
        return "We cannot generate valid IDs at the moment. Please contact: markus.kneer@gmail.com"

    return_number = numbers[0]
    if len(numbers) > 1:
        rest = [str(x) for x in numbers[1:]]
    else:
        rest = []

    bucket.put_object(Key=file_name, Body="\n".join(rest))

    return str(return_number)


@application.route('/pop_number/<unique_identifier>', methods=['GET'])
def pop_number_uri(unique_identifier):
    data = {
        'user_id': pop_number(unique_identifier),
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')

    return resp


@application.route('/pop_number', methods=['GET'])
def pop_number_hint():
    return "You probably tried to pop a number. Please append the unique identifier of the ressource you wanted to pop. Example: Append /abc to pop the ressource with the identifier abc"


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
