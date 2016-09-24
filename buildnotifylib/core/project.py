from dateutil.parser import parse
from datetime import datetime


class Project:
    def __init__(self, server_url, prefix, props):
        self.server_url = server_url
        self.prefix = prefix
        self.name = props['name']
        self.status = props['lastBuildStatus']
        self.activity = props['activity']
        self.url = props['url']
        self.last_build_time = props['lastBuildTime']
        self.last_build_label = props.get('lastBuildLabel', None)

    def get_build_status(self):
        return self.status + "." + self.activity

    def label(self):
        if self.prefix:
            return "[" + self.prefix + "] " + self.name
        return self.name

    def different_builds(self, project):
        return self.last_build_label != project.last_build_label

    def get_last_build_time(self):
        if len(self.last_build_time) == 0:
            return datetime.now()
        return parse(self.last_build_time).replace(tzinfo=None)
