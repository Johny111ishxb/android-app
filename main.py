from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import os
import mido
import threading
import platform

# Initialize Android-specific classes only when needed
class AndroidServices:
    def __init__(self):
        self.BluetoothAdapter = None
        self.BluetoothDevice = None
        self.WifiManager = None
        self.WifiConfiguration = None
        self.Context = None
        self.Intent = None
        self.Activity = None
        self.initialized = False
        self.is_android = platform.system() == 'Linux' and 'ANDROID' in os.environ

    def initialize(self):
        if not self.is_android or self.initialized:
            return
        
        try:
            from jnius import autoclass, cast
            # Android Bluetooth classes
            self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
            # Android Wi-Fi classes
            self.WifiManager = autoclass('android.net.wifi.WifiManager')
            self.WifiConfiguration = autoclass('android.net.wifi.WifiConfiguration')
            self.Context = autoclass('android.content.Context')
            self.Intent = autoclass('android.content.Intent')
            self.Activity = autoclass('org.kivy.android.PythonActivity')
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize Android services: {str(e)}")

class VibrotactileApp(App):
    def build(self):
        # Initialize Android services
        self.android_services = AndroidServices()
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        self.main_layout.add_widget(Label(
            text='Vibrotactile Music App',
            font_size=20,
            size_hint_y=None,
            height=40
        ))
        
        # Bluetooth section
        self.bt_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.bt_button = Button(text='Connect Bluetooth', size_hint_x=0.5)
        self.bt_button.bind(on_press=self.connect_bluetooth)
        self.bt_layout.add_widget(self.bt_button)
        self.bt_status = Label(text='BT: Not Connected')
        self.bt_layout.add_widget(self.bt_status)
        self.main_layout.add_widget(self.bt_layout)
        
        # Wi-Fi section
        self.wifi_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.wifi_button = Button(text='Connect Wi-Fi', size_hint_x=0.5)
        self.wifi_button.bind(on_press=self.show_wifi_popup)
        self.wifi_layout.add_widget(self.wifi_button)
        self.wifi_status = Label(text='Wi-Fi: Not Connected')
        self.wifi_layout.add_widget(self.wifi_status)
        self.main_layout.add_widget(self.wifi_layout)
        
        # File selection
        self.file_button = Button(
            text='Select MIDI File',
            size_hint_y=None,
            height=40
        )
        self.file_button.bind(on_press=self.show_file_chooser)
        self.main_layout.add_widget(self.file_button)
        
        self.selected_file_label = Label(
            text='No file selected',
            size_hint_y=None,
            height=40
        )
        self.main_layout.add_widget(self.selected_file_label)
        
        # Playback controls
        self.play_button = Button(
            text='Play',
            disabled=True,
            size_hint_y=None,
            height=40
        )
        self.play_button.bind(on_press=self.play_midi)
        self.main_layout.add_widget(self.play_button)
        
        self.stop_button = Button(
            text='Stop',
            disabled=True,
            size_hint_y=None,
            height=40
        )
        self.stop_button.bind(on_press=self.stop_playback)
        self.main_layout.add_widget(self.stop_button)
        
        # Status label for vibration simulation
        self.status_label = Label(
            text='Status: Ready',
            size_hint_y=None,
            height=40
        )
        self.main_layout.add_widget(self.status_label)
        
        # Initialize variables
        self.midi_file = None
        self.is_playing = False
        self.play_thread = None
        self.stop_event = threading.Event()
        self.bluetooth_connected = False
        self.wifi_connected = False
        
        # Check for default MIDI file in app directory
        default_midi = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.mid')
        if os.path.exists(default_midi):
            self.midi_file = default_midi
            self.selected_file_label.text = f"Selected: {os.path.basename(default_midi)}"
            self.play_button.disabled = False
        
        # Set platform flag
        self.is_android = self.android_services.is_android
        if not self.is_android:
            self.bt_status.text = 'BT: Not available on PC'
            self.wifi_status.text = 'Wi-Fi: Not available on PC'
        
        return self.main_layout
    
    def connect_bluetooth(self, instance):
        """Connect to the ESP32-C3 SuperMini via Bluetooth"""
        if not self.is_android:
            self.bt_status.text = 'BT: Not available on PC'
            return
        
        # Initialize Android services if not already done
        self.android_services.initialize()
        if not self.android_services.initialized:
            self.bt_status.text = 'BT: Initialization failed'
            return
        
        try:
            # Get the default Bluetooth adapter
            adapter = self.android_services.BluetoothAdapter.getDefaultAdapter()
            if adapter is None:
                self.bt_status.text = 'BT: No Bluetooth adapter'
                return
            
            # Check if Bluetooth is enabled
            if not adapter.isEnabled():
                activity = self.android_services.Activity.mActivity
                intent = self.android_services.Intent(self.android_services.BluetoothAdapter.ACTION_REQUEST_ENABLE)
                activity.startActivityForResult(intent, 1)
                self.bt_status.text = 'BT: Enabling...'
                return
            
            # Scan for devices (simplified for demo)
            self.bt_status.text = 'BT: Scanning...'
            devices = adapter.getBondedDevices().toArray()
            
            # Look for ESP32-C3 SuperMini (assumed name)
            target_device = None
            for device in devices:
                device_name = device.getName()
                if device_name and 'ESP32-C3' in device_name:
                    target_device = device
                    break
            
            if target_device:
                self.bt_status.text = f'BT: Connecting to {target_device.getName()}'
                # For demo, simulate a connection (no GATT for now)
                self.bluetooth_connected = True
                self.bt_status.text = f'BT: Connected to {target_device.getName()}'
            else:
                self.bt_status.text = 'BT: ESP32-C3 not found'
        
        except Exception as e:
            self.bt_status.text = f'BT: Error - {str(e)}'
    
    def show_wifi_popup(self, instance):
        """Show Wi-Fi connection popup"""
        if not self.is_android:
            self.wifi_status.text = 'Wi-Fi: Not available on PC'
            return
        
        # Initialize Android services if not already done
        self.android_services.initialize()
        if not self.android_services.initialized:
            self.wifi_status.text = 'Wi-Fi: Initialization failed'
            return
        
        content = BoxLayout(orientation='vertical')
        self.ssid_input = TextInput(hint_text='Enter SSID', multiline=False)
        content.add_widget(self.ssid_input)
        self.password_input = TextInput(hint_text='Enter Password', multiline=False, password=True)
        content.add_widget(self.password_input)
        
        buttons = BoxLayout(size_hint_y=None, height=40)
        connect_button = Button(text='Connect')
        cancel_button = Button(text='Cancel')
        buttons.add_widget(cancel_button)
        buttons.add_widget(connect_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Connect to Wi-Fi', content=content, size_hint=(0.9, 0.5))
        
        def connect_clicked(instance):
            self.connect_wifi(self.ssid_input.text, self.password_input.text)
            popup.dismiss()
        
        def cancel_clicked(instance):
            popup.dismiss()
        
        connect_button.bind(on_press=connect_clicked)
        cancel_button.bind(on_press=cancel_clicked)
        popup.open()
    
    def connect_wifi(self, ssid, password):
        """Connect to a Wi-Fi network"""
        try:
            self.wifi_status.text = f'Wi-Fi: Connecting to {ssid}...'
            activity = self.android_services.Activity.mActivity
            wifi_manager = self.android_services.WifiManager.cast(
                self.android_services.WifiManager,
                activity.getSystemService(self.android_services.Context.WIFI_SERVICE)
            )
            
            # Check if Wi-Fi is enabled
            if not wifi_manager.isWifiEnabled():
                wifi_manager.setWifiEnabled(True)
            
            # Configure Wi-Fi network
            wifi_config = self.android_services.WifiConfiguration()
            wifi_config.SSID = f'"{ssid}"'
            wifi_config.preSharedKey = f'"{password}"'
            
            # Add and connect to the network
            network_id = wifi_manager.addNetwork(wifi_config)
            if network_id != -1:
                wifi_manager.disconnect()
                wifi_manager.enableNetwork(network_id, True)
                wifi_manager.reconnect()
                self.wifi_connected = True
                self.wifi_status.text = f'Wi-Fi: Connected to {ssid}'
            else:
                self.wifi_status.text = 'Wi-Fi: Connection failed'
        
        except Exception as e:
            self.wifi_status.text = f'Wi-Fi: Error - {str(e)}'
    
    def show_file_chooser(self, instance):
        """Show file chooser to select a MIDI file"""
        content = BoxLayout(orientation='vertical')
        app_dir = os.path.dirname(os.path.abspath(__file__))
        file_chooser = FileChooserListView(path=app_dir, filters=['*.mid', '*.midi'])
        content.add_widget(file_chooser)
        
        buttons = BoxLayout(size_hint_y=None, height=40)
        select_button = Button(text='Select')
        cancel_button = Button(text='Cancel')
        buttons.add_widget(cancel_button)
        buttons.add_widget(select_button)
        content.add_widget(buttons)
        
        popup = Popup(title='Select MIDI File', content=content, size_hint=(0.9, 0.9))
        
        def select_clicked(instance):
            if file_chooser.selection:
                self.midi_file = file_chooser.selection[0]
                self.selected_file_label.text = f"Selected: {os.path.basename(self.midi_file)}"
                self.play_button.disabled = False
            popup.dismiss()
        
        def cancel_clicked(instance):
            popup.dismiss()
        
        select_button.bind(on_press=select_clicked)
        cancel_button.bind(on_press=cancel_clicked)
        popup.open()
    
    def play_midi(self, instance):
        """Play the MIDI file and simulate vibrations"""
        if self.is_playing or not self.midi_file:
            return
        
        self.is_playing = True
        self.stop_event.clear()
        self.play_button.disabled = True
        self.stop_button.disabled = False
        self.status_label.text = 'Status: Playing'
        
        # Start playback in a separate thread
        self.play_thread = threading.Thread(target=self.playback_thread)
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def stop_playback(self, instance):
        """Stop the MIDI playback"""
        if self.is_playing:
            self.stop_event.set()
            self.is_playing = False
            self.play_button.disabled = False
            self.stop_button.disabled = True
            self.status_label.text = 'Status: Stopped'
    
    def playback_thread(self):
        """Simulate MIDI playback and vibrations"""
        try:
            midi_data = mido.MidiFile(self.midi_file)
            
            def update_ui(dt):
                if not self.is_playing:
                    self.status_label.text = 'Status: Stopped'
            
            for msg in midi_data.play():
                if self.stop_event.is_set():
                    break
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Simulate vibration for each note-on event
                    self.status_label.text = f'Status: Vibrate (Note: {msg.note})'
                    print(f"Sending vibration signal: Note {msg.note}, Time {msg.time:.2f}s")
                    Clock.schedule_once(update_ui)
            
            # Reset UI when done
            def reset_ui(dt):
                self.is_playing = False
                self.play_button.disabled = False
                self.stop_button.disabled = True
                self.status_label.text = 'Status: Finished'
            
            Clock.schedule_once(reset_ui)
        
        except Exception as e:
            def show_error(dt):
                self.status_label.text = f'Status: Error - {str(e)}'
                self.is_playing = False
                self.play_button.disabled = False
                self.stop_button.disabled = True
            
            Clock.schedule_once(show_error)

if __name__ == '__main__':
    VibrotactileApp().run()