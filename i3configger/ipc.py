import subprocess

from i3configger.base import log


# todo use Adaephons i3 library
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
        cmd = ['i3-msg', msg]
        try:
            output = subprocess.check_output(cmd).decode()
            if '"success":true' in output:
                return True
            return False
        except subprocess.CalledProcessError as e:
            if msg == 'restart' and e.returncode == 1:
                log.debug("[IGNORE] exit 1 is ok for restart")
                return True

    @classmethod
    def config_is_ok(cls, path):
        cmd = ['i3', '-C', str(path)]
        try:
            subprocess.check_output(cmd)
            return True
        except subprocess.CalledProcessError as e:
            Notify.send(f"error in {path}:\n{e.output}")
            return False


class Notify:
    @classmethod
    def set_notify_command(cls, offSwitch):
        if offSwitch:
            log.info("deactivate notification")
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
            subprocess.check_call(['killall', '-SIGUSR1', 'i3status'])
        except subprocess.CalledProcessError as e:
            # TODO make this work for other status bars
            log.debug("ignored failed status refresh: %s", e)
