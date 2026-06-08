from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDoubleSpinBox, QPushButton, QHBoxLayout,
    QVBoxLayout, QColorDialog, QFileDialog, QLabel, QDialogButtonBox,
)
from PyQt5.QtGui import QColor

from renderer.ui.scene_builder import make_material

# Field layout per object type
TYPE_LABELS = {
    "sphere": "Küre",
    "cube": "Küp",
    "tetra": "Dörtyüzlü",
    "plane": "Düzlem",
    "obj": "OBJ Model",
}


def _spin(minv, maxv, default, step=0.1):
    s = QDoubleSpinBox()
    s.setRange(minv, maxv)
    s.setSingleStep(step)
    s.setDecimals(3)
    s.setValue(default)
    return s


class ObjectDialog(QDialog):
    def __init__(self, obj_type, parent=None):
        super().__init__(parent)
        self.obj_type = obj_type
        self.setWindowTitle(f"{TYPE_LABELS.get(obj_type, obj_type)} Ekle")
        self._color = QColor(204, 178, 153)  # default beige
        self._obj_path = None

        form = QFormLayout()

        # Position / center / point (x,y,z)
        self._px = _spin(-1000, 1000, 0.0)
        self._py = _spin(-1000, 1000, 0.0)
        self._pz = _spin(-1000, 1000, -3.0)

        if obj_type in ("sphere",):
            form.addRow("Konum X", self._px)
            form.addRow("Konum Y", self._py)
            form.addRow("Konum Z", self._pz)
            self._radius = _spin(0.01, 1000, 1.0)
            form.addRow("Yarıçap", self._radius)

        elif obj_type in ("cube", "tetra"):
            form.addRow("Merkez X", self._px)
            form.addRow("Merkez Y", self._py)
            form.addRow("Merkez Z", self._pz)
            self._size = _spin(0.01, 1000, 1.0)
            form.addRow("Boyut", self._size)

        elif obj_type == "plane":
            self._py.setValue(-1.0)
            self._pz.setValue(0.0)
            form.addRow("Nokta X", self._px)
            form.addRow("Nokta Y", self._py)
            form.addRow("Nokta Z", self._pz)
            self._nx = _spin(-1, 1, 0.0)
            self._ny = _spin(-1, 1, 1.0)
            self._nz = _spin(-1, 1, 0.0)
            form.addRow("Normal X", self._nx)
            form.addRow("Normal Y", self._ny)
            form.addRow("Normal Z", self._nz)

        elif obj_type == "obj":
            self._file_label = QLabel("(dosya seçilmedi)")
            file_btn = QPushButton("Dosya Seç…")
            file_btn.clicked.connect(self._pick_file)
            file_row = QHBoxLayout()
            file_row.addWidget(file_btn)
            file_row.addWidget(self._file_label)
            form.addRow("OBJ Dosyası", self._wrap(file_row))
            self._scale = _spin(0.001, 10000, 30.0)
            form.addRow("Ölçek", self._scale)
            form.addRow("Konum X", self._px)
            form.addRow("Konum Y", self._py)
            form.addRow("Konum Z", self._pz)

        # Material: color + reflectivity (all types)
        self._color_btn = QPushButton("Renk Seç…")
        self._color_btn.clicked.connect(self._pick_color)
        self._update_color_btn()
        form.addRow("Renk", self._color_btn)
        self._reflect = _spin(0.0, 1.0, 0.1, step=0.05)
        form.addRow("Yansıma", self._reflect)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _wrap(self, inner_layout):
        from PyQt5.QtWidgets import QWidget
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    def _pick_color(self):
        c = QColorDialog.getColor(self._color, self, "Renk Seç")
        if c.isValid():
            self._color = c
            self._update_color_btn()

    def _update_color_btn(self):
        self._color_btn.setStyleSheet(
            f"background-color: {self._color.name()};")

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "OBJ Dosyası Seç", "", "OBJ Dosyaları (*.obj)")
        if path:
            self._obj_path = path
            self._file_label.setText(path.split("/")[-1])

    def _on_accept(self):
        if self.obj_type == "obj" and not self._obj_path:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Eksik", "Lütfen bir OBJ dosyası seçin.")
            return
        self.accept()

    def _material(self):
        diffuse = (self._color.red() / 255.0,
                   self._color.green() / 255.0,
                   self._color.blue() / 255.0)
        return make_material(diffuse, self._reflect.value())

    def get_result_spec(self):
        """Return the object-spec dict from current field values."""
        material = self._material()
        pos = (self._px.value(), self._py.value(), self._pz.value())

        if self.obj_type == "sphere":
            return {"type": "sphere", "position": pos,
                    "radius": self._radius.value(), "material": material}
        if self.obj_type == "cube":
            return {"type": "cube", "center": pos,
                    "size": self._size.value(), "material": material}
        if self.obj_type == "tetra":
            return {"type": "tetra", "center": pos,
                    "size": self._size.value(), "material": material}
        if self.obj_type == "plane":
            return {"type": "plane", "point": pos,
                    "normal": (self._nx.value(), self._ny.value(), self._nz.value()),
                    "material": material}
        if self.obj_type == "obj":
            return {"type": "obj", "path": self._obj_path,
                    "scale": self._scale.value(), "position": pos,
                    "material": material}
        raise ValueError(f"Unknown type {self.obj_type}")


def summarize_spec(spec):
    """One-line label for the object list widget."""
    t = spec["type"]
    label = TYPE_LABELS.get(t, t)
    if t == "sphere":
        return f"{label} @ {spec['position']} r={spec['radius']}"
    if t in ("cube", "tetra"):
        return f"{label} @ {spec['center']} s={spec['size']}"
    if t == "plane":
        return f"{label} nokta={spec['point']} normal={spec['normal']}"
    if t == "obj":
        name = spec["path"].split("/")[-1] if spec.get("path") else "?"
        return f"{label} {name} @ {spec['position']} x{spec['scale']}"
    return label
