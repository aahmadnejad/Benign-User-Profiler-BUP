#!/usr/bin/env python3

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random

class TrafficModel(ABC):
    def __init__(self):
        # Default values
        self.start_time = datetime.now()
        self.frequency = 1
        self.time_interval = 0
        self.model_config = {}

    @abstractmethod
    def generate(self) -> None:
        """Generate traffic for this model"""
        pass

    @abstractmethod
    def verify(self) -> bool:
        """Verify that the model configuration is valid"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Get a string representation of this model"""
        pass

    def get_start_time(self):
        """Get the scheduled start time for this model"""
        return self.start_time
    
    def set_start_time(self, frequency: int):
        """Set the start time for this model based on frequency and time interval"""
        # If time_interval is a list [min, max], use a random value in that range
        if isinstance(self.time_interval, list) and len(self.time_interval) == 2:
            interval = random.randint(self.time_interval[0], self.time_interval[1])
        else:
            interval = self.time_interval
            
        # Add the interval multiplied by frequency to the start time
        self.start_time = self.start_time + timedelta(seconds=frequency * interval)