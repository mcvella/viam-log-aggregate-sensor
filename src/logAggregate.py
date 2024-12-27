from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self

from typing import Any, Final, Mapping, Optional


from viam.utils import SensorReading


from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from viam.components.sensor import Sensor

import time
import asyncio
import subprocess
import re
from datetime import datetime
import hashlib
import pytz


class logAggregate(Sensor, Reconfigurable):

    MODEL: ClassVar[Model] = Model(ModelFamily("mcvella", "sensor"), "log-aggregate")
    log_data: dict
    running: bool
    duration: int

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.running = False
        self.log_data = {"error": {}}
        # 10 minutes default
        self.duration = config.attributes.fields["duration"].number_value or 600

        asyncio.ensure_future(self.log_loop())

        return

    async def log_loop(self):
        self.running = True
        cmd = ['journalctl', '-u', 'viam-agent', '-f', '-n', '10']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        pattern = r'^(\w{3} \d{2} \d{2}:\d{2}:\d{2}) (\S+) (\S+)\[(\d+)\]: (\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$'

        while self.running:
            output = process.stdout.readline()
            if output:
                #    'timestamp': match.group(1),
                #    'hostname': match.group(2),
                #    'process': match.group(3),
                #    'pid': int(match.group(4)),
                #    'iso_timestamp': match.group(5),
                #    'log_level': match.group(6),
                #    'service': match.group(7),
                #    'file': match.group(8),
                #    'message': match.group(9)
                match = re.match(pattern, output.strip())
                if match.group(6) == "ERROR":
                    # remove extra logging info
                    m = match.group(9)
                    p = r'\s*\{[^{}]*\}\s*$'
                    m = re.sub(p, '', m)

                    # initialize
                    if not "started" in self.log_data:
                        self.log_data["started"] = match.group(5)
                    message_hash = generate_md5(match.group(8) + m)
                    if message_hash in self.log_data["error"]:
                        self.log_data["error"][message_hash]["times"].append(match.group(5))
                    else:
                        self.log_data["error"][message_hash] = {"count": 1, "times": [match.group(5)], "message": m, "service": match.group(7), "file": match.group(8)}
            for message in self.log_data["error"]:
                for time in self.log_data["error"][message]["times"]:
                    # remove any instanced older than the duration we are tracking
                    diff = compare_timestamps(time, get_current_time_iso())
                    if diff > self.duration:
                        self.log_data["error"][message]["times"] = self.log_data["error"][message]["times"][1:]
                self.log_data["error"][message]["count"] = len(self.log_data["error"][message]["times"])
                if len(self.log_data["error"][message]["times"]) == 0:
                    del self.log_data["error"][message]                    
            await asyncio.sleep(.01)                
                        
    async def get_readings(
        self, *, extra: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, SensorReading]:

        ret = {"count": 0, "errors": []}
        if "started" in self.log_data:
            for message in self.log_data["error"]:
                m = self.log_data["error"][message].copy()
                del m["times"]
                ret["errors"].append(m)
                ret["count"] = ret["count"] + self.log_data["error"][message]["count"]
        ret["errors"] = sorted(ret["errors"], key=lambda x: x['count'], reverse=True)
        return ret



def compare_timestamps(timestamp1, timestamp2):
    # Parse the timestamps into datetime objects
    dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
    dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))

    # Calculate the time difference in seconds
    time_diff_seconds = abs((dt2 - dt1).total_seconds())

    return time_diff_seconds

def generate_md5(input_string):
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    
    # Update the hash object with the bytes of the input string
    md5_hash.update(input_string.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    return md5_hash.hexdigest()

def get_current_time_iso():
    # Get the current time in UTC
    current_time = datetime.now(pytz.UTC)
    
    # Format the time as ISO 8601 with milliseconds
    iso_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return iso_time