"""
Module 1 Assignment — Task 1.1
MQTT Sensor Publisher

Complete all TODO sections. Do not modify the function signatures
or the SensorReading dataclass — the tests depend on them.
"""

import json
import logging
import random
from socket import timeout
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER_HOST = "localhost"
BROKER_PORT = 1883
CLIENT_ID   = "smartfactory-publisher-001"

LINES   = ["line1", "line2"]
SENSORS = {
    "temperature": {"unit": "C",    "base": 70.0, "noise": 3.0,  "qos": 1},
    "vibration":   {"unit": "mm/s", "base": 1.2,  "noise": 0.3,  "qos": 0},
    "power":       {"unit": "kW",   "base": 45.0, "noise": 5.0,  "qos": 2},
}

CRITICAL_TEMP_THRESHOLD = 85.0


@dataclass
class SensorReading:
    line:      str
    sensor:    str
    value:     float
    unit:      str
    timestamp: str
    seq:       int


class SmartFactoryPublisher:
    """Publishes simulated sensor data for the SmartFactory assignment."""

    def __init__(self, broker_host: str = BROKER_HOST, broker_port: int = BROKER_PORT):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self._seq: dict[str, int] = {}          # per-topic sequence counter
        self._client: Optional[mqtt.Client] = None

    # ── Connection ─────────────────────────────────────────────────────────────

    def _build_client(self) -> mqtt.Client:
        """
        TODO 1: Create and configure the MQTT client.
        Requirements:
          - Use CLIENT_ID as the client identifier
          - Set clean_session=False for a persistent session
          - Register on_connect, on_publish callbacks (defined below)
          - Configure the Last Will and Testament for EACH line:
              topic   = f"factory/{line}/status"
              payload = "offline"
              qos     = 1
              retain  = True
            (Note: paho only supports a single LWT per client — set it for line1;
             the tests only verify line1 LWT)
        """
        # TODO: implement this method

        client = mqtt.Client(
            client_id= CLIENT_ID,
            clean_session=False
            )
        
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish

        # LWT only for line1 
        client.will_set(
            topic ="factory/line1/status",
            payload="offline",
            qos=1,
            retain=True
            )

        self._client = client

        return client

        

    def connect(self) -> None:
        """
        TODO 2: Connect to the broker and publish the initial 'online' retained
        status message for each line.
          - Start the network loop (loop_start)
          - Wait up to 5 seconds for the connection to establish
          - For each line, publish retained 'online' to factory/{line}/status (QoS 1)
        """
        # TODO: implement this method
        self._build_client()

        assert self._client is not None

        self._client.connect(self.broker_host, self.broker_port, keepalive=60)
        self._client.loop_start()

        # Wait for connection (5 seconds)
        timeout = time.time() + 5
        while not hasattr(self, "_connected") and time.time() < timeout:
            time.sleep(0.1)

        if not getattr(self, "_connected", False):
            raise TimeoutError("MQTT connection failed or time out")

        # Publish online retained for each line

        for line in LINES:
            topic =f"factory/{line}/status"
            self._client.publish(topic, "online", qos=1, retain=True)
            log.info(f"[STATUS] {topic} = online (retained)")

        

    def disconnect(self) -> None:
        """Cleanly disconnect: publish 'offline' retained for each line, then stop."""
        if self._client is None:
            return
        for line in LINES:
            self._client.publish(f"factory/{line}/status", "offline", qos=1, retain=True)
        self._client.loop_stop()
        self._client.disconnect()
        log.info("Disconnected cleanly")

    # ── Callbacks ──────────────────────────────────────────────────────────────

    def on_connect(self, client, userdata, flags, rc: int) -> None:
        """
        TODO 3: Implement the on_connect callback.
          - Log "Connected (rc=<rc>)" at INFO level on success (rc == 0)
          - Log "Connection refused: <rc>" at ERROR level on failure
        """
        # TODO: implement this callback

        if rc == 0:
            self._connected = True
            log.info(f"Connected (rc ={rc})")
        else:
            log.error(f"Connected refused: {rc}")
            self._connected = False
        pass

    def on_publish(self, client, userdata, mid: int) -> None:
        """
        TODO 4: Implement the on_publish callback.
          - Log "PUBACK received for mid=<mid>" at DEBUG level
        """
        # TODO: implement this callback
        log.debug(f"PUBACK received for mid ={mid}")

        pass

    # ── Sensor Simulation ──────────────────────────────────────────────────────

    def _simulate_reading(self, line: str, sensor: str) -> SensorReading:
        """Generate a realistic simulated sensor reading with Gaussian noise."""
        cfg   = SENSORS[sensor]
        value = round(cfg["base"] + random.gauss(0, cfg["noise"]), 3)
        key   = f"{line}/{sensor}"
        self._seq[key] = self._seq.get(key, 0) + 1
        return SensorReading(
            line=line,
            sensor=sensor,
            value=value,
            unit=cfg["unit"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            seq=self._seq[key],
        )

    def _topic(self, line: str, sensor: str) -> str:
        """
        TODO 5: Return the correct MQTT topic string.
          Format: factory/{line}/{sensor}
          Example: factory/line1/temperature
        """
        # TODO: implement this method

        return f"factory/{line}/{sensor}"

        

    # ── Publishing ─────────────────────────────────────────────────────────────

    def publish_reading(self, line: str, sensor: str) -> SensorReading:
        """
        TODO 6: Simulate a reading and publish it.
          - Generate a SensorReading using _simulate_reading
          - Serialise to JSON (use dataclasses.asdict)
          - Publish to the correct topic at the sensor's configured QoS level
          - Log the publication: "[{line}/{sensor}] value={value} {unit}  QoS={qos}  seq={seq}"
          - Return the SensorReading for testing purposes
        """
        # TODO: implement this method

        reading = self._simulate_reading(line, sensor)

        payload = json.dumps(asdict(reading))

        topic = self._topic(line, sensor)

        qos = SENSORS[sensor]["qos"]

        result = self._client.publish(topic, payload, qos=qos)

        log.info(
            f"[{line}/{sensor}] value = {reading.value} {reading.unit} "
            f"QoS={qos} seq ={reading.seq}"
            )

        return reading

        

    # ── Main Loop ──────────────────────────────────────────────────────────────

    def run(self, interval_s: float = 1.0) -> None:
        """Continuously publish all sensors until interrupted."""
        self.connect()
        log.info("Publishing started (Ctrl-C to stop)")
        try:
            while True:
                for line in LINES:
                    for sensor in SENSORS:
                        self.publish_reading(line, sensor)
                time.sleep(interval_s)
        except KeyboardInterrupt:
            log.info("Shutting down…")
        finally:
            self.disconnect()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pub = SmartFactoryPublisher()
    pub.run()
