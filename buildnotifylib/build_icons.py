import sys, os

class BuildIcons:
    success_sleeping = '/icon-success.png'
    success_building = '/icon-success-building.png'
    failure_sleeping = '/icon-failure.png'
    failure_building = '/icon-failure-building.png'
    unavailable = '/icon-inactive.png' 
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.all_status = {'Success.Sleeping':self.success_sleeping,
         'Success.CheckingModifications': self.success_sleeping,
         'Success.Building':self.success_building, 
         'Failure.Sleeping':self.failure_sleeping, 
         'Failure.CheckingModifications': self.failure_sleeping,
         'Failure.Building': self.failure_building, 
         'unavailable':self.unavailable }
        
 
    def for_status(self, status):
        if self.all_status.has_key(status):
            return self.root_dir + self.all_status[status]
        else: 
            return self.root_dir + self.all_status['unavailable']
