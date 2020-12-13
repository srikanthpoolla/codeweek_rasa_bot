# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
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


class ActionJiraLogHours(Action):

    def name(self) -> Text:
        return "action_jira_log_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        print('Entities are:')
        print(entities)

        for e in entities:
            if e['entity'] == 'proj':
                app = e['value']

            if e['entity'] == 'hrs':
                hours = e['value']


        message = self.log_hours(app, hours)

        dispatcher.utter_message(text=message)

        return []

    def log_hours(self, jira_no, hrs):
        date = '01-01-2000'
        a_file = open("actions/dataJson.json", "r")
        json_object = json.load(a_file)
        a_file.close()
        proj_id = jira_no.split('-')[0]

        project = json_object['projects']
        if project['projectID'] == proj_id:
            for jira in project['jiraFields']:
                if jira['jiraID'] == jira_no:
                    input_dict = {'Date': date,
                                  'Hours': hrs,
                                  'Comments': 'test comments'}
                    jira['workLog'].append(input_dict)
                else:
                    print("Jira not mapped under project")
        else:
            print("Invalid project")

        a_file = open("actions/dataJson.json", "w")
        json.dump(json_object, a_file)
        a_file.close()

        print('#### Done ####')
        return '--Hours have been logged--'


class JiraForm(FormAction):

    def name(self) -> Text:
        return "create_jira_form"

    @staticmethod
    def required_slots(tracker):
        return ['proj_id', 'summary', 'estimate', 'description', 'jira_type']

    def slot_mappings(self):
        return {
            "proj_id": [
                self.from_entity(entity='proj_id')
            ],
            "summary": [
                self.from_text(intent='get_summary'),
                self.from_text(intent='get_desc')
            ],
            "description": [
                self.from_text(intent='get_desc'),
                self.from_text(intent='get_summary')
            ],
            "estimate": [
                self.from_intent(intent='get_est', value=None),
                self.from_entity(entity='estimate')
            ]
        }

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:

        summary = tracker.get_slot('summary')
        estimate = tracker.get_slot('estimate')
        description = tracker.get_slot('description')
        proj_id = tracker.get_slot('proj_id')

        entities = tracker.latest_message['entities']
        print('######')
        print(entities)
        for e in entities:
            if e['entity'] == 'proj_id':
                proj_id = e['value']

            if e['entity'] == 'jira_type':
                jira_type = e['value']

        print(summary, estimate, description, proj_id, jira_type)
        self.create_jira(estimate, proj_id, jira_type)
        return []

    def create_jira(self, est, jira, type):
        a_file = open("actions/dataJson.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        new_jira = {"jiraID": jira, "type": type, "epic": "techFix", "status": "Open", "assignee": "User10", "estimate": est}
        for item in json_object["projects"]:
            if item == 'jiraFields':
                for i, jf in enumerate(json_object["projects"][item]):
                    json_object["projects"][item].append(new_jira)
                    break

        a_file = open("actions/dataJson.json", "w")
        json.dump(json_object, a_file)
        a_file.close()

        return

