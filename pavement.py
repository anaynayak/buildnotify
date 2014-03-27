from paver.easy import *

@task
def clean():
    for fl in ['BuildNotify.egg-info', 'build', 'dist', 'deb_dist']:
        p = path(fl)
        p.rmtree()
        
@task
def mk_resources():
    """Regenerate source corresponding to icons/Qt designer files"""
    sh('pyuic4 -o buildnotifylib/generated/preferences_ui.py data/preferences.ui')
    sh('pyuic4 -o buildnotifylib/generated/server_configuration_ui.py data/server_configuration.ui')
    sh('pyrcc4 data/icons.qrc -o buildnotifylib/generated/icons_rc.py')

@task
@needs('dist_pypi', 'dist_ppa')
def dist():
    """Triggers dist_pypi and dist_ppa"""
    pass

@task
@needs('clean')
def dist_pypi():
    """Upload package to https://pypi.python.org/pypi/BuildNotify/"""
    sh('python setup.py sdist upload')

@task
@needs('clean', 'mk_deb')
def dist_ppa():
    """Upload package to https://launchpad.net/~anay/+archive/ppa"""
    sh('python setup.py --command-packages=stdeb.command sdist_dsc --force-buildsystem=False')
    dist_package = path('deb_dist').dirs('buildnotify-*')[0]
    sh('sed -i s/unstable/precise/ %s/debian/changelog' % dist_package)
    sh('cd %s;dpkg-buildpackage -i -S -I -rfakeroot' % dist_package)
    changes_file = path('deb_dist').files('*.changes')[0]
    sh('dput ppa:anay/ppa %s' % changes_file)

@task
@needs('clean')
def mk_deb():
    """Build deb package"""
    sh('python setup.py --command-packages=stdeb.command bdist_deb')

@task
@needs('clean')
def mk_osc():
    """Upload package to https://build.opensuse.org/package/repositories/home:Anay/BuildNotifyTest"""
    sh('python setup.py sdist')
    sh('python setup.py --command-packages=stdeb.command sdist_dsc --force-buildsystem=False')
    dist_package = path('deb_dist').dirs('buildnotify-*')[0]
    sh('rm %s' % path('../BuildNotifyTest').files('*.tar.gz')[0])
    sh('rm %s' % path('../BuildNotifyTest').files('*.dsc')[0])
    sh('cp %s/debian/changelog ../BuildNotifyTest/debian.changelog' % dist_package)
    sh('cp %s/debian/control ../BuildNotifyTest/debian.control' % dist_package)
    sh('cp %s/debian/rules ../BuildNotifyTest/debian.rules' % dist_package)
    sh('cp %s ../BuildNotifyTest/' % path('dist').files('BuildNotify-*')[0])
    sh('cp %s ../BuildNotifyTest/' % path('deb_dist').files('buildnotify*.dsc')[0])
    sh('osc addremove ../BuildNotifyTest/')
    sh('osc commit ../BuildNotifyTest/ -m"Updated package"')
