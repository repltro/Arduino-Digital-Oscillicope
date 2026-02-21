import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports
import threading

BAUD_RATE = 115200
MAX_POINTS = 200

x_data = list(range(MAX_POINTS))
y_voltage = [0.0] * MAX_POINTS

current_pot1 = 512.0
current_pot2 = 0.0

ser = None
is_connected = False

def get_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_serial():
    global ser, is_connected
    port = dpg.get_value("port_combo")
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        is_connected = True
        dpg.set_value("status_text", f"Connected to {port}")
    except Exception as e:
        is_connected = False
        dpg.set_value("status_text", "Connection Failed")

def refresh_ports():
    dpg.configure_item("port_combo", items=get_ports())

def read_serial_data():
    global y_voltage, current_pot1, current_pot2
    while True:
        if is_connected and ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                data_list = line.split(',')
                
                if len(data_list) == 7:
                    # Index 0 is Pot 1 raw, Index 3 is Exp. Voltage, Index 6 is Pot 2 mapped
                    current_pot1 = float(data_list[0])
                    exp_voltage = float(data_list[3])
                    current_pot2 = float(data_list[6])
                    
                    y_voltage.pop(0)
                    y_voltage.append(exp_voltage)
            except:
                pass

serial_thread = threading.Thread(target=read_serial_data, daemon=True)
serial_thread.start()

dpg.create_context()

with dpg.window(label="Nanoscope", width=800, height=600):
    with dpg.group(horizontal=True):
        dpg.add_combo(items=get_ports(), tag="port_combo", width=150)
        dpg.add_button(label="Refresh", callback=refresh_ports)
        dpg.add_button(label="Connect", callback=connect_serial)
        dpg.add_text("Disconnected", tag="status_text")
    
    with dpg.plot(label="Voltage Plot", height=500, width=-1):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Voltage (V)", tag="y_axis")
        dpg.add_line_series(x_data, y_voltage, tag="voltage_series", parent="y_axis")

dpg.create_viewport(title='Custom Oscilloscope', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    # 1. Update the line data
    dpg.set_value("voltage_series", [x_data, y_voltage])
    
    # 2. Calculate the camera Y-Transformation (0 to 60V center point)
    center_y = (current_pot1 / 1023.0) * 60.0
    
    # 3. Calculate the camera Zoom Span (Invert it so larger pot map = tighter zoom)
    # If pot2 is 0, span is 60V. If pot2 is 10, span is 5V.
    span_y = 60.0 - (current_pot2 * 5.5)
    if span_y < 2.0:
        span_y = 2.0 
        
    # 4. Apply the new dynamic limits to the Y-axis
    y_min = center_y - (span_y / 2.0)
    y_max = center_y + (span_y / 2.0)
    dpg.set_axis_limits("y_axis", y_min, y_max)
    
    dpg.render_dearpygui_frame()

if ser and ser.is_open:
    ser.close()
dpg.destroy_context()
