import pandas as pd
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
df_andenes_ute = pd.read_csv('logs/cansat_real.txt', sep=',')
df_andenes_inne = pd.read_csv('logs/cansat_launch.txt', sep=',')
df_spaceport = pd.read_csv('logs/log.txt', sep=',')
print(df_andenes_ute)

df_merged = pd.merge(df_spaceport, df_andenes_ute, on=['elapsed_time','id','time','alt','lat','lng','pressure','ohm','hum','co2','temp','rssi'], how='outer')  # Merge df1 and df2
df_merged = pd.merge(df_merged, df_andenes_inne, on=['elapsed_time','id','time','alt','lat','lng','pressure','ohm','hum','co2','temp','rssi'], how='outer')  # Merge the result with df3

# The "how='outer'" parameter ensures that all unique values from each dataset are included in the merged dataset without overlapping the same values

df_merged = df_merged.sort_values('id') 

df_merged.drop_duplicates(subset=['id'], inplace=True) # Deletes the duplicate id's so we dont get duplicate values

# Saves the merged dataset to a txt file
df_merged.to_csv('merged_data.txt', index=False, sep=',')

# NTC Material constants
A1 = 3.354016e-3
B1 = 2.569850e-4
C1 = 2.620131e-6
D1 = 6.383091e-8
# Logarithmic values of resistance
log_NTC = np.log(df_merged['ohm']/10000)
# Steinhart and Hart Equation
temp = (1 / (A1 + B1 * log_NTC + C1 * log_NTC * log_NTC + D1 * log_NTC * log_NTC * log_NTC)) - 273.15


# Finds the difference between the ID difference to find difference between ID's
df_andenes_ute['loss'] = df_andenes_ute['id'].diff()
df_andenes_inne['loss'] = df_andenes_inne['id'].diff()
df_spaceport['loss'] = df_spaceport['id'].diff()
df_merged['loss'] = df_merged['id'].diff()

# Removes all 1 values to find where packages was lost
loss_au = df_andenes_ute[df_andenes_ute['loss'] > 1]
loss_ai = df_andenes_inne[df_andenes_inne['loss'] > 1]
loss_sp = df_spaceport[df_spaceport['loss'] > 1]
loss = df_merged[df_merged['loss'] > 1]

# Prints number indexes for each datasets loss. The actual packages lost is a little higher, but it show how many times we lost packages
print(f"Packets lost at Spaceport:{len(loss_sp.index)}")
print(f"Packets lost at Andenes inside:{len(loss_ai.index)}")
print(f"Packets lost at Andenes outside:{len(loss_au.index)}")
print(f"Packets lots in total: {len(loss.index)}")


R = 8.31446261815324 # Universal gas constant
T0 = temp + 273.15 # temp in Kelvin
g = 9.80665 # Gravitational constant
M = 0.0289644 # molar mass of Earth's air
P0 = 101033.66 # Pressure at ground level
P = df_merged['pressure'] # pressure in Pa

altitude = (R*T0/(g*M))*np.log(P0/P) # barometric altimeter equation

print(f"Max altitude: {altitude.max()} meters")

# Plot the calculated altitude vs GPS altitude
plt.xticks(np.arange(0,1597, 400)) 
plt.plot(df_merged['time'], altitude)
plt.plot(df_merged['time'], df_merged['alt'], 'r')
plt.xlabel('Time')
plt.ylabel('Altitude')
plt.title('Altitude')
plt.show()

# Plots signal loss at Andenes outside
plt.xticks(np.arange(0,1597, 200))
plt.scatter(loss_au.index, loss_au['loss'], s=2)
plt.xlabel('Index')
plt.ylabel('Packets lost')
plt.title('Signal loss Andenes Ute')
plt.show()

# Plots signal loss at Andenes inside
plt.scatter(loss_ai.index, loss_ai['loss'], s=2)
plt.xlabel('Index')
plt.ylabel('Packets lost')
plt.title('Signal loss Andenes Inne')
plt.show()

# Plots signal loss at Andøya Space
plt.scatter(loss_sp.index, loss_sp['loss'], s=2)
plt.xlabel('Index')
plt.ylabel('Packets lost')
plt.title('Signal loss Spaceport')
plt.show()

# Plots total signal loss
plt.scatter(loss.index, loss['loss'], s=2)
plt.xlabel('Index')
plt.ylabel('Packets lost')
plt.title('Signal lost total')
plt.show()