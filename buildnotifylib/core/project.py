from dateutil.parser import parse
from datetime import datetime

class Project:
    def __init__(self, props):
        self.name = props['name']
        self.status = props['lastBuildStatus']
        self.activity = props['activity']
        self.url = props['url']
        self.server_url = props['server_url']
        self.last_build_time = props['lastBuildTime']
        self.last_build_label = props.get('lastBuildLabel', None)

    def get_build_status(self):
        return self.status + "." + self.activity

    def different_builds(self, project):
        return self.last_build_label != project.last_build_label

    def get_last_build_time(self):
        if len(self.last_build_time)==0:
            return datetime.now()
        return parse(self.last_build_time).replace(tzinfo=None)
