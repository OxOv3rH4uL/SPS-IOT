from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
import sys
import fileinput
import boto3
from dotenv import load_dotenv
import os
import time
load_dotenv()


class SetupWindow(QMainWindow):
    def __init__(self):
        super(SetupWindow, self).__init__()

        self.setWindowTitle("SPS IOT MODULE")
        self.setGeometry(650, 200, 600, 300)  
        self.setWindowIcon(QtGui.QIcon("logo.ico"))
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        note_label = QLabel("SPS IOT MODULE is in development and it currently supports RaspberryPi")
        layout.addWidget(note_label)
        vehicle_group = QtWidgets.QGroupBox("Equipment Information")
        vehicle_layout = QVBoxLayout()
        label_vehicle = QLabel("Equipment Name with ID:")
        self.edit_vehicle = QLineEdit(self)
        vehicle_layout.addWidget(label_vehicle)
        vehicle_layout.addWidget(self.edit_vehicle)
        vehicle_group.setLayout(vehicle_layout)
        layout.addWidget(vehicle_group)

        # Type Section
        type_group = QtWidgets.QGroupBox("Type Information")
        type_layout = QVBoxLayout()
        label_type = QLabel("Equipment Type:")
        self.edit_type = QLineEdit(self)
        type_layout.addWidget(label_type)
        type_layout.addWidget(self.edit_type)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Sensor Section
        sensor_group = QtWidgets.QGroupBox("Sensor Information")
        sensor_layout = QVBoxLayout()
        label_sensor_name = QLabel("Type Of Sensor:")
        self.comboBox_sensor_name = QComboBox(self)
        self.comboBox_sensor_name.addItems(["Temperature", "Vibration"])
        label_sensor_type = QLabel("Name of Sensor:")
        self.edit_sensor_type = QLineEdit(self)
        sensor_layout.addWidget(label_sensor_name)
        sensor_layout.addWidget(self.comboBox_sensor_name)
        sensor_layout.addWidget(label_sensor_type)
        sensor_layout.addWidget(self.edit_sensor_type)
        sensor_group.setLayout(sensor_layout)
        layout.addWidget(sensor_group)

        # Submit Button
        button_submit = QPushButton("Submit", self)
        button_submit.clicked.connect(self.submit_clicked)
        layout.addWidget(button_submit)

        # Generated Label (Clickable)
        self.generated_label = QLabel("", self)
        self.generated_label.setOpenExternalLinks(True)
        layout.addWidget(self.generated_label)

        #Generated Label 
        self.gen_label = QLabel("",self)
        layout.addWidget(self.gen_label)

        # Instructions Label
        self.instructions_label = QLabel("", self)
        layout.addWidget(self.instructions_label)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        
        font_id = QFontDatabase.addApplicationFont("Poppins-Medium.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 16)
        font.setPointSize(12)
        self.setFont(font)

        # Apply color changes
        self.setStyleSheet("""
            
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            QComboBox {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #0d1282;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #827d0d;
            }
        """)

    def submit_clicked(self):
        vehicle_info = self.edit_vehicle.text()
        type_info = self.edit_type.text()
        sensor_name_info = self.comboBox_sensor_name.currentText()
        sensor_type_info = self.edit_sensor_type.text()
        if "temperature" in sensor_name_info.lower():
            instruction_label_text = "Make sure to connect the pin in D22"
            self.instructions_label.setText(instruction_label_text)
            file_path = os.path.abspath('./Scripts/SENSOR_TEMPERATURE.py')
            with fileinput.FileInput(file_path, inplace=True) as file:
                for line in file:
                    if line.startswith("VEHICLE="):
                        line = f'VEHICLE="{vehicle_info}"\n'
                    elif line.startswith("TYPE="):
                        line = f'TYPE="{type_info}"\n'
                    elif line.startswith("SENSOR_NAME="):
                        line = f'SENSOR_NAME="{sensor_name_info}"\n'
                    elif line.startswith("SENSOR_TYPE="):
                        line = f'SENSOR_TYPE="{sensor_type_info}"\n'
                    print(line, end='')

            region_name = os.getenv("region_name")
            aws_access_key_id = os.getenv("aws_access_key_id")
            aws_secret_access_key = os.getenv("aws_secret_access_key")
            s3 = boto3.client('s3', region_name=region_name, aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)
            file_name = "./Scripts/SENSOR_TEMPERATURE.py"
            bucket = "<bucket_name>"
            destination = "SENSOR_TEMPERATURE.py"
            s3.upload_file(file_name, bucket, destination)
            s3.put_object_acl(Bucket=bucket, Key=destination, ACL='public-read')
            time.sleep(5)
            # BASH FILES
            file_name = "./BashScripts/TEMPERATURE/service_temperature.sh"
            destination = "service_temperature.sh"
            s3.upload_file(file_name, bucket, destination)
            s3.put_object_acl(Bucket=bucket, Key=destination, ACL='public-read')
            time.sleep(5)
            file_name = "./BashScripts/TEMPERATURE/setup_temperature.sh"
            destination = "setup_temperature.sh"
            s3.upload_file(file_name, bucket, destination)
            s3.put_object_acl(Bucket=bucket, Key=destination, ACL='public-read')
            time.sleep(10)
            name = "Sensor Service Script"
            val = "https:/...../service_temperature.sh"
            label_text = f'<a href="{val}">{name}</a>'
            self.generated_label.setText(label_text)
            label_text2 = f'{name} : {val}'
            self.gen_label.setText(label_text2)

    def handle_link_click(self, url):
        print(f'Link clicked: {url}')


def main():
    app = QApplication([])
    window = SetupWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
