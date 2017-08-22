import subprocess
from datetime import datetime


class ProjectStatusNotification(object):
    def __init__(self, config, old_integration_status, current_integration_status, notification):
        self.config = config
        self.old_integration_status = old_integration_status
        self.current_integration_status = current_integration_status
        self.notification = notification
        self.timed_project_filter = TimedProjectFilter()

    def show_notifications(self):
        project_status = ProjectStatus(self.old_integration_status.get_projects(),
                                       self.current_integration_status.get_projects())

        self.show_notification_msg(self.config.get_value("fixedBuild"),
                                   project_status.successful_builds(), "Fixed builds")
        self.show_notification_msg(self.config.get_value("brokenBuild"),
                                   project_status.failing_builds(), "Broken builds")
        self.show_notification_msg(self.config.get_value("stillFailingBuild"),
                                   project_status.still_failing_builds(), "Build is still failing")
        self.show_notification_msg(self.config.get_value("connectivityIssues"),
                                   self.unavailable_server_urls(), "Connectivity issues")
        self.show_notification_msg(self.config.get_value("successfulBuild"),
                                   project_status.still_successful_builds(), "Yet another successful build")

    def unavailable_server_urls(self):
        urls = [server.url for server in self.current_integration_status.unavailable_servers()]
        return self.timed_project_filter.filter(urls)

    def show_notification_msg(self, show_notification, builds, message):
        if show_notification is False or builds == []:
            return
        self.notification.show_message(message, "\n".join(builds))
        if self.config.get_custom_script_enabled():
            command = self.config.get_custom_script().replace('#status#', message).replace('#projects#',
                                                                                           ",".join(builds))
            subprocess.Popen(command, shell=True)


class TimedProjectFilter(object):
    map = dict()
    fact = [1, 2, 3, 5, 8, 13, 21]

    def __init__(self):
        pass

    def filter(self, urls):
        return [url for url in urls if self.is_new(url)]

    def is_new(self, url):
        if url not in self.map:
            self.map[url] = (datetime.now(), 1)
            return True
        connection_time, fail_count = self.map[url]
        fail_count += 1
        if self.fact[len(self.fact) - 1] <= fail_count:
            fail_count = 1
        self.map[url] = (connection_time, fail_count)
        return fail_count in self.fact


class ProjectStatus(object):
    def __init__(self, old_projects, current_projects):
        self.old_projects = old_projects
        self.current_projects = current_projects

    def failing_builds(self):
        return self.filter_all(lambda project_tuple: project_tuple.has_failed())

    def successful_builds(self):
        return self.filter_all(lambda project_tuple: project_tuple.has_succeeded())

    def still_failing_builds(self):
        return self.filter_all(lambda project_tuple: project_tuple.has_been_failing())

    def still_successful_builds(self):
        return self.filter_all(lambda project_tuple: project_tuple.has_been_successful())

    def filter_all(self, filter_fn):
        project_tuples = [self.tuple_for(project) for project in self.current_projects]
        return [project_tuple.current_project.label()
                for project_tuple in project_tuples if filter_fn(project_tuple)]

    def tuple_for(self, new_project):
        for project in self.old_projects:
            if new_project.matches(project):
                return ProjectTuple(new_project, project)
        return ProjectTuple(new_project, None)


class ProjectTuple(object):
    def __init__(self, current_project, old_project):
        self.current_project = current_project
        self.old_project = old_project

    def has_failed(self):
        return self.status('Failure', 'Success')

    def has_succeeded(self):
        return self.status('Success', 'Failure')

    def has_been_successful(self):
        return (self.old_project is None) or (
            self.status('Success', 'Success') and self.current_project.different_builds(self.old_project))

    def has_been_failing(self):
        return self.status('Failure', 'Failure') and self.current_project.different_builds(self.old_project)

    def status(self, new_status, old_status):
        return self.current_project.status == new_status and self.old_project is not None and self.old_project.status == old_status
