import pv_channel
import json
import numpy as np
import pandas as pd
from datetime import datetime

class Test:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {
            'variables_to_monitor': [],
            'models_and_scalers': {},
            'PVname': {},
            'Outputname': {},
            'Freq': {}
        }
        self.variable_data = {}
        self.load_config()
        self.init_channel()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
            # print("Config loaded:", self.config)
            for variable in self.config['variables_to_monitor']:
                self.variable_data[variable] = {
                    'data_vector': np.zeros(360),
                    'time_vector': [],
                    'results_df': pd.DataFrame(columns=['Time', 'Anomaly']),
                    'last_save_time': datetime.min
                }
            return self.config  # 确保返回新的配置 
        
        except FileNotFoundError:
            print("Config file not found. Please check the path.")
        except json.JSONDecodeError:
            print("Error parsing the config file. Please check the file format.")

    def init_channel(self):
        self.input_channel = pv_channel.PvChannel()
        self.output_channel = pv_channel.PvChannel()
        self.input_channel_old = {}
        self.output_channel_old = {}
        self.push_pvs()

    def push_pvs(self):
        self.input_channel_old = self.input_channel.channelDict.copy()
        self.output_channel_old = self.output_channel.channelDict.copy()
        self.push_channels(self.input_channel, self.input_channel_old, "PVname")
        self.push_channels(self.output_channel, self.output_channel_old, "Outputname")

    def push_channels(self, channel, channel_old, define_name):
        for variable_name in channel_old:
            if variable_name not in self.config[define_name].items():
                channel.remove(variable_name)
        for variable_name, pvname in self.config[define_name].items():
            channel.push(variable_name, pvname)



test1 = Test("./config.json")
# print(test1.output_channel.get_value("DTL1BackT"))
print(test1.output_channel.channelDict)
print(test1.input_channel.channelDict)

for i in range(5):
    user_input = input("请输入：")
    test1.load_config()
    test1.push_pvs()
    print(test1.output_channel.channelDict)
    print(test1.input_channel.channelDict)