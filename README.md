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
       unit_of_measurement: kWh
       battery_capacity: 41
#      unique_id : to set a unique id to this sensor
#      attribute : attribute of source to monitor
#      precision : the precision of state
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

Only source is required

</details>

