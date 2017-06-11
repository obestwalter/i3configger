import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def configure(args):
    I3.set_msg_type(args.i3_refresh_msg)
    log.info(f'set i3 refresh method to {I3.refresh.__name__}', )
    Notify.set_notify_command(args.notify)
    log.info(f'set notify method to {Notify.send.__name__}', )


def communicate(msg='new config active', refresh=False):
    if refresh:
        I3.refresh()
        StatusBar.refresh()
    Notify.send(msg)


class I3:
    @classmethod
    def set_msg_type(cls, which):
        cls.refresh = {
            'restart': cls.restart_i3,
            'reload': cls.reload_i3,
        }.get(which, cls.nop)

    @classmethod
    def reload_i3(cls):
        cls._send_i3_msg('reload')

    @classmethod
    def restart_i3(cls):
        subprocess.call(['i3-msg', 'restart'])

    @classmethod
    def nop(cls):
        pass

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
            return e.output
        except FileNotFoundError as e:
            assert Path(path).exists(), path
            assert "No such file or directory: 'i3'" in e.strerror
            log.warning("[IGNORE] crashed - no i3 -> assuming test system")
            return ''


class Notify:
    @classmethod
    def set_notify_command(cls, notify):
        cls.send = cls.notify_send if notify else cls.nop

    @classmethod
    def notify_send(cls, msg, urgency='low'):
        subprocess.check_call([
            'notify-send', '-a', 'i3configger', '-t', '1', '-u', urgency, msg])

    @staticmethod
    def nop(*args, **kwargs):
        pass

    send = notify_send


class StatusBar:
    @classmethod
    def refresh(cls):
        try:
            subprocess.check_output(['killall', '-SIGUSR1', 'i3status'])
        except subprocess.CalledProcessError as e:
            log.debug("[IGNORE] failed status refresh: %s", e)
