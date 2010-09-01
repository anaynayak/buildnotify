from paver.easy import *

@task
def clean():
    for fl in ['BuildNotify.egg-info', 'build', 'dist', 'deb_dist']:
        p = path(fl)
        p.rmtree()
        
@task
def mk_resources():
    sh('pyuic4 -o buildnotifylib/preferences_ui.py data/preferences.ui')
    sh('pyuic4 -o buildnotifylib/server_configuration_ui.py data/server_configuration.ui')

@task
@needs('dist_pypi', 'dist_ppa')
def dist():
    pass

@task
@needs('clean')
def dist_pypi():
    sh('python setup.py sdist upload')

    
@task
@needs('clean')
def dist_ppa():
    sh('python setup.py --command-packages=stdeb.command sdist_dsc')
    dist_package = path('deb_dist').dirs('buildnotify-*')[0]
    sh('sed -i s/unstable/lucid/ %s/debian/changelog' % dist_package)
    sh('cd %s;dpkg-buildpackage -i -S -I -rfakeroot' % dist_package)
    changes_file = path('deb_dist').files('*.changes')[0]
    sh('dput ppa:anay/ppa %s' % changes_file)
    
