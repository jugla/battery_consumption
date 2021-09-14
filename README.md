# battery_consumption

Battery Consumption custom component for [Home Assistant](https://home-assistant.io/).


![GitHub release](https://img.shields.io/github/release/jugla/battery_consumption)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)


This component is used to compute statistics on a battery (based on its level state)

This component allows to :
- to display the current varation of battery
- the charge in % or in Wh/kWh...
- the discharge in % or in Wh/kWh ...
- the total charge/discharge

The refresh rate is based on battery's level state

## Installation
Either use HACS (default), either manual
### [HACS](https://hacs.xyz/) (Home Assistant Community Store)   {REQUEST ON PROCESS}
1. Go to HACS page on your Home Assistant instance 
1. Select `integration` 
1. Press add icon and search for `battery_consumption` 
1. Select battery_consumption and install 

### Manual
<details><summary>Manual Procedure</summary>
  
1. Download the folder battery_consumption from the latest [release](https://github.com/jugla/battery_consumption/releases) (with right click, save 
link as) 
1. Place the downloaded directory on your Home Assistant machine in the `config/custom_components` folder (when there is no `custom_components` folder in the 
folder where your `configuration.yaml` file is, create it and place the directory there) 
1. restart HomeAssistant
</details>

# Breaking change
<details><summary>detail description</summary>
N/A
</details>

## Using the component
in configuration.yaml, declare :

```yaml
##configuration.yaml example
battery_consumption:
    zoe:
       source: sensor.battery_level
#      attribute : attribute of source to monitor
#      unique_id : to set a unique id to this sensor
#      precision : the precision of state
       unit_of_measurement: kWh
       battery_capacity: 41
    galaxy_s7:
       source: sensor.sm_g930f_niveau_de_batterie
       unit_of_measurement: Wh
       battery_capacity: 11.55

``` 
where :
- source is name of the state to monitor
- attribute is the attribute of source to monitor
- unique_id is to set a unique id to this sensor
- precision is the precision you set (default 2)
- battery_capacity is the capacity of the monitored battery
- unit_of_measurement is the unit of capacity : kWh, Wh, ...

*Only source* item is required

</details>

## Sensor and attribute
For each battery to monitor one sensor is created.
| sensor name | support | unit | Description |
| ---------------|---------|-------|------------------------------------------|
| battery_consumption+*name of sensor to minotor* | V1.0.0 | % | the current value of battery to monitor | 


The sensor is created with the following attribute :

| Attribute name | support | present | unit | Description |
| ---------------|---------|-------|------|------------------------------------|
| Source | V1.0.0 | always | string | the name of battery to monitor | 
| Previous value | V1.0.0 |  always | % | the previous value of battery to monitor |
| Variation | V1.0.0 |  always | % | the difference between current and previous value |
| Battery charge | V1.0.0 |  always | % | the difference between current and previous value if positive (battery is charging) |
| Battery discharge | V1.0.0 |  always | % | the difference between current and previous value if negative (battery is discharging) |
| Total charge | V1.0.0 |  always | % | the sum of all *battery charge* since the beginning | 
| Total discharge | V1.0.0 |  always | % | the sum of all *battery discharge* since the beginning |
| Capacity | V1.0.0 |  if capacity given  | kWh , Wh, ...  | the capacity of the battery cf. yaml |
| Capacity unit | V1.0.0 |  if capacity given | kWh , Wh, ... | the unif of the capacity of the battery cf. yaml |
| Energy charge | V1.0.0 |  if capacity given | kWh , Wh, ... | the *battery charge* converted in energy |
| Energy discharge | V1.0.0 |  if capacity given | kWh , Wh, ... | the *battery discharge* converted in energy |
| Total energy charge | V1.0.0 |  if capacity given | kWh , Wh, ... | the *total battery charge* converted in energy |
| Total energy discharge | V1.0.0 |  if capacity given | kWh , Wh, ... | the *total battery discharge* converted in energy |

## Typical use
Typical use is to follow the consumption of battery thanks to utility meter

```yaml
##configuration.yaml example
template:
  - sensor:
      - name: zoe_batterie_total_charge
        state: "{{ state_attr('sensor.battery_consumption_sensor_battery_level', 'total_energy_charge') }}"
        unit_of_measurement: 'kWh'
        device_class: energy
        state_class: measurement

  - sensor:
      - name: zoe_batterie_total_discharge
        state: "{{ state_attr('sensor.battery_consumption_sensor_battery_level', 'total_energy_discharge') }}"
        unit_of_measurement: 'kWh'
        device_class: energy
        state_class: measurement

## UTILITY METER
utility_meter:
  zoe_batterie_total_charge_daily:
   source: sensor.zoe_batterie_total_charge
   cycle : daily
  zoe_batterie_total_charge_weekly:
   source: sensor.zoe_batterie_total_charge
   cycle : weekly
  zoe_batterie_total_charge_monthly:
   source: sensor.zoe_batterie_total_charge
   cycle : monthly

  zoe_batterie_total_discharge_daily:
   source: sensor.zoe_batterie_total_discharge
   cycle : daily
  zoe_batterie_total_discharge_weekly:
   source: sensor.zoe_batterie_total_discharge
   cycle : weekly
  zoe_batterie_total_discharge_monthly:
   source: sensor.zoe_batterie_total_discharge
   cycle : monthly
``` 

Another typical use is to follow the variation of battery in statistics graph .
```yaml
##configuration.yaml example
template:
  - sensor:
      - name: zoe_batterie_variation
        state: "{{ state_attr('sensor.battery_consumption_sensor_battery_level', 'variation') }}"
        unit_of_measurement: '%'
        device_class: battery
        state_class: measurement
``` 

