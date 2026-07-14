from ctypes import CDLL, c_void_p, c_double, c_int
import os

class AdvancedPidEngine:
    """
    A class to interface with the Advanced PID Engine DLL.

    Attributes
    ----------
    _pid_dll : CDLL
        The CDLL object representing the loaded PID DLL.
    obj : c_void_p
        The handle for the created PID engine instance.

    Methods
    -------
    set_kp(kp, ch_num)
        Sets the proportional gain for a specific channel.
    set_ki(ki, ch_num)
        Sets the integral gain for a specific channel.
    set_kd(kd, ch_num)
        Sets the derivative gain for a specific channel.
    set_set_point(set_point, ch_num)
        Sets the set point for a specific channel.
    set_minimum_output(minimum, ch_num)
        Sets the minimum output for a specific channel.
    set_maximum_output(maximum, ch_num)
        Sets the maximum output for a specific channel.
    input(input_value, ch_num)
        Inputs a value to the PID engine for a specific channel.
    iterate(ch_num)
        Iterates the PID engine for a specific channel.
    get_output(ch_num)
        Gets the output from the PID engine for a specific channel.
    error(ch_num)
        Gets the error value from the PID engine for a specific channel.
    reset()
        Resets the PID engine.
    """

    def __init__(self):
        """
        Initializes the AdvancedPidEngine class and loads the DLL.
        """
        script_dir = os.path.dirname(os.path.realpath(__file__))
        dll_path = os.path.join(script_dir, "pidDll.dll")
        self._pid_dll = CDLL(dll_path)
        self._pid_dll.AdvancedPidEngine_new.restype = c_void_p
        self._pid_dll.AdvancedPidEngine_delete.argtypes = [c_void_p]
        self._pid_dll.AdvancedPidEngine_set_kp.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_set_ki.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_set_kd.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_set_set_point.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_set_minimum_output.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_set_maximum_output.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_input.argtypes = [c_void_p, c_double, c_int]
        self._pid_dll.AdvancedPidEngine_iterate.argtypes = [c_void_p, c_int]
        self._pid_dll.AdvancedPidEngine_get_output.argtypes = [c_void_p, c_int]
        self._pid_dll.AdvancedPidEngine_get_output.restype = c_double
        self._pid_dll.AdvancedPidEngine_error.argtypes = [c_void_p, c_int]
        self._pid_dll.AdvancedPidEngine_error.restype = c_double
        self._pid_dll.AdvancedPidEngine_reset.argtypes = [c_void_p]

        self.obj = self._pid_dll.AdvancedPidEngine_new()
        if not self.obj:
            raise Exception("Failed to create AdvancedPidEngine instance")

    def __del__(self):
        """
        Destroys the PID engine instance when the object is deleted.
        """
        if self.obj:
            self._pid_dll.AdvancedPidEngine_delete(self.obj)

    def set_kp(self, kp, ch_num):
        """
        Sets the proportional gain for a specific channel.

        Parameters
        ----------
        kp : float
            The proportional gain.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_kp(self.obj, c_double(kp), c_int(ch_num))

    def set_ki(self, ki, ch_num):
        """
        Sets the integral gain for a specific channel.

        Parameters
        ----------
        ki : float
            The integral gain.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_ki(self.obj, c_double(ki), c_int(ch_num))

    def set_kd(self, kd, ch_num):
        """
        Sets the derivative gain for a specific channel.

        Parameters
        ----------
        kd : float
            The derivative gain.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_kd(self.obj, c_double(kd), c_int(ch_num))

    def set_set_point(self, set_point, ch_num):
        """
        Sets the set point for a specific channel.

        Parameters
        ----------
        set_point : float
            The set point.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_set_point(self.obj, c_double(set_point), c_int(ch_num))

    def set_minimum_output(self, minimum, ch_num):
        """
        Sets the minimum output for a specific channel.

        Parameters
        ----------
        minimum : float
            The minimum output.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_minimum_output(self.obj, c_double(minimum), c_int(ch_num))

    def set_maximum_output(self, maximum, ch_num):
        """
        Sets the maximum output for a specific channel.

        Parameters
        ----------
        maximum : float
            The maximum output.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_set_maximum_output(self.obj, c_double(maximum), c_int(ch_num))

    def input(self, input_value, ch_num):
        """
        Inputs a value to the PID engine for a specific channel.

        Parameters
        ----------
        input_value : float
            The input value.
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_input(self.obj, c_double(input_value), c_int(ch_num))

    def iterate(self, ch_num):
        """
        Iterates the PID engine for a specific channel.

        Parameters
        ----------
        ch_num : int
            The channel number.
        """
        self._pid_dll.AdvancedPidEngine_iterate(self.obj, c_int(ch_num))

    def get_output(self, ch_num):
        """
        Gets the output from the PID engine for a specific channel.

        Parameters
        ----------
        ch_num : int
            The channel number.

        Returns
        -------
        float
            The output value.
        """
        return self._pid_dll.AdvancedPidEngine_get_output(self.obj, c_int(ch_num))

    def error(self, ch_num):
        """
        Gets the error value from the PID engine for a specific channel.

        Parameters
        ----------
        ch_num : int
            The channel number.

        Returns
        -------
        float
            The error value.
        """
        return self._pid_dll.AdvancedPidEngine_error(self.obj, c_int(ch_num))

    def reset(self):
        """
        Resets the PID engine.
        """
        self._pid_dll.AdvancedPidEngine_reset(self.obj)
