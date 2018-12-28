from i3configger.message import Messenger


def test_shadow(tmp_path):
    messenger = Messenger(tmp_path / "dontcare",  [], message=["shadow", "k", "v"])
    messenger.digest_message()