import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def configure(cnf=None, deactivate=False):
    if deactivate:
        I3.configure(None)
        I3bar.configure(None)
        Notify.configure(None)
        log.info("ipc deactivated")
    else:
        I3.configure(cnf.payload["main"]["i3_refresh_msg"])
        log.info(f'set i3 refresh method to {I3.refresh.__name__}', )
        I3bar.configure(cnf.payload["main"]["status_command"])
        log.info(f'set i3bar refresh method to {I3bar.refresh.__name__}', )
        Notify.configure(cnf.payload["main"]["notify"])
        log.info(f'set notify method to {Notify.send.__name__}', )


def communicate(msg='new config active', refresh=False, urgency='low'):
    if refresh:
        I3.refresh()
        I3bar.refresh()
    Notify.send(msg, urgency=urgency)


class I3:
    @classmethod
    def configure(cls, which):
        cls.refresh = {
            'restart': cls.restart_i3,
            'reload': cls.reload_i3,
        }.get(which, nop)

    @classmethod
    def reload_i3(cls):
        cls._send_i3_msg('reload')

    @classmethod
    def restart_i3(cls):
        subprocess.call(['i3-msg', 'restart'])

    refresh = restart_i3

    @classmethod
    def _send_i3_msg(cls, msg):
        try:
            output = subprocess.check_output(['i3-msg', msg]).decode()
            if '"success":true' in output:
                return True
            return False
        except subprocess.CalledProcessError as e:
            if msg == 'restart' and e.returncode == 1:
                log.debug("[IGNORE] exit 1 is ok for restart")
                return True

    @classmethod
    def get_config_error_report(cls, path):
        cmd = ['i3', '-C', '-c', str(path)]
        try:
            return subprocess.check_output(cmd).decode()
        except subprocess.CalledProcessError as e:
            return e.output.decode()
        except FileNotFoundError as e:
            assert Path(path).exists(), path
            assert "No such file or directory: 'i3'" in e.strerror
            log.warning("[IGNORE] crashed - no i3 -> assuming test system")
            return ''


class Notify:
    @classmethod
    def configure(cls, notify):
        cls.send = cls.notify_send if notify else nop

    @classmethod
    def notify_send(cls, msg, urgency='low'):
        """urgency levels: low, normal, critical"""
        subprocess.check_call([
            'notify-send', '-a', 'i3configger', '-t', '1', '-u', urgency, msg])

    send = notify_send


class I3bar:
    command = 'i3status'

    @classmethod
    def configure(cls, command):
        cls.command = command
        cls.refresh = cls.refresh if command else nop

    @classmethod
    def send_sigusr1(cls):
        try:
            subprocess.check_output(['killall', '-SIGUSR1', cls.command])
        except subprocess.CalledProcessError as e:
            log.debug("[IGNORE] failed status refresh: %s", e)

    refresh = send_sigusr1


# noinspection PyUnusedLocal
def nop(*args, **kwargs):
    pass
