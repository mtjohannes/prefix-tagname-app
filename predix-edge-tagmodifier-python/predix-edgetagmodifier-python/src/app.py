import os
import sys
import traceback
import json
import paho.mqtt.client as mqtt

class App():
    '''
    This application subscribes to data on an MQTT data topic,
    and republishes it with a new tagname using the prefix.

    Attributes:
        predix_edge_broker - the name of the predix edge broker as defined
                            in our docker-compose file
        topic - either a string or a list of strings indicating which topic(s) to subsrcibe to
        tag_name - string indicating the tag of the data we want to modify
        client - manages relationship with MQTT data broker
    '''

    def __init__(self, predix_edge_broker, topic, prefix):
        '''
        Initializes App class with default names for predix_edge_broker,
        a single topic called 'app_data', and a sample tag to look for
        '''
        self.predix_edge_broker = predix_edge_broker
        self.topic = topic
		self.prefix = prefix
        self.client = mqtt.Client()

        #add MQTT callbacks and enable logging for easier debugging
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.message_callback_add(self.topic, self.tagname_on_message)
        self.client.enable_logger()

    def on_connect(self, client, userdata, flags, rc):
        '''
        The callback for when the client receives a CONNACK response from the server.
        The variables it takes are part of the underlying MQTT library
        '''
        print("Connected with result code "+str(rc))
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        '''
        The callback for when a PUBLISH message is received from the server.
        '''
        print(msg.topic+" "+str(msg.payload))

    def on_publish(self, client, userdata, is_published):
        '''
        the callback for when we send something to be published
        '''
        print("Is published " + str(is_published))


    def tagname_on_message(self, client, userdata, msg):
        '''
        Specific callback for our topic
        '''
        #Convert message from bytearray to json object
        payload_as_string = bytes.decode(msg.payload)
        payload = json.loads(payload_as_string)

        new_tagname_payload = new_tagname(payload, prefix)
 
        payload_as_string = json.dumps(new_tagname_payload)
        client.publish(self.topic, payload_as_string.encode())

def new_tagname(message, prefix):
    '''
    This function takes in a JSON message and adds the prefix to each tagname
    '''
    item = message['body']
    length = len(item)
    for i in range(length):
		item[i]['name'] = prefix + "." + item[i]['name']
    return message

if __name__ == '__main__':
    #Set broker values if we are running locally
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            BROKER = "127.0.0.1"
            TOPIC = "timeseries_data"
			PREFIX = "prefix"
    #Otherwise, read from environment variables
    else:
        try:
            BROKER = os.environ['BROKER']
            TOPIC = os.environ['TOPIC']
			PREFIX = os.environ['PREFIX']
        except KeyError:
            print(traceback.print_tb(sys.exc_info()[2]))
            sys.exit("Not all of your environment variables are set")
    APP = App(BROKER, TOPIC, PREFIX)
    APP.client.connect(APP.predix_edge_broker)
    APP.client.loop_forever()
