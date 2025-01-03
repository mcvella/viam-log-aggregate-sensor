"""
This file registers the model with the Python SDK.
"""

from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .logAggregate import logAggregate

Registry.register_resource_creator(Sensor.SUBTYPE, logAggregate.MODEL, ResourceCreatorRegistration(logAggregate.new, logAggregate.validate))
