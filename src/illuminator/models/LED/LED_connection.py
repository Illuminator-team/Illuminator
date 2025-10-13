from illuminator.builder import ModelConstructor
import mosaik_api_v3 as mosaik_api
import serial
import time
import os
from numpy import ceil


class LED_connection(ModelConstructor):
    """
    Multi-interface LED driver (ID-centric).

    Parameters (YAML)
    -----------------
    min_speed : float
    max_speed : float
    direction : int  (0 or 1) base/default direction

    Inputs (YAML wiring)
    --------------------
    speed : dict
        {
          "sources": [ "<modelA>", "<modelB>", ... ],
          "value":   [ <floatA>,    <floatB>,   ... ]
        }
        Each value[i] came from sources[i].

    mapping : list[dict]
        StoryMode controller mapping items, each:
        {
          "from": "<source model name>",
          "to":   "<destination model name>",
          "id":   "<led_id or int-like>",
          "direction": 0|1   # optional per-connection override
        }

    States
    ------
    connections : list[str]
        List of LED IDs currently considered "connected" (observed from USB),
        based on 3-sample miss logic per *device path*.
    """

    # EXACT same parameters as before
    parameters = {
        'min_speed': 0.0,
        'max_speed': 0.5,
        'direction': 0,
    }

    # Inputs as per updated controller wiring
    inputs = {
        'speed': {},       # dict: {'sources': [...], 'value': [...]}
        'mapping': [],     # list of dicts (from, to, id, direction)
    }

    outputs = {}
    states = {'connections': []}

    time_step_size = 1
    time = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        p = self.parameters
        self.min_speed = float(p.get('min_speed', 0.0))
        self.max_speed = float(p.get('max_speed', 0.5))
        try:
            self.base_direction_param = int(p.get('direction', 0)) & 1
        except Exception:
            self.base_direction_param = 0

        # Per-device health memory (device path -> last observed ID history)
        # {
        #   "/dev/ttyACM0": { "history": ["id" or "-1", ... up to 3], "current_id": str }
        # }
        self._dev_state = {}

        # Reverse index: LED id -> last known device path
        self._id_to_device = {}

    # ---------- helpers ----------

    def normalize_speed_and_direction(self, raw_speed: float, base_direction: int):
        """Map raw speed to 0..100%, flipping direction if speed < 0."""
        direction = base_direction
        try:
            speed = float(raw_speed)
        except Exception:
            speed = 0.0

        if speed < 0:
            direction = 1 - direction
            speed = -speed

        if speed <= self.min_speed:
            pct = 0.0
        else:
            denom = max(1e-9, (self.max_speed - self.min_speed))
            pct = ((speed - self.min_speed) / denom) * 100.0
            if pct < 0:
                direction = 1 - direction
                pct = -pct

        if pct < 0:
            pct = 0.0
        return pct, direction

    def decide_colour_and_delay(self, percent_speed: float):
        """
        Convert 0–100% to (delay, colour):
          delay in [0..4] via ceil(4 * pct/100)
          colour 'r' when delay >= 4 else 'g'
        """
        if percent_speed <= 0:
            return 0, 'g'
        delay = int(round(max(0, min(4, ceil(4 * (percent_speed / 100.0))))))
        colour = 'r' if delay >= 4 else 'g'
        return delay, colour

    def _update_device_history(self, device: str, observed_id: str):
        """3-strike disconnect logic per device path; update reverse index id->device."""
        key = str(device)
        state = self._dev_state.setdefault(key, {"history": [], "current_id": "-1"})
        hist = state["history"]
        hist.append(observed_id if observed_id else "-1")
        if len(hist) > 3:
            hist.pop(0)

        if len(hist) >= 3 and hist[-1] == "-1" and hist[-2] == "-1" and hist[-3] == "-1":
            # disconnected
            state["current_id"] = "-1"
        else:
            if hist[-1] != "-1":
                state["current_id"] = hist[-1]

        self._dev_state[key] = state

        # maintain reverse mapping when we have a valid id
        if state["current_id"] and state["current_id"] != "-1":
            self._id_to_device[state["current_id"]] = key
        else:
            # if device has no valid id, drop any id that pointed here
            for lid, path in list(self._id_to_device.items()):
                if path == key:
                    self._id_to_device.pop(lid, None)

    def _device_for_index(self, idx: int) -> str:
        """Map 0..3 to /dev/ttyACM{idx}."""
        return f"/dev/ttyACM{idx}"

    def _present_devices(self, max_idx: int = 3):
        """List candidate device paths that exist (soft filter)."""
        devs = []
        for i in range(max_idx + 1):
            path = self._device_for_index(i)
            # don't require existence; some OSes don't list it until open
            if os.path.exists(path):
                devs.append(path)
            else:
                # include anyway to try open (keeps behavior similar to before)
                devs.append(path)
        return devs

    def send_led_animation(self, device: str, percent_speed: float, direction: int) -> str:
        """
        Send to a single USB LED controller, return observed ID or "-1".
        Protocol: write f"{delay}{colour}{direction}\n", read last byte(s) as ID.
        """
        observed_id = "-1"

        try:
            ser = serial.Serial(device, timeout=5.0)
        except Exception as e:
            print(f"[{device}] open failed: {e}")
            return "-1"

        # Drain any pending bytes first
        try:
            if getattr(ser, 'in_waiting', 0) > 0:
                drain = ser.read(ser.in_waiting)
                if drain:
                    try:
                        observed_id = drain[-1:].decode('utf-8').strip() or "-1"
                        print(f"[{device}] pre-read ID: {observed_id}")
                    except Exception:
                        observed_id = "-1"
        except Exception as e:
            print(f"[{device}] pre-read error: {e}")

        delay, colour = self.decide_colour_and_delay(percent_speed)
        payload = f"{delay}{colour}{(int(direction) & 1)}\n"
        try:
            print(f"[{device}] send '{payload.strip()}' (pct={percent_speed:.1f} dir={direction})")
            ser.write(payload.encode('utf-8'))
        except Exception as e:
            print(f"[{device}] write failed: {e}")
            try:
                ser.close()
            except Exception:
                pass
            return "-1"

        time.sleep(0.5)

        try:
            if getattr(ser, 'in_waiting', 0) > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    observed_id = data[-1:].decode('utf-8').strip() or "-1"
                    print(f"[{device}] post-read ID: {observed_id}")
        except Exception as e:
            print(f"[{device}] read failed: {e}")
            observed_id = "-1"
        finally:
            try:
                ser.close()
            except Exception:
                pass

        time.sleep(0.1)
        return observed_id

    # ---------- input parsing helpers ----------

    def _speeds_by_source(self, speed_input) -> dict:
        """
        Convert speed dict {'sources': [...], 'value': [...]} to {source: speed}.
        If shape is unexpected, be forgiving.
        """
        result = {}
        if isinstance(speed_input, dict):
            sources = speed_input.get('sources', [])
            values = speed_input.get('value', [])
            try:
                n = min(len(sources), len(values))
                for i in range(n):
                    src = str(sources[i]).split('-0.')[0]  # base model name
                    print(f"base source model name: {src}")
                    try:
                        val = float(values[i])
                    except Exception:
                        val = 0.0
                    result[src] = val
            except Exception:
                pass
        else:
            # single scalar applies to an anonymous source
            try:
                result['__default__'] = float(speed_input)
            except Exception:
                result['__default__'] = 0.0
        return result

    def _desired_animation_by_id(self, mapping_list, speeds_by_source: dict) -> dict:
        """
        Build desired animation per LED id using mapping + per-source speeds.

        Returns: { "<id>": (percent_speed, direction) }
        """
        print ("Mapping List", mapping_list)
        desired = {}
        for item in mapping_list:
            print ( "The Item is", item, "and it is type", type(item))
            if not isinstance(item, dict):
                continue

            from_model = str(item.get('from', '')).strip().split('_LED')[0]
            to_model = str(item.get('to', '')).strip().split('_LED')[0]

            led_id = str(item.get('connection_id', '')).strip()
            if not led_id:
                continue

            print(f"Now checking item {item}, is it dict? {isinstance(item, dict)}, from model is {from_model}, to model is {to_model}, led_id is {led_id}")

            # per-item direction override or base
            try:
                item_dir = int(item.get('direction', self.base_direction_param)) & 1
            except Exception:
                item_dir = self.base_direction_param

            # get speed from the specific source model (fall back if missing)
            # raw_speed = speeds_by_source.get(src_model, speeds_by_source.get('__default__', 0.0))
            raw_speed = speeds_by_source.get(from_model, None)
            if raw_speed is None:
                raw_speed = speeds_by_source.get(to_model, speeds_by_source.get('__default__', 0.0))
                item_dir = 1 - item_dir  # reverse direction if using "to" model speed

            pct, eff_dir = self.normalize_speed_and_direction(raw_speed, item_dir)

            desired[led_id] = (pct, eff_dir)
        return desired

    # ---------- simulation step ----------

    def step(self, time: int, inputs: dict = None, max_advance: int = 900) -> int:
        inp = self.unpack_inputs(inputs, return_sources=True)
        self.time = time

        print ("Here are the unpacked inputs:", inputs)

        speed_input = inp.get('speed', {})
        mapping_list = inp.get('mapping', [])['value'] or []

        print("Speed input:", speed_input)

        speeds_by_source = self._speeds_by_source(speed_input)
        desired_by_id = self._desired_animation_by_id(mapping_list, speeds_by_source)

        print(f"[LED] t={time} speeds_by_source={speeds_by_source} desired_by_id={desired_by_id}")

        # Iterate physical devices (ACM0..3). For each device, find its current LED id
        # (from last observation) and send that id's desired animation. If unknown or not
        # mapped, send a small probe to learn the id.
        for idx in range(4):
            device = self._device_for_index(idx)
            state = self._dev_state.get(device, {})
            current_id = state.get("current_id", "-1")

            if current_id and current_id != "-1" and current_id in desired_by_id:
                pct, dirn = desired_by_id[current_id]
                print(f"[LED] device {device} has known id {current_id}, using desired pct={pct:.1f} dir={dirn}")
            else:
                # Unknown/not-mapped id: send a light probe (0%) to elicit ID with white default state
                print(f"[LED] device {device} has unknown or unmapped id '{current_id}', sending probe")
                pct, dirn = (0.0, self.base_direction_param)

            observed = self.send_led_animation(device, pct, dirn)

            # Update health + reverse index
            self._update_device_history(device, observed)

        # Report list of currently connected LED IDs
        reported = []
        for dev, state in self._dev_state.items():
            curr = state.get("current_id", "-1")
            if curr and curr != "-1":
                reported.append(curr)

        print(f"[LED] report connections: {reported}")
        self.set_states({'connections': reported})
        return time + self._model.time_step_size


if __name__ == '__main__':
    mosaik_api.start_simulation(LED_connection(), 'LED connection Simulator')
