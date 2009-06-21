import os
from xml.dom import minidom
import urllib2
import socket
class Project:
    def __init__(self, props):
        self.name = props['name']
	self.status = props['lastBuildStatus']
        self.activity = props['activity']
	self.lastBuildTime = props['lastBuildTime']
	self.url = props['url']
    def get_build_status(self):
	return self.status + "." + self.activity
	
class Projects: 
    def __init__(self, urls):
        self.urls = urls
        self.all_projects = []
        
    def load_from_server(self, conf, callback):
        self.all_projects = []
        for url in self.urls:
        	self.check_nodes(conf, url)
        if not self.all_projects == []:
            callback(self)
        
    def get_build_status(self):
        if (self.all_projects == []):
            return "unavailable"
        if (self.get_failing_builds() == []):
            return 'Success.Sleeping' 
        return "Failure.Sleeping"
           
    def get_failing_builds(self):
        failing_builds = []
        for project in self.all_projects:
            if project.status == 'Failure':
                failing_builds.append(project)
        return failing_builds
        
    def check_nodes(self, conf, url):
        socket.setdefaulttimeout(conf.timeout)
        try:
            data=urllib2.urlopen(url)
        except (Exception), e:
            return
        dom = minidom.parse(data)
        for node in dom.getElementsByTagName('Project'):
            self.all_projects.append(Project({'name': node.getAttribute('name'), 'lastBuildStatus':node.getAttribute('lastBuildStatus'),
                'activity': node.getAttribute('activity'), 'url': node.getAttribute('webUrl'), 'lastBuildTime': node.getAttribute('lastBuildTime')}))

