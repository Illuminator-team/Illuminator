from illuminator.builder import IlluminatorModel, ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
import time



class LED_connection(ModelConstructor):
    """
    Calculates total load demand based on number of houses and input load.

    Parameters
    ----------
    load : float
        Input load per house in kW or kWh depending on output_type
        
    Returns
    -------
    re_params : dict
        Dictionary containing calculated load demand values
    """

    parameters={
                }
    inputs={}
    outputs={
             }
    states={
            }
    time_step_size=1
    time=None


    def init(self, *args, **kwargs) -> None:
        """
        Initialize Load model with given parameters.

        Parameters
        ----------
        kwargs : dict
            Dictionary containing model parameters and initial states
            
        Returns
        -------
        None
        """
        result = super().init(*args, **kwargs)
        self.state = 0
        return result


    def step(self, time: int, inputs: dict=None, max_advance: int=900) -> None:
        """
        Performs a single simulation time step by calculating load demand.

        Parameters
        ----------
        time : float
            Current simulation time in seconds
        inputs : dict
            Dictionary containing input values including 'load'
        max_advance : int, optional
            Maximum time step advancement, defaults to 1
            
        Returns
        -------
        float
            Next simulation time step
        """
        input_data = self.unpack_inputs(inputs)
        self.time = time

        self.send_led_animation()
        # self.set_outputs(results)

        return time + self._model.time_step_size
    

    def send_led_animation(self):
        device = '/dev/ttyACM0'
        ser = serial.Serial(device, timeout=5)
        line = ''

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(line)
        
        colour = 'r'
        if self.state == 0:
            colour = 'r'
            self.state = 1
        elif self.state == 1:
            colour = 'g'
            self.state = 2
        elif self.state == 2:
            colour = 'b'
            self.state = 0

        ser.write(f"2{colour}1\n".encode('utf-8'))
        time.sleep(1)

        return


if __name__ == '__main__':
    #send_led_animation()
    mosaik_api.start_simulation(LED_connection(), 'LED connection Simulator')
