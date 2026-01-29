"""DRAFT: Working on a UI for sb4dfritz with NiceGUI"""

from datetime import datetime
from nicegui import ui, run, Event

from sb4dfritz import HomeAutoSystem, HomeAutoDevice

homeauto = HomeAutoSystem()

def status_update(message:str):
    """Pushes a message to the log window, including a timestamp"""
    current_time = datetime.now().strftime('%X')
    log.push(f"[{current_time}]  {message}")

def build_device_ui(device:HomeAutoDevice):
    """Build a UI card for the device"""
    ## OUTLETS ##
    def onoff_handler(e:Event, d:HomeAutoDevice):
        # temporatily disable control
        ui_control = d.ui_elements['onoff']
        ui_control.disable()
        # check soft off option
        soft_off = d.ui_elements['softofftoggle'].value
        new_state = e.value
        if (not new_state) and soft_off:
            final_state = d.switch_off_when_idle(status_updater=status_update)
        else:
            d.set_switch_state(new_state)
            final_state = d.get_switch_state()
        final_state = 'on' if final_state else 'off'
        status_update(f"{d.name} was switched {final_state}")
        ui_control.enable()
    def autoswitch_handler(e, d):
        ui_control = d.ui_elements['autoswitch']
        ui_control.disable()
        d.set_automatic_switching(e.value)
        ui_control.enable()
        status_update(f"{d.name} set to switch mode {d.get_switch_mode()}")
    def target_temp_handler(e:Event, d:HomeAutoDevice):
        # ui_control = d.ui_elements['temp_slider']
        # ui_control.disable()
        d.set_temperature(e.value)
        status_update(f"{d.name}: target temperature set to {d.get_target_temperature()}")
        # ui_control.enable()
    ## UI CONTROLS
    if device.features.outlet:
        device.ui_elements = {}
        with ui.card().props('flat bordered'):
            ui.label(text=device.name).classes('w-full text-center font-bold text-[17px]')
            # on/off switch
            device.ui_elements['onoff'] = ui.toggle(
                options={True:'On', False:'Off'},
                value=device.get_switch_state(),
                on_change=lambda e, d=device: run.io_bound(onoff_handler, e, d)
            )
            # soft off checkbox
            device.ui_elements['softofftoggle'] = ui.checkbox(
                text='soft off',
                value=True
            )
            # autoswitch toggle
            device.ui_elements['autoswitch'] = ui.toggle(
                options={False:'manual', True:'auto'},
                value=(device.get_switch_mode() == 'auto'),
                on_change=lambda e, d=device: run.io_bound(autoswitch_handler, e, d)
            )
    ## RADIATORS ##
    elif device.features.temp_control:
        device.ui_elements = {}
        with ui.card().props('flat bordered').style('width: 250px;'):
            ui.label(text=device.name).classes('w-full text-center font-bold text-[17px]')
            target_temp = device.get_target_temperature()
            # ui.label(f"Target temperature: {target_temp:0.1f}°C")
            ui.label("Target temperature")
            temp_slider = ui.slider(
                min=8,
                max=28,
                step=0.5,
                value=target_temp,
                on_change=lambda e, d=device: run.io_bound(target_temp_handler, e, d),
            ).props('label-always')
            device.ui_elements['temp_slider'] = temp_slider


# Build UI
devices_by_category = {
    'Outlets': [device for device in homeauto.devices if device.features.outlet],
    'Radiators': [device for device in homeauto.devices if device.features.temp_control]
}
with ui.row():
    ui.label("🏠 sb4dfritz Home Automation Control Panel").classes("text-2xl font-bold")
with ui.row():
    for cat, devices in devices_by_category.items():
        with ui.column():
            ui.label(cat).classes("text-xl font-bold")
            for dev in devices:
                build_device_ui(dev)
    with ui.column().classes('w-150'):
        ui.label("Log Messages").classes("text-xl font-bold")
        log = ui.log(max_lines=15).classes('w-full')


# Start UI in dark mode
ui.dark_mode().enable()
ui.run()
status_update("App started")
