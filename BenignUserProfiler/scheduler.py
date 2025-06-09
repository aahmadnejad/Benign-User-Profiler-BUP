#!/usr/bin/env python3

import copy
import random
from datetime import datetime, timedelta

class Scheduler(object):
    def __init__(self):
        self.__tasks = []
        self.__tasks_ids = []
        self.__models = []

    def add_model(self, model):
        """Add a traffic model to the scheduler"""
        self.__models.append(model)
        self.__schedule_model(model)

    def __schedule_model(self, model):
        """Schedule tasks for a single model based on its frequency"""
        task_id = len(self.__tasks)
        
        # Schedule the model for its specified frequency
        for frequency_index in range(model.frequency):
            task = copy.copy(model)
            task.set_start_time(frequency=frequency_index)
            self.__tasks.append((task_id, task))
            self.__tasks_ids.append((task_id, task.get_start_time()))
            task_id += 1

        # Sort tasks by start time
        self.__tasks_ids.sort(key=lambda task: task[1], reverse=True)

    def get_tasks_ids(self):
        """Get the IDs of all scheduled tasks"""
        tasks = [task[0] for task in self.__tasks_ids]
        return tasks

    def get_task_by_id(self, task_id: int):
        """Get a task by its ID"""
        for task in self.__tasks:
            if task[0] == task_id:
                return task[1]
        return None
        
    def get_tasks_count(self):
        """Get the total number of scheduled tasks"""
        return len(self.__tasks)