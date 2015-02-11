import logging
import logging.config
import sys
import os
from flask import Flask, Response, request, url_for
import plivoxml
import settings, greetings

########################### Taken from greeting.py
# This is the message that Plivo reads when the caller dials in
GREETING = greetings.welcome_greeting

SCHEDULE = greetings.schedule_and_focus

LOCATION = greetings.directions_and_info

# Hold music
custom_music = greetings.custom_hold_music
default_music = greetings.default_hold_music

# This is the message that Plivo reads when the caller does nothing at all
NO_INPUT_MESSAGE = greetings.NO_INPUT_MESSAGE

# This is the message that Plivo reads when the caller inputs a wrong number.
WRONG_INPUT_MESSAGE = greetings.WRONG_INPUT_MESSAGE

########################### Taken from greeting.py END ###############
#
#############Begin Prayer Line Python code
#
# Each Prayer Line/Conference requires a title
CONFERENCE_NAME = "PrayerLine"

#Prayer coordinator Pin
SPEAKER_PIN = settings.pin_number

# Voice used for speaking. MAN or WOMAN
VOICE='alice'

app = Flask(__name__)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'recording': {
            'format': '[%(asctime)s]: %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s::%(asctime)s::%(module)s -- %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'recordings_file': {
            'level': 'INFO',
            'filename': 'recordings.log',
            'class': 'logging.FileHandler',
            'formatter': 'recording'
        },
        'logfile': {
            'level': 'DEBUG',
            'filename': 'debug.log',
            'class': 'logging.FileHandler',
            'formatter': 'verbose'
        }
    },

    'loggers': {
        'recordings': {
            'handlers': ['recordings_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'root': {
            'handlers': ['logfile', 'console'],
            'level': 'INFO',
            'propagate': True
        },
    }
})

logger = logging.getLogger(__name__)
recordings = logging.getLogger('recordings')

@app.route('/response/main_menu', methods=['GET', 'POST'])
def main_menu():
    logger.debug('New call')
    logger.debug('--')
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
            response.addSpeak(SCHEDULE)#, voice=VOICE)
            response.addRedirect(url_for('main_menu', _external=True), method='GET')
        if digit == '3':
            #sms('directions.')
            response.addSpeak(LOCATION)#, voice=VOICE)
            # NOTE: plivo does not seem to support adding a pause. What you can do is playing
            #  an empty/muted sound file of the desired length
            response.addSpeak("For more information, including directions, \
                please visit fellowship mission church.org")#, voice=VOICE)
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
    g.addSpeak('%s Please enter the code to host the conference.' % header_text,voice=alice) ##VOICE variable

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

    # print values
    #
    # print 'Conference event:'
    # print '  action = %s (event = %s)' % (action, values.get('Event'))

    # 'Event' and 'ConferenceRecordStop' are undocumented by Plivo
    if action == 'record' and values.get('Event') == 'ConferenceRecordStop':
        # You would start the download here (but not from this thread, because that may take
        #  too long and cause plivo to timeout.
        record_file = values.get('RecordFile')
        recordings.info('Conference recording has finished. Recording url: %s' % record_file)

    return Response()

# Set this url as the fallback url on plivio app setup page. This url will be called on app
#  errors and thus can be used for debugging (displaying/logging) the error and recovery
#  (e.g. sending the caller back to the main menu, maybe telling them that there was an error)
@app.route('/response/error_handler/', methods=['POST'])
def error_handler():
    logger.error('Pilvo error: %s , %s' % (request.values, request.data))

    response = plivoxml.Response()
    response.addRedirect(url_for('ivr', _external=True))

    return Response(str(response), mimetype='text/xml')


# Set this as the Hangup URL on the plivio app setup page. This is completely optional, can be
#  used for logging
@app.route('/response/hangup_handler/', methods=['POST'])
def hangup_handler():
    # print 'Call has been hung up'

    return Response()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
