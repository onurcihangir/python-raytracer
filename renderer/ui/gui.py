import sys
import time
from datetime import timedelta
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QWidget
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot

import config
from renderer.ui.render_thread import RenderThread

class RayTracerWindow(QMainWindow):
    """
    Main window for the ray tracer GUI
    """
    def __init__(self, width, height, camera, objects, light):
        super().__init__()
        
        self.width = width
        self.height = height
        self.camera = camera
        self.objects = objects
        self.light = light
        
        self.img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        self.initUI()
        self.startRendering()
    
    def initUI(self):
        self.setWindowTitle('Python Ray Tracer')
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.width, self.height)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        self.updateImage(self.img_array)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.width * self.height)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        
        stats_layout = QVBoxLayout()
        
        self.time_label = QLabel("Süre: 00:00:00")
        self.pixels_label = QLabel(f"İşlenen Piksel: 0 / {self.width * self.height} (%0.0)")
        self.rays_label = QLabel("Ray Sayısı: 0")
        self.speed_label = QLabel("Piksel/Saniye: 0.0")
        self.eta_label = QLabel("Tahmini Kalan Süre: --:--:--")
        
        stats_layout.addWidget(self.time_label)
        stats_layout.addWidget(self.pixels_label)
        stats_layout.addWidget(self.rays_label)
        stats_layout.addWidget(self.speed_label)
        stats_layout.addWidget(self.eta_label)
        
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(stats_layout)
        
        self.setCentralWidget(main_widget)
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.updateStats)
        self.stats_timer.start(500)
        
        self.resize(self.width, self.height + 150)
        self.show()
    
    def startRendering(self):
        self.render_thread = RenderThread(self.width, self.height, self.camera, self.objects, self.light)
        self.render_thread.update_signal.connect(self.updateRender)
        self.render_thread.finished_signal.connect(self.renderFinished)
        self.render_thread.progress_signal.connect(self.updateProgress)
        self.render_thread.start()
    
    @pyqtSlot(np.ndarray, int, int)
    def updateRender(self, img_array, start_row, end_row):
        self.img_array[start_row:end_row, :, :] = img_array[start_row:end_row, :, :]
        self.updateImage(self.img_array)
    
    @pyqtSlot(np.ndarray)
    def renderFinished(self, img_array):
        self.img_array = img_array
        self.updateImage(self.img_array)
        self.updateStats()
        
        image = Image.fromarray(self.img_array)
        image.save("output.png")
        
        total_time = config.render_stats["end_time"] - config.render_stats["start_time"]
        print(f"Rendering completed in {total_time:.2f} seconds")
        print(f"Total rays cast: {config.render_stats['ray_count']}")
        print(f"Rays per second: {config.render_stats['ray_count'] / total_time:.2f}")
    
    @pyqtSlot(int)
    def updateProgress(self, processed_pixels):
        """
        Updates the progress bar
        """
        self.progress_bar.setValue(processed_pixels)
    
    def updateImage(self, img_array):
        """
        Updates the QLabel with the rendered image
        """
        height, width, channels = img_array.shape
        bytes_per_line = channels * width
        
        q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        self.image_label.setPixmap(pixmap)
    
    def updateStats(self):
        """
        Updates the statistics labels
        """
        current_time = time.time()
        
        if config.render_stats["end_time"] > 0:
            elapsed = config.render_stats["end_time"] - config.render_stats["start_time"]
            if self.stats_timer.isActive():
                self.stats_timer.stop()
        else:
            elapsed = current_time - config.render_stats["start_time"]
        
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        total_pixels = max(1, config.render_stats["total_pixels"])  # 0'a bölünmeyi önle
        progress = config.render_stats["processed_pixels"] / total_pixels * 100
        
        fps = config.render_stats["processed_pixels"] / max(1, elapsed)
        
        self.time_label.setText(f"Süre: {elapsed_str}")
        self.pixels_label.setText(f"İşlenen Piksel: {config.render_stats['processed_pixels']} / {config.render_stats['total_pixels']} (%{progress:.1f})")
        self.rays_label.setText(f"Ray Sayısı: {config.render_stats['ray_count']}")
        self.speed_label.setText(f"Piksel/Saniye: {fps:.1f}")
        
        if progress > 0 and progress < 100:
            estimated_total = elapsed * 100 / progress
            remaining = estimated_total - elapsed
            remaining_str = str(timedelta(seconds=int(remaining)))
            self.eta_label.setText(f"Tahmini Kalan Süre: {remaining_str}")
        elif progress >= 100:
            self.eta_label.setText("Render Tamamlandı!")
    
    def closeEvent(self, event):
        """
        Stops the render thread when the window is closed
        """
        if hasattr(self, 'render_thread'):
            self.render_thread.stop()
            self.render_thread.wait()
        event.accept()

def start_gui(width, height, camera, objects, light):
    """
    Renders the scene using PyQt GUI
    """
    app = QApplication(sys.argv)
    window = RayTracerWindow(width, height, camera, objects, light)
    sys.exit(app.exec_())