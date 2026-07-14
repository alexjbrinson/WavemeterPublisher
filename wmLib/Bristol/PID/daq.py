#!/usr/bin/env python3

#import numpy as np
from mcculw import ul
from mcculw.enums import ULRange 
from mcculw.ul import ULError 
from wmLib.Bristol.PID.advanced_pid_engine import AdvancedPidEngine

class DAQ:
    """
    A class to manage data acquisition and control using an advanced PID engine.

    Attributes
    ----------
    gain : float
        The gain for the PID engine.
    offset : float
        The offset for the PID engine.
    low_voltage : float
        The minimum output voltage.
    high_voltage : float
        The maximum output voltage.
    engine : AdvancedPidEngine
        An instance of the AdvancedPidEngine class for PID control.

    Methods
    -------
    setKp(kp_value, index)
        Sets the proportional gain for a specific channel.
    setKi(ki_value, index)
        Sets the integral gain for a specific channel.
    setKd(kd_value, index)
        Sets the derivative gain for a specific channel.
    setSetPoint(sp_value, index)
        Sets the set point for a specific channel.
    setGain(gain, index)
        Sets the gain for the PID engine for a specific channel.
    setOffset(offset, index)
        Sets the offset for the PID engine for a specific channel.
    setLowVoltage(low_voltage, ch_num)
        Sets the minimum output voltage for a specific channel.
    setHighVoltage(high_voltage, ch_num)
        Sets the maximum output voltage for a specific channel.
    convert_wavelength_to_voltage(wavelength, ch_num )
        Converts a wavelength value to a voltage.
    clamp(value, ch_num)
        Clamps a value to the range defined by low_voltage and high_voltage.
    update_pid_engine_wavelength_limits(ch_num)
        Updates the PID engine with the wavelength limits for a specific channel.
    convert_voltage_to_wavelength(voltage, ch_num)
        Converts a voltage value to a wavelength.
    computePID(active_channel_and_board, wavelength)
        Computes the PID output for a specific channel and wavelength.
    set_voltage(voltage, channel_number, board_number)
        Sets the output voltage for a specific channel and board.
    """

    def __init__(self):
        """
        Initializes the DAQ class with default values.
        """
        self.gain = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] 
        self.low_voltage = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] 
        self.high_voltage = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        self.engine = AdvancedPidEngine()

    def setKp(self, kp_value, index):
        """
        Sets the proportional gain for a specific channel.

        Parameters
        ----------
        kp_value : float
            The proportional gain.
        index : int
            The channel index.
        """
        self.engine.set_kp(kp_value, index)

    def setKi(self, ki_value, index):
        """
        Sets the integral gain for a specific channel.

        Parameters
        ----------
        ki_value : float
            The integral gain.
        index : int
            The channel index.
        """
        self.engine.set_ki(ki_value, index)

    def setKd(self, kd_value, index):
        """
        Sets the derivative gain for a specific channel.

        Parameters
        ----------
        kd_value : float
            The derivative gain.
        index : int
            The channel index.
        """
        self.engine.set_kd(kd_value, index)

    def setSetPoint(self, sp_value, index):
        """
        Sets the set point for a specific channel.

        Parameters
        ----------
        sp_value : float
            The set point value.
        index : int
            The channel index.
        """
        self.engine.set_set_point(sp_value, index)

    def setGain(self, gain, index):
        """
        Sets the gain for the PID engine.

        Parameters
        ----------
        gain : float
            The gain value.
        index : int
            The channel index
        """
        self.gain[index] = gain

    def setOffset(self, offset, index):
        """
        Sets the offset for the PID engine.

        Parameters
        ----------
        offset : float
            The offset value.
        index : int
            The channel index
        """
        self.offset[index] = offset

    def setLowVoltage(self, low_voltage, ch_num):
        """
        Sets the minimum output voltage for a specific channel.

        Parameters
        ----------
        low_voltage : float
            The minimum output voltage.
        ch_num : int
            The channel number.
        """
        self.low_voltage[ch_num] = low_voltage
        self.engine.set_minimum_output(low_voltage, ch_num)

    def setHighVoltage(self, high_voltage, ch_num):
        """
        Sets the maximum output voltage for a specific channel.

        Parameters
        ----------
        high_voltage : float
            The maximum output voltage.
        ch_num : int
            The channel number.
        """
        self.high_voltage[ch_num] = high_voltage
        self.engine.set_maximum_output(high_voltage, ch_num)

    def convert_wavelength_to_voltage(self, wavelength, ch_num):
        """
        Converts a wavelength value to a voltage.

        Parameters
        ----------
        wavelength : float
            The wavelength value.
        ch_num : int
            Channel number.
        Returns
        -------
        float
            The converted voltage.
        """
        return self.gain[ch_num] * wavelength + self.offset[ch_num]

    def clamp(self, value, ch_num):
        """
        Clamps a value to the range defined by low_voltage and high_voltage.

        Parameters
        ----------
        value : float
            The value to be clamped.
        ch_num : int
            The current channel.
        Returns
        -------
        float
            The clamped value.
        """
        if value < self.low_voltage[ch_num]:
            return self.low_voltage[ch_num]
        elif value > self.high_voltage[ch_num]:
            return self.high_voltage[ch_num]
        return value

    def update_pid_engine_wavelength_limits(self, ch_num):
        """
        Updates the PID engine with the wavelength limits for a specific channel.

        Parameters
        ----------
        ch_num : int
            The channel number.
        """
        converted_low_voltage = self.convert_voltage_to_wavelength(self.low_voltage[ch_num], ch_num)
        converted_high_voltage = self.convert_voltage_to_wavelength(self.high_voltage[ch_num], ch_num)
        self.engine.set_minimum_output(min(converted_low_voltage, converted_high_voltage), ch_num)
        self.engine.set_maximum_output(max(converted_low_voltage, converted_high_voltage), ch_num)

    def convert_voltage_to_wavelength(self, voltage, ch_num):
        """
        Converts a voltage value to a wavelength.

        Parameters
        ----------
        voltage : float
            The voltage value.
        ch_num : int
            The current channel.
        Returns
        -------
        float
            The converted wavelength.
        """
        return (voltage - self.offset[ch_num]) / self.gain[ch_num]

    def computePID(self, active_channel_and_board, wavelength):
        """
        Computes the PID output for a specific channel and wavelength.

        Parameters
        ----------
        active_channel_and_board : tuple
            A tuple containing measurement component board channel, board number, and channel array number.
        wavelength : float
            The wavelength value.

        Returns
        -------
        tuple
            The error and the clamped voltage output.
        """
        meas_comp_board_ch, meas_comp_board_num, ch_array_num = active_channel_and_board
        self.engine.input(wavelength, ch_array_num)
        self.engine.iterate(ch_array_num)
        output = self.engine.get_output(ch_array_num)

        error = self.engine.error(ch_array_num)
        voltage = self.clamp(self.convert_wavelength_to_voltage(output, ch_array_num), ch_array_num)
        # self.set_voltage(voltage, meas_comp_board_ch, meas_comp_board_num)

        return error, output, voltage

    def set_voltage(self, voltage, channel_number, board_number):
        """
        Sets the output voltage for a specific channel and board.

        Parameters
        ----------
        voltage : float
            The voltage value.
        channel_number : int
            The channel number.
        board_number : int
            The board number.

        Returns
        -------
        bool
            True if the operation is successful, False otherwise.
        """
        try:
            output_value = ul.from_eng_units(board_number, ULRange.BIP10VOLTS, voltage)
            print(f"Board num: {board_number}, Channel num: {channel_number}, Output volt: {output_value}")
            ul.a_out(board_number, channel_number, ULRange.BIP10VOLTS, output_value)
            return True
        except ULError as e:
            print(f"Error: {e}")
            return False
