from charms.reactive import when, when_not, set_flag, set_state, when_file_changed
from charmhelpers.core.host import service, service_running, service_available
from charmhelpers.core.hookenv import open_port, config
from charmhelpers.core.hookenv import application_name
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.templating import render

from subprocess import check_call
import os

def dbname():
    return f'hello-juju_{application_name()}'

def port():
    return int(config('port'))

@when('codebase.available')
@when_not('omnivector_challenge.installed')
def install_omnivector_challenge():
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #

    # further links
    # - https://ubuntu.com/blog/charming-discourse-with-the-reactive-framework

    app = application_name()
    venv_root = f"/srv/omnivector-challenge/venv"
    status_set("maintenance", "Creating Python virtualenv")
    check_call(['/usr/bin/python3', '-m', 'venv', venv_root])
    status_set("maintenance", "Installing Python requirements")
    check_call([f'{venv_root}/bin/pip', 'install', 'gunicorn'])
    check_call([f'{venv_root}/bin/pip', 'install', '-r', '/srv/omnivector-challenge/current/requirements.txt'])
    set_state('omnivector_challenge.installed')


@when('omnivector_challenge.installed')
@when_not('omnivector_challenge.gunicorn_configured')
def configure_gunicorn():
    status_set("maintenance", "Configuring gunicorn service")
    render(
        'omnivector-challenge.service.j2',
        '/etc/systemd/system/omnivector-challenge.service',
        perms=0o755,
        context={
            'port': port(),
            'project_root': '/srv/omnivector-challenge/current',
            'user': 'www-data',
            'group': 'www-data',
        }
    )
    service("enable", "omnivector-challenge")
    status_set("active", "Serving HTTP from gunicorn")

@when_file_changed('/srv/omnivector-challenge/current/settings.py', '/etc/systemd/system/omnivector-challenge.service')
def restart():
    open_port(port())
    if service_running('omnivector-challenge'):
        service('restart', 'omnivector-challenge')
    else:
        service('start', 'omnivector-challenge')
    status_set("active", "")

@when('config.changed.port')
def port_updated():
    configure_gunicorn()
    restart()
