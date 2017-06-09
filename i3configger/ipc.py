import subprocess

from i3configger.base import log


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
    def get_config_errors(cls, path):
        try:
            subprocess.check_output(['i3', '-C', '-c', str(path)])
            return None
        except subprocess.CalledProcessError as e:
            return e.output


class Notify:
    @classmethod
    def set_notify_command(cls, notify):
        if not notify:
            log.debug("do not send notifications")
            cls.send = cls.nop

    @classmethod
    def send(cls, msg, urgency='low'):
        subprocess.check_call([
            'notify-send', '-a', 'i3configger', '-t', '1', '-u', urgency, msg])

    @staticmethod
    def nop(*args, **kwargs):
        pass


class StatusBar:
    @classmethod
    def refresh(cls):
        try:
            subprocess.check_output(['killall', '-SIGUSR1', 'i3status'])
        except subprocess.CalledProcessError as e:
            log.debug("[IGNORE] failed status refresh: %s", e)
