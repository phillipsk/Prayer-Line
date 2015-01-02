import os
from flask import Flask, Response, request, url_for
import plivoxml
from utils import joke_from_reddit, conf
import plivo

# This file will be played when a caller presses 2.
PLIVO_SONG = "https://s3.amazonaws.com/plivocloud/music.mp3"

# This is the message that Plivo reads when the caller dials in
greeting = "Welcome to the Prayer Line of Fellowship Mission Church. Please press 1 \
            at any time to continue to the Prayer Line. Please press 2 for our \
            seasonal worship service. Please press 3 for our location and directions\
            to our Congregation."

greeting2 =  "The Prayer Line will begin shortly."

# This is the message that Plivo reads when the caller does nothing at all
NO_INPUT_MESSAGE = "Please try again."

# This is the message that Plivo reads when the caller inputs a wrong number.
WRONG_INPUT_MESSAGE = "There is no option assigned to your selection. Please \
                        try again."

app = Flask(__name__)


@app.route('/response/ivr', methods=['GET', 'POST'])
def ivr():
    response = plivoxml.Response()
    if request.method == 'GET':
        # GetDigit XML Docs - http://plivo.com/docs/xml/getdigits/
        getdigits_action_url = url_for('main_menu', _external=True)
        getDigits = plivoxml.GetDigits(action=getdigits_action_url,
                                       method='POST', timeout=7, numDigits=1,
                                       retries=1)

        getDigits.addSpeak(greeting)
        response.add(getDigits)
        response.addSpeak(NO_INPUT_MESSAGE)

        return Response(str(response), mimetype='text/xml')
def comment_out():
    """
    pass
    elif request.method == 'POST':
        digit = request.form.get('Digits')

        if digit == "1":
            # Fetch a random joke using the Reddit API.
            #joke = joke_from_reddit()
            #response.addSpeak(joke)
            #start_conference = conf()
            #response.start_conference(conf)
            #response.addConference
            confe()

        elif digit == "2":
            # Listen to a song
            #response.addPlay(PLIVO_SONG)
            response.addConference
        else:
            response.addSpeak(WRONG_INPUT_MESSAGE)

        return Response(str(response), mimetype='text/xml')
        """


@app.route('/response/main_menu', methods=['GET', 'POST'])
def main_menu():
    response = plivoxml.Response()
    sms('main menu.')
    if request.method == 'POST':
        digit_pressed = request.values.get('Digits', None)

        if digit_pressed == '1':
            sms('prayer line.')
            with response.dial() as d:
              d.addConference('conference-1', muted=True)
        if digit_pressed == '2':
            sms('schedule.')
            response.say("Our current seasonal focus is Sharing and Caring through Prayer. Our Worship \
                service schedule is as follows: \
                Sunday Worship service begins at 12 noon, \
                with Sunday Prayer \
                and Sunday School services beginning earlier in the day at 10:30 am. \
                During the week, \
                Prayer is held on Tuesday nights at 7:30pm and Bible Study begins at 7:30pm on \
                Friday nights.", voice=v, action='/response/main_menu')
        if digit_pressed == '3':
            sms('directions.')
            response.say("Our Congregation is centered between the historic Fort Hill neighborhood \
                and directly behind Roxbury Community College. We are steps away from the Orange Line \
                Roxbury Crossing T Station. Our direct address is 85 Centre Street, Roxbury, 02119. The \
                spelling of 'Centre' street is 'C. E. N. T. R. E.'.", voice=v) #action='/response/main_menu'
            response.pause(length = "2")
            response.say("For more information, including directions, \
                please visit fellowship mission church.org", voice=v) #action='/response/main_menu'
        if digit_pressed == '4':
            sms('nothing (4).')
            response.pause(length='1')
        
        if digit_pressed == '5':
            sms('spanish version.')
            response.say(Espanol_G, voice='alice', language='es-MX')

        if digit_pressed == '7':
            sms('host prompt.')
            with response.gather(numDigits=4, action='/response/conference_speaker') as g:
                g.say('Prayer Coordinators, Please enter the code to host the conference.', voice=v)

        # TODO: handle the rest of the menu here:

        else:
            with response.gather(numDigits=1, action='/response/') as g:
                g.pause(length = "6")
                g.say("Please press 9 to repeat these options.", voice=v)
                g.pause(length = "13")
                g.say("Thank you for calling the Prayer Line of Fellowship Mission \
                    Church, May the Peace of the Lord be With you, and God Bless!", voice=v)
            #response.say('Invalid choice')
            # TODO: say main menu and gather responses again

    return Response(str(response), mimetype='text/xml')

@app.route('/response/conference/', methods=['GET', 'POST'])
def confe():
    response = plivoxml.Response()


    if request.method == 'GET':  #use to be GET  
        response.addSpeak(greeting2)  
        getdigits_action_url = url_for('conference', _external=True)
        getDigits = plivoxml.GetDigits(action=getdigits_action_url,
                                       method='POST', timeout=15, numDigits=4,
                                       retries=1, finishOnKey='#')
        getDigits.addSpeak('If you know your conference pin, please enter the pin followed by the # key.')
        response.add(getDigits)
        response.addSpeak(NO_INPUT_MESSAGE)
        return Response(str(response), mimetype='text/xml')

    elif request.method == 'POST':
        digit = request.form.get('Digits')

        if digit == "1989":
            # Fetch a random joke using the Reddit API.
            #joke = joke_from_reddit()
            #response.addSpeak(joke)
            start_conference = conf()
            response.start_conference(conf)
            
        elif digit == "2":
            # Listen to a song
            response.addPlay(PLIVO_SONG)
        else:
            response.addSpeak(WRONG_INPUT_MESSAGE)

        return Response(str(response), mimetype='text/xml')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
