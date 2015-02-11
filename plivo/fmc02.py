import os
from flask import Flask, Response, request, url_for
import plivoxml
import logging
import logging.config

# This file will be played when a caller presses 2.
PLIVO_SONG = "https://s3.amazonaws.com/plivocloud/music.mp3"

# Voice used for speaking. MAN or WOMAN
VOICE='MAN'

# This is the message that Plivo reads when the caller dials in
Greeting = "Welcome to the Prayer Line of Fellowship Mission Church. Please press 1 \
    at any time to continue to the Prayer Line. Please press 2 for our \
    seasonal worship service. Please press 3 for our location and directions\
    to our Congregation." #Please press 7 to join as a Prayer Coordinator."

GREETING2 =  "The Prayer Line will begin shortly."

SCHEDULE = "___"

LOCATION = "___"

CONFERENCE_WAIT_SONG = "https://s3-us-west-2.amazonaws.com/music-queue/test34.wav"

# This is the message that Plivo reads when the caller does nothing at all
NO_INPUT_MESSAGE = "Please try again."

# This is the message that Plivo reads when the caller inputs a wrong number.
WRONG_INPUT_MESSAGE = "There is no option assigned to your selection. Please \
                        try again."

CONFERENCE_NAME = "PrayerLine"
#import logging files
logging.config()
logger = logging.getlogger()

SPEAKER_PIN = '8824'

app = Flask(__name__)

# @app.route('/response/ivr', methods=['POST']) #, 'POST'])
# def ivr():
#     response = plivoxml.Response()
#     # GetDigit XML Docs - http://plivo.com/docs/xml/getdigits/
#
#
#     return Response(str(response), mimetype='text/xml')

#Set this as the answer URL
@app.route('/response/main_menu', methods=['GET', 'POST'])
def main_menu():
    response = plivoxml.Response()

    if request.method == 'GET':
        g = response.addGetDigits(action=url_for('main_menu', _external=True),
                                       method='POST', timeout=7, numDigits=1,
                                       retries=1)

        g.addSpeak(GREETING)
        response.addSpeak(NO_INPUT_MESSAGE)
    elif request.method == 'POST':
        digit = request.form.get('Digits')

        if digit == '1':
            # TODO: use digitsMatch to ask for pin and if match unmute?
            response.addConference(
                CONFERENCE_NAME, waitSound=url_for('conference_listener_wait',_external=True),
                startConferenceOnEnter='false', muted='true', stayAlone='false',
                record='true'
            )
        if digit == '2':
            #sms('schedule.')
            response.addSpeak(SCHEDULE, voice=VOICE)
            response.addRedirect(url_for('main_menu', _external=True), method='GET')
        if digit == '3':
            #sms('directions.')
            response.addSpeak(LOCATION, voice=VOICE)
            # NOTE: plivo does not seem to support adding a pause. What you can do is playing
            #  an empty/muted sound file of the desired length
            response.addSpeak("For more information, including directions, \
                please visit fellowship mission church.org", voice=VOICE)
            response.addRedirect(url_for('main_menu', _external=True), method='GET')
        if digit == '4':
            #sms('nothing (4).')
            pass

        if digit == '5':
            #sms('spanish version.')
            response.addSpeak("...", voice='alice', language='es-MX')

        if digit == '7':
            response.addRedirect(url_for('conference_speaker', _external=True), method='GET')
        # if digit == '9':
        #     # Repeat main menu
        #     response.addRedirect(url_for('main_menu', _external=True), method='GET')
        else:
            response.addRedirect(url_for('repeat_menu', _external=True), method='GET')

    return Response(str(response), mimetype='text/xml')


@app.route('/response/repeat_menu/', methods=['GET', 'POST'])
def repeat_menu():
    """
    Repeats the main menu (and passes transfer back) after pressing '9'. This could be used
    as a generic 'repeat menu' service if we used the information where the user was
    redirected to here from. (See Redirect documentation).

    This is not perfect. I would simply add option 9 to the main menu (then both repeat and
    selecting a valid option works).
    """
    response = plivoxml.Response()

    if request.method == 'GET':
        g = response.addGetDigits(action=url_for('repeat_menu', _external=True),
                               method='POST', timeout=7, numDigits=1,
                               retries=1)
        g.addSpeak("Please press 9 to repeat.")
    elif request.method == 'POST':
        if request.form.get('Digits') == '9':
            response.addRedirect(url_for('main_menu', _external=True), method='GET')
        else:
            response.addRedirect(url_for('repeat_menu', _external=True), method='GET')

    return Response(str(response), mimetype='text/xml')


@app.route('/response/conference/listener/wait', methods=['POST'])
def conference_listener_wait():
    response = plivoxml.Response()

    response.addPlay(CONFERENCE_WAIT_SONG)

    return Response(str(response), mimetype='text/xml')

def add_conference_pin_request(response, header_text):
    g = response.addGetDigits(numDigits=4, action=url_for('conference_speaker', _external=True))
    g.addSpeak('%s Please enter the code to host the conference.' % header_text,voice=VOICE)

    return response

@app.route('/response/conference_speaker', methods=['GET', 'POST'])
def conference_speaker():
    response = plivoxml.Response()

    if request.method == 'GET':
        add_conference_pin_request(response, 'Prayer Coordinators,')
    elif request.method == 'POST':
        if request.form.get('Digits') == SPEAKER_PIN:
            # response.addConference(
            #     CONFERENCE_NAME, startConferenceOnEnter='true', muted='false', stayAlone='true',
            #     record='true', callbackUrl=url_for('conference_callback'), callbackMethod='POST'
            # )

            response.addConference(
                CONFERENCE_NAME, startConferenceOnEnter='true', muted='false', stayAlone='true',
                record='true', callbackUrl=url_for('conference_callback', _external=True),
                callbackMethod='POST'
            )
        else:
            add_conference_pin_request(response, 'Please try again. ')

    return Response(str(response), mimetype='text/xml')


@app.route('/response/conference_callback', methods=['POST'])
def conference_callback():
    """
    This URL is called when a conference event happens. (Only set for the speakers for now, as
    it seems to make sense so.) Here you can handle the beginning and the end of a recording.
    E.g. download the recording when it has ended.
    """
    values = request.form
    action = values.get('ConferenceAction')
    #comment below out, to avoid confusion?
    print values

    print 'Conference event:'
    print '  action = %s (event = %s)' % (action, values.get('Event'))

    # 'Event' and 'ConferenceRecordStop' are undocumented by Plivo
    if action == 'record' and values.get('Event') == 'ConferenceRecordStop':
        # You would start the download here (but not from this thread, because that may take
        #  too long and cause plivo to timeout.
        record_file = values.get('RecordFile')
        print '*********Conference recording has finished. Recording url: %s' % record_file

    return Response()

# Set this url as the fallback url on plivio app setup page. This url will be called on app
#  errors and thus can be used for debugging (displaying/logging) the error and recovery
#  (e.g. sending the caller back to the main menu, maybe telling them that there was an error)
@app.route('/response/error_handler/', methods=['POST'])
def error_handler():
    print 'Pilvo error:'
    print '  ', request.values, request.data

    response = plivoxml.Response()
    response.addRedirect(url_for('ivr', _external=True))

    return Response(str(response), mimetype='text/xml')


# Set this as the Hangup URL on the plivio app setup page. This is completely optional, can be
#  used for logging
@app.route('/response/hangup_handler/', methods=['POST'])
def hangup_handler():
    print 'Call has been hung up'

    return Response()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)


