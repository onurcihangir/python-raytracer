import sys
import time
from datetime import timedelta
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar,
    QWidget, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget,
    QGroupBox, QFormLayout, QMessageBox,
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSlot

import config
from renderer.ui.render_thread import RenderThread
from renderer.ui.scene_builder import build_scene
from renderer.ui.object_dialog import (
    ObjectDialog, summarize_spec, TYPE_LABELS, LightDialog, summarize_light)
from renderer.ui.style import STYLESHEET


class RayTracerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.object_specs = []
        self.light_specs = [{"position": (3, 5, 2), "color": (1, 1, 1), "intensity": 1.0}]
        self.render_thread = None
        self._stopped_by_user = False
        self.img_array = np.zeros((300, 400, 3), dtype=np.uint8)
        self.initUI()

    # ---------- UI construction ----------
    def initUI(self):
        self.setWindowTitle('Python Ray Tracer')
        central = QWidget()
        root = QHBoxLayout()
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)
        central.setLayout(root)

        root.addLayout(self._build_preview_column(), stretch=3)
        root.addWidget(self._build_control_panel(), stretch=1)

        self.setCentralWidget(central)

        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.updateStats)

        self.resize(1000, 640)
        self.show()

    def _build_preview_column(self):
        col = QVBoxLayout()
        col.setSpacing(14)

        title = QLabel("Ray Tracer")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        subtitle = QLabel("Sahne oluştur, ayarla ve render et")
        subtitle.setObjectName("statLabel")
        col.addWidget(title)
        col.addWidget(subtitle)

        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 300)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            "background-color: #14141c; border: 1px solid #34344a;"
            " border-radius: 10px;")
        self.updateImage(self.img_array)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(400 * 300)
        self.progress_bar.setValue(0)

        # Stats card
        stats_card = QGroupBox("İstatistikler")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(2)
        self.time_label = QLabel("Süre: 00:00:00")
        self.pixels_label = QLabel("İşlenen Piksel: 0 / 0 (%0.0)")
        self.rays_label = QLabel("Ray Sayısı: 0")
        self.speed_label = QLabel("Piksel/Saniye: 0.0")
        self.eta_label = QLabel("Tahmini Kalan Süre: --:--:--")
        for w in (self.time_label, self.pixels_label, self.rays_label,
                  self.speed_label, self.eta_label):
            w.setObjectName("statLabel")
            stats_layout.addWidget(w)
        stats_card.setLayout(stats_layout)

        col.addWidget(self.image_label, alignment=Qt.AlignHCenter)
        col.addWidget(self.progress_bar)
        col.addWidget(stats_card)
        col.addStretch()
        return col

    def _build_control_panel(self):
        panel = QWidget()
        panel.setFixedWidth(300)
        layout = QVBoxLayout()
        layout.setSpacing(16)
        panel.setLayout(layout)

        # --- Objects group ---
        obj_group = QGroupBox("Objeler")
        obj_layout = QVBoxLayout()

        self.type_combo = QComboBox()
        for key in ("sphere", "cube", "tetra", "plane", "obj"):
            self.type_combo.addItem(TYPE_LABELS[key], key)

        add_btn = QPushButton("Ekle")
        add_btn.clicked.connect(self.on_add_object)
        del_btn = QPushButton("Sil")
        del_btn.clicked.connect(self.on_remove_object)

        self.object_list = QListWidget()

        add_row = QHBoxLayout()
        add_row.addWidget(self.type_combo)
        add_row.addWidget(add_btn)

        obj_layout.addLayout(add_row)
        obj_layout.addWidget(self.object_list)
        obj_layout.addWidget(del_btn)
        obj_group.setLayout(obj_layout)

        # --- Settings group ---
        set_group = QGroupBox("Ayarlar")
        form = QFormLayout()

        self.width_spin = QSpinBox(); self.width_spin.setRange(1, 4000); self.width_spin.setValue(400)
        self.height_spin = QSpinBox(); self.height_spin.setRange(1, 4000); self.height_spin.setValue(300)
        self.aa_spin = QSpinBox(); self.aa_spin.setRange(1, 4); self.aa_spin.setValue(1)
        form.addRow("Genişlik", self.width_spin)
        form.addRow("Yükseklik", self.height_spin)
        form.addRow("Anti-aliasing", self.aa_spin)
        set_group.setLayout(form)

        # --- Lights group ---
        light_group = QGroupBox("Işıklar")
        light_layout = QVBoxLayout()
        add_light_btn = QPushButton("Işık Ekle")
        add_light_btn.clicked.connect(self.on_add_light)
        del_light_btn = QPushButton("Sil")
        del_light_btn.clicked.connect(self.on_remove_light)
        self.light_list = QListWidget()
        for spec in self.light_specs:
            self.light_list.addItem(summarize_light(spec))
        light_layout.addWidget(add_light_btn)
        light_layout.addWidget(self.light_list)
        light_layout.addWidget(del_light_btn)
        light_group.setLayout(light_layout)

        # --- Action ---
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self.on_start_stop)

        layout.addWidget(obj_group)
        layout.addWidget(set_group)
        layout.addWidget(light_group)
        layout.addWidget(self.start_btn)
        layout.addStretch()

        # collect controls to enable/disable during render
        self._controls = [self.type_combo, add_btn, del_btn, self.object_list,
                          self.width_spin, self.height_spin, self.aa_spin,
                          add_light_btn, del_light_btn, self.light_list]
        return panel

    # ---------- Object management ----------
    def on_add_object(self):
        obj_type = self.type_combo.currentData()
        dialog = ObjectDialog(obj_type, self)
        if dialog.exec_() == ObjectDialog.Accepted:
            spec = dialog.get_result_spec()
            self.object_specs.append(spec)
            self.object_list.addItem(summarize_spec(spec))

    def on_remove_object(self):
        row = self.object_list.currentRow()
        if row < 0:
            return
        self.object_list.takeItem(row)
        del self.object_specs[row]

    def on_add_light(self):
        dialog = LightDialog(self)
        if dialog.exec_() == LightDialog.Accepted:
            spec = dialog.get_result_spec()
            self.light_specs.append(spec)
            self.light_list.addItem(summarize_light(spec))

    def on_remove_light(self):
        row = self.light_list.currentRow()
        if row < 0:
            return
        self.light_list.takeItem(row)
        del self.light_specs[row]

    # ---------- Render lifecycle ----------
    def on_start_stop(self):
        if self.render_thread is not None and self.render_thread.isRunning():
            self._stopped_by_user = True
            self.render_thread.stop()
            return
        self.start_render()

    def start_render(self):
        width = self.width_spin.value()
        height = self.height_spin.value()

        try:
            camera, objects, lights = build_scene(
                width, height, self.object_specs, self.light_specs)
        except Exception as e:
            QMessageBox.critical(self, "Sahne Hatası", f"Sahne kurulamadı:\n{e}")
            return

        config.AA_SAMPLES = self.aa_spin.value()

        self.image_label.setFixedSize(width, height)
        self.img_array = np.zeros((height, width, 3), dtype=np.uint8)
        self.updateImage(self.img_array)
        self.progress_bar.setMaximum(width * height)
        self.progress_bar.setValue(0)

        self._set_controls_enabled(False)
        self.start_btn.setText("Stop")

        self._stopped_by_user = False
        self.render_thread = RenderThread(width, height, camera, objects, lights)
        self.render_thread.update_signal.connect(self.updateRender)
        self.render_thread.finished_signal.connect(self.renderFinished)
        self.render_thread.progress_signal.connect(self.updateProgress)
        self.render_thread.start()
        self.stats_timer.start(500)

    def _set_controls_enabled(self, enabled):
        for w in self._controls:
            w.setEnabled(enabled)

    def _reset_to_idle(self):
        self._set_controls_enabled(True)
        self.start_btn.setText("Start")
        if self.stats_timer.isActive():
            self.stats_timer.stop()

    @pyqtSlot(np.ndarray, int, int)
    def updateRender(self, img_array, start_row, end_row):
        self.img_array[start_row:end_row, :, :] = img_array[start_row:end_row, :, :]
        self.updateImage(self.img_array)

    @pyqtSlot(np.ndarray)
    def renderFinished(self, img_array):
        self.img_array = img_array
        self.updateImage(self.img_array)
        self.updateStats()
        self._reset_to_idle()
        if not getattr(self, "_stopped_by_user", False):
            Image.fromarray(self.img_array).save("output.png")
            total_time = config.render_stats["end_time"] - config.render_stats["start_time"]
            if total_time > 0:
                print(f"Rendering completed in {total_time:.2f} seconds")

    @pyqtSlot(int)
    def updateProgress(self, processed_pixels):
        self.progress_bar.setValue(processed_pixels)

    def updateImage(self, img_array):
        height, width, channels = img_array.shape
        bytes_per_line = channels * width
        q_img = QImage(img_array.data, width, height, bytes_per_line,
                       QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

    def updateStats(self):
        current_time = time.time()
        if config.render_stats["end_time"] > 0:
            elapsed = config.render_stats["end_time"] - config.render_stats["start_time"]
        else:
            elapsed = current_time - config.render_stats["start_time"]

        elapsed_str = str(timedelta(seconds=int(elapsed)))
        total_pixels = max(1, config.render_stats["total_pixels"])
        progress = config.render_stats["processed_pixels"] / total_pixels * 100
        fps = config.render_stats["processed_pixels"] / max(1, elapsed)

        self.time_label.setText(f"Süre: {elapsed_str}")
        self.pixels_label.setText(
            f"İşlenen Piksel: {config.render_stats['processed_pixels']} / "
            f"{config.render_stats['total_pixels']} (%{progress:.1f})")
        self.rays_label.setText(f"Ray Sayısı: {config.render_stats['ray_count']}")
        self.speed_label.setText(f"Piksel/Saniye: {fps:.1f}")

        if 0 < progress < 100:
            remaining = elapsed * 100 / progress - elapsed
            self.eta_label.setText(
                f"Tahmini Kalan Süre: {str(timedelta(seconds=int(remaining)))}")
        elif progress >= 100:
            self.eta_label.setText("Render Tamamlandı!")

    def closeEvent(self, event):
        if self.render_thread is not None and self.render_thread.isRunning():
            self.render_thread.stop()
            self.render_thread.wait()
        event.accept()


def start_gui():
    """Launch the ray tracer GUI with an empty scene."""
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = RayTracerWindow()
    sys.exit(app.exec_())
