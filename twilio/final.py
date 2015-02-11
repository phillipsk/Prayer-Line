#!/env/bin/python
import os
from flask import Flask, Response, request
import twilio.twiml
import settings
from twilio.rest import TwilioRestClient

# Urls to set up in twillio number setup (Voice)
# request url:  ... /response/
# fallback url: ... /response/error_handler/

app = Flask(__name__)

ACCOUNT_SID = settings.api_tok
TOKEN = settings.api_tok
Twilio_number = settings.from_number
Ministry_number = settings.to_number

v = "Alice" #choose from 'man', 'alice', or 'woman'

Greeting = "Welcome to the Prayer Line of Fellowship Mission Church. Please press 1 \
    at any time to continue to the Prayer Line. Please press 2 for our \
    seasonal worship service. Please press 3 for our location and directions\
    to our Congregation."

S_schedule_S_focus = "Our current seasonal focus is 'Worship, Wisdom and Witnessing: Go and Tell Somebody!' \
                Our Worship service schedule is as follows: \
                Sunday Worship service begins at 12 noon, \
                with Sunday Prayer \
                and Sunday School services beginning earlier in the day at 10:30 am. \
                During the week, \
                Prayer is held on Tuesday nights at 7:30pm and Bible Study begins at 7:30pm on \
                Friday nights."

M_directions = "Our Congregation is centered between the historic Fort Hill neighborhood \
                and directly behind Roxbury Community College. We are steps away from the Orange Line \
                Roxbury Crossing T Station. Our direct address is 85 Centre Street, Roxbury, 02119. The \
                spelling of 'Centre' Street is 'C. E. N. T. R. E.'."

M_info = "For more information, including directions, \
                    please visit fellowship mission church.org"

P_coord = 'Prayer Coordinators, Please enter the code to host the conference.'

Espanol_G = "Bienvenido a la linea de oracion de la Iglesia Mision de Becas . Por favor, pulse 1 \
    en cualquier momento para seguir la linea de oracion . Por favor, pulse 2 para nuestro \
    servicio de adoracion de temporada . Por favor, pulse 3 para nuestra ubicacion y como llegar \
    a nuestra Congregacion ."#.encode("utf-8")

exit_M = "Thank you for calling the Prayer Line of Fellowship Mission \
                    Church, May the Peace of the Lord be With you and God Bless!"

error_M = 'Please try again. Please enter the code with or without the pound key.'



#MAIN_MENU = 'Press 1 to join conference as a speaker, 2 to join conference as a moderator'

@app.route('/response/', methods=['GET', 'POST'])
def welcome():
    response = twilio.twiml.Response()
    # response.say(Greeting)
    sms()

    with response.gather(numDigits=1, action='/response/main_menu') as g:
        g.say(Greeting, voice=v)
    sms()
    sms('nothing (4).')
    return Response(str(response), mimetype='text/xml')

@app.route('/response/main_menu', methods=['GET', 'POST'])
def main_menu():
    response = twilio.twiml.Response()
    sms('main menu.')
    if request.method == 'POST':
        digit_pressed = request.values.get('Digits', None)

        if digit_pressed == '1':
            sms('prayer line.')
            with response.dial() as d:
                d.addConference('conference-1', muted=True)
        if digit_pressed == '2':
            sms('schedule.')
            response.say(S_schedule_S_focus, voice=v, action='/response/main_menu')
        if digit_pressed == '3':
            sms('directions.')
            response.say(M_directions, voice=v) #action='/response/main_menu'
            response.pause(length="2")
            response.say(M_info, voice=v) #action='/response/main_menu'
        if digit_pressed == '4':
            sms('nothing (4).')
            response.pause(length='1')
        
        if digit_pressed == '5':
            sms('Spanish version.')
            response.say(Espanol_G, voice='alice', language='es-MX')

        if digit_pressed == '7':
            sms('host prompt.')
            with response.gather(numDigits=4, action='/response/conference_speaker') as g:
                g.say(P_coord, voice=v)

        #TODO: handle the rest of the menu here:

        else:
            with response.gather(numDigits=1, action='/response/') as g:
                g.pause(length="6")
                g.say("Please press 9 to repeat.", voice=v)
                g.pause(length="7")
                g.say(exit_M, voice=v)
            #response.say('Invalid choice')
            # TODO: say main menu and gather responses again

    return Response(str(response), mimetype='text/xml')

@app.route('/response/conference_speaker', methods=['POST'])
def conference_speaker():
    response = twilio.twiml.Response()
    
    if request.values.get('Digits') == '8824':
        with response.dial() as d:
          d.addConference('conference-1')
    else:           
        response.say(error_M, voice=v) #!!!!!!!!!!
        
    return Response(str(response), mimetype='text/xml')

# Set this url as the fallback url on twilio number setup page:
# https://www.twilio.com/user/account/phone-numbers/ ....
@app.route('/response/error_handler/', methods=['GET', 'POST'])
def error_handler():
    print 'Twilio error:'
    print '  ', request.values, request.data

    response = twilio.twiml.Response()
    response.say('An error has occured. You are taken back to the main menu.', voice=v)

    with response.gather(numDigits=1, action='/response/main_menu') as g:
        g.say(Greeting)

    return Response(str(response), mimetype='text/xml')

def sms(s):
    # put your own credentials here 
    ACCOUNT_SID = settings.api_sid
    AUTH_TOKEN = settings.api_tok  
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)  
    calls = client.calls.list(status='in-progress')
    first_call = calls[0]
    to_number = first_call.to
    from_number = first_call.from_
    #call_id = (call.sid)
    #for call in calls:
    #        print(call.sid)
    #first_call = calls[0]
    message_1 = client.messages.create(
        to=settings.to_number, 
        from_=settings.num_formal, 
        body="%s has joined the prayer line! They are listening to the %s" % (from_number, s)  
    )
    #first_call = calls[0]
    #print(first_call.__dict__)
    print message_1
   

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port=port)
