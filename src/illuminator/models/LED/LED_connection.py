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

    parameters={'min_speed': 0,  # minimum speed for the connection
                'max_speed': 0.5,  # maximum speed for the connection
                'direction': 0,  # direction of the connection (towards the unit)
                }
    inputs={'speed': 0}  # speed for the connection
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
        self.min_speed = self.parameters.get('min_speed')
        self.max_speed = self.parameters.get('max_speed')
        self.direction = self.parameters.get('direction')
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

        speed = input_data.get('speed', 0)
        direction = self.direction
        print("got speed: ", speed)

        if speed < 0:
            direction = 1 - direction
            speed *=-1

        if speed <= self.min_speed:
            speed = 0
        elif speed >= self.max_speed:
            speed = 100
        else:
            speed = ((speed - self.min_speed) / (self.max_speed - self.min_speed)) * 100

        self.send_led_animation(speed, direction)
        # self.set_outputs(results)

        return time + self._model.time_step_size
    

    def send_led_animation(self, speed, direction) -> None:
        device = '/dev/ttyACM0'
        ser = serial.Serial(device, timeout=5)
        line = ''

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(line)
        
        if speed == 0:
            colour = 'g'
            delay = 0
        else:
            delay = max(0, min(3, int(3 * speed/100)))  # Maps 0-100% to 0-3, with bounds checking
            delay = round(delay)

            if delay >= 3:
                colour = 'r'
            else:
                colour = 'g'

        print(f"speed: {speed}%, Sending {delay}{colour}1")
        ser.write(f"{delay}{colour}{direction}\n".encode('utf-8'))
        time.sleep(3)

        return


if __name__ == '__main__':
    #send_led_animation()
    mosaik_api.start_simulation(LED_connection(), 'LED connection Simulator')
