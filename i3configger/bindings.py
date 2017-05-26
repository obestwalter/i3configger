# TODO
class I3Binder:
    """Read key bindings and render nice info file to look up the bindings"""

    def fetch_bindings(self):
        """read in all bindcode and bindsym assignments"""

    def translate_bindings(self):
        """translate bindsym to bindsym assignments
    
        this need to be done the moment the information is asked because it
        depends on the currently acitve layout.
        """
    def write_bindings_info(self):
        pass
