# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json, os


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World! from action python code!")

        return []


class ActionJiraStatus(Action):

    def name(self) -> Text:
        return "action_jira_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        print('Entities are:')
        print(entities)

        for e in entities:
            if e['entity'] == 'app':
                app = e['value']

            if e['entity'] == 'status':
                status = e['value']

        message = self.jira_status(app, status)

        dispatcher.utter_message(text=message)

        return []

    def jira_status(self, app, status):
        a_file = open("actions/dataJson.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        new_status = status
        new_assignee = 'User2'

        # for item in json_object["projects"]:
        #     if item == 'jiraFields':
        #         for jf in json_object["projects"][item]:
        #             if jf == "status" and json_object["projects"][item][jf] != new_status:
        #                 json_object["projects"][item][jf] = new_status
        #             if jf == "assignee" and json_object["projects"][item][jf] != new_assignee:
        #                 json_object["projects"][item][jf] = new_assignee

        for item in json_object["projects"]:
            if item == 'jiraFields':
                for i, jf in enumerate(json_object["projects"][item]):
                    for key in jf:
                        # print(json_object["projects"][item])
                        if app == json_object["projects"][item][i]['jiraID'] and key == "status" and\
                                json_object["projects"][item][i][key] != new_status:
                            json_object["projects"][item][i][key] = new_status
                        if key == "assignee" and json_object["projects"][item][i][key] != new_assignee:
                            json_object["projects"][item][i][key] = new_assignee

        a_file = open("actions/dataJson.json", "w")
        json.dump(json_object, a_file)
        a_file.close()

        print('#### Done ####')
        return '--Jira status updated--'

