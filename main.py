import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QListWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from process import image_to_3d_relief
from visor import show_3d_model

RESOURCES_DIR = "resources"
MODELS_DIR = "models"

class ModelerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Modeler")
        self.setGeometry(300, 100, 800, 600)

        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.init_ui()
        os.makedirs(RESOURCES_DIR, exist_ok=True)
        os.makedirs(MODELS_DIR, exist_ok=True)
        self.load_models()

    def init_ui(self):
        layout = QVBoxLayout()

        # Camera preview label
        self.camera_label = QLabel("Camera preview will appear here")
        self.camera_label.setFixedSize(770, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camera_label)

        # Buttons to control camera
        camera_buttons_layout = QHBoxLayout()
        self.start_camera_btn = QPushButton("Start Camera")
        self.start_camera_btn.clicked.connect(self.start_camera)
        camera_buttons_layout.addWidget(self.start_camera_btn)

        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        camera_buttons_layout.addWidget(self.capture_btn)

        self.stop_camera_btn = QPushButton("Stop Camera")
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.stop_camera_btn.setEnabled(False)
        camera_buttons_layout.addWidget(self.stop_camera_btn)

        layout.addLayout(camera_buttons_layout)

        # Generate model button
        self.generate_btn = QPushButton("Generate 3D Model from Captured Image")
        self.generate_btn.clicked.connect(self.generate_model)
        layout.addWidget(self.generate_btn)

        # List of models
        self.models_list = QListWidget()
        layout.addWidget(self.models_list)

        # Buttons for model actions
        buttons_layout = QHBoxLayout()
        self.view_btn = QPushButton("View Selected 3D Model")
        self.view_btn.clicked.connect(self.view_model)
        buttons_layout.addWidget(self.view_btn)

        self.refresh_btn = QPushButton("Refresh Model List")
        self.refresh_btn.clicked.connect(self.load_models)
        buttons_layout.addWidget(self.refresh_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def start_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.critical(self, "Error", "Cannot open camera")
                self.camera = None
                return
        self.timer.start(30)
        self.start_camera_btn.setEnabled(False)
        self.capture_btn.setEnabled(True)
        self.stop_camera_btn.setEnabled(True)

    def update_frame(self):
        ret, frame = self.camera.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.camera_label.setPixmap(pix)

    def capture_image(self):
        if self.camera is None:
            QMessageBox.warning(self, "Warning", "Camera is not running")
            return
        ret, frame = self.camera.read()
        if not ret:
            QMessageBox.warning(self, "Warning", "Failed to capture image")
            return
        save_path = os.path.join(RESOURCES_DIR, "capture.jpg")
        cv2.imwrite(save_path, frame)
        QMessageBox.information(self, "Info", f"Image captured and saved to:\n{save_path}")

    def stop_camera(self):
        self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
        self.camera_label.clear()
        self.camera_label.setText("Camera preview will appear here")
        self.start_camera_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        self.stop_camera_btn.setEnabled(False)

    def generate_model(self):
        input_path = os.path.join(RESOURCES_DIR, "capture.jpg")
        if not os.path.exists(input_path):
            QMessageBox.warning(self, "Warning", "No captured image found. Please capture an image first.")
            return

        name, ok = QInputDialog.getText(self, "Model Name", "Enter a name for the 3D model (no extension):")
        if ok and name.strip():
            output_path = os.path.join(MODELS_DIR, f"{name.strip()}.stl")
            try:
                image_to_3d_relief(input_path, output_path)
                QMessageBox.information(self, "Success", f"3D model saved to:\n{output_path}")
                self.load_models()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate model:\n{e}")
        else:
            QMessageBox.warning(self, "Warning", "Invalid model name.")

    def load_models(self):
        self.models_list.clear()
        if not os.path.exists(MODELS_DIR):
            return
        models = [f for f in os.listdir(MODELS_DIR) if f.endswith(".stl")]
        self.models_list.addItems(models)

    def view_model(self):
        selected_items = self.models_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a model to view.")
            return
        model_name = selected_items[0].text()
        model_path = os.path.join(MODELS_DIR, model_name)
        try:
            show_3d_model(model_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show model:\n{e}")

    def closeEvent(self, event):
        # Properly release camera if window closes
        self.stop_camera()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelerApp()
    window.show()
    sys.exit(app.exec())
