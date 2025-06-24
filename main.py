import sys
import os

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QRadioButton,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QHeaderView,
)
from PyQt5.QtCore import Qt
from extract_all_files import extract_all_files
from extract_selected_file import extract_selected_file
from add_files import add_files
from save_bm import save_bm
from ui_helpers import update_file_count_label, search_table
from brute_force_decode_array import brute_force_decode_array
from context_menu import open_context_menu, copy_selected_row
from export_decrypted_file import export_decrypted_file


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(36)
        self.setStyleSheet("""
            background-color: #181818;
            color: #e0e0e0;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        self.title = QLabel("MagicTool - BM File Viewer", self)
        self.title.setStyleSheet("font-weight: bold; font-size: 12pt; color: #e0e0e0;")
        layout.addWidget(self.title)
        layout.addStretch()
        self.min_btn = QPushButton("–", self)
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.setStyleSheet(
            "QPushButton { background: #232323; color: #e0e0e0; border: none; border-radius: 4px; } QPushButton:hover { background: #444; }"
        )
        self.min_btn.clicked.connect(self.minimize)
        layout.addWidget(self.min_btn)
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet(
            "QPushButton { background: #8B0000; color: #fff; border: none; border-radius: 4px; } QPushButton:hover { background: #a83232; }"
        )
        self.close_btn.clicked.connect(self.close_window)
        layout.addWidget(self.close_btn)
        self._mouse_pos = None

    def minimize(self):
        if self.parent:
            self.parent.showMinimized()

    def close_window(self):
        if self.parent:
            self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pos and event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self._mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_pos = None


class BMViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MagicTool - BM File Viewer")
        import os

        self.setWindowFlags(Qt.FramelessWindowHint)
        if getattr(sys, "frozen", False):
            icon_path = os.path.join(sys._MEIPASS, "magictool.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "magictool.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1200, 800)
        self.files_to_add = []  # Ensure this is always initialized
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Top: Label
        self.label = QLabel("Open a .bm file to view its contents.")
        main_layout.addWidget(self.label)

        # Table for file list
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            [
                "File Name",
                "Unpacked Size",
                "Packed Size",
                "Offset",
                "File Time",
                "File State",
            ]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(
            lambda pos: open_context_menu(self, pos)
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        # Set column sizes: Name larger, sizes/offset smaller
        self.table.setColumnWidth(
            0, 140
        )  # File Name (adjusted to be between previous and current)
        self.table.setColumnWidth(1, 120)  # Unpacked Size
        self.table.setColumnWidth(2, 120)  # Packed Size
        self.table.setColumnWidth(3, 120)  # Offset
        self.table.setColumnWidth(4, 160)  # File Time
        self.table.setColumnWidth(5, 180)  # File State
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        main_layout.addWidget(self.table)

        # File count label
        self.file_count_label = QLabel("")
        main_layout.addWidget(self.file_count_label)

        # Game type selection
        game_group = QGroupBox("Game")
        game_layout = QVBoxLayout()
        self.rb_dom1 = QRadioButton("Dawn Of Magic")
        self.rb_bm = QRadioButton("Blood Magic")
        self.rb_bm_sm = QRadioButton("Blood Magic Smoke and Mirrors")
        self.rb_dom_gold = QRadioButton("Dawn Of Magic Gold")
        self.rb_dom1.setChecked(True)
        game_layout.addWidget(self.rb_dom1)
        game_layout.addWidget(self.rb_bm)
        game_layout.addWidget(self.rb_bm_sm)
        game_layout.addWidget(self.rb_dom_gold)
        game_group.setLayout(game_layout)

        # Search box
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        search_box_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(lambda: search_table(self))
        search_box_layout.addWidget(self.search_box)
        search_box_layout.addWidget(self.search_btn)
        search_layout.addLayout(search_box_layout)
        search_group.setLayout(search_layout)

        # Extraction buttons
        extract_group = QGroupBox("BM Extraction")
        extract_layout = QVBoxLayout()
        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_bm_file)
        self.extract_all_btn = QPushButton("Extract All")
        self.extract_all_btn.clicked.connect(lambda: extract_all_files(self))
        self.extract_selected_btn = QPushButton("Extract Selected")
        self.extract_selected_btn.clicked.connect(lambda: extract_selected_file(self))
        self.export_decrypted_btn = QPushButton("Export Decrypted")
        self.export_decrypted_btn.clicked.connect(lambda: export_decrypted_file(self))
        self.bruteforce_btn = QPushButton("Brute Force Decode Array")
        self.bruteforce_btn.clicked.connect(lambda: brute_force_decode_array(self))
        extract_layout.addWidget(self.open_btn)
        extract_layout.addWidget(self.extract_all_btn)
        extract_layout.addWidget(self.extract_selected_btn)
        # extract_layout.addWidget(self.export_decrypted_btn)
        # extract_layout.addWidget(self.bruteforce_btn)
        extract_group.setLayout(extract_layout)

        # Create BM file group
        create_group = QGroupBox("Create BM file")
        create_layout = QVBoxLayout()
        self.add_files_btn = QPushButton("Add files")
        self.save_bm_btn = QPushButton("Save BM")
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Plain", "Encryption", "Encryption/Compression"])
        from PyQt5.QtWidgets import QListView

        self.combo_mode.setView(QListView())  # Force non-native popup for dark styling
        create_layout.addWidget(self.combo_mode)
        create_layout.addWidget(self.add_files_btn)
        create_layout.addWidget(self.save_bm_btn)
        create_group.setLayout(create_layout)

        # Status label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Layout for bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(game_group)
        bottom_layout.addWidget(search_group)
        bottom_layout.addWidget(create_group)
        bottom_layout.addWidget(extract_group)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect buttons
        # self.add_files_btn.clicked.connect(lambda: add_files(self))  # Removed duplicate connection
        # self.save_bm_btn.clicked.connect(lambda: save_bm(self))      # Removed duplicate connection
        # self.extract_all_btn.clicked.connect(lambda: extract_all_files(self))  # Removed duplicate connection

    def update_file_count_label(self):
        update_file_count_label(self)

    def search_table(self):
        search_table(self)

    def open_context_menu(self, pos):
        open_context_menu(self, pos)

    def copy_selected_row(self):
        copy_selected_row(self)

    def extract_all_files(self):
        extract_all_files(self)

    def extract_selected_file(self):
        extract_selected_file(self)

    def add_files(self):
        add_files(self)

    def save_bm(self):
        save_bm(self)

    def brute_force_decode_array(self, encoded: bytes, expected: bytes, array_len=1024):
        return brute_force_decode_array(self, encoded, expected, array_len)

    def open_bm_file(self):
        import struct
        import datetime

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open .bm File", "", "BM Files (*.bm)"
        )
        if file_path:
            self.label.setText(f"Loaded: {file_path}")
            self.table.setRowCount(0)
            try:
                with open(file_path, "rb") as f:
                    count_bytes = f.read(8)
                    if len(count_bytes) < 8:
                        raise Exception("File too short for header")
                    file_count = struct.unpack("<Q", count_bytes)[0]
                    self.status_label.setText(f"Number of files: {file_count}")
                    entries_bytes = f.read(file_count * 92)
                    for num in range(file_count):
                        base = num * 92
                        entry = entries_bytes[base : base + 92]
                        # File name (null-terminated ASCII)
                        name_bytes = entry[:64]
                        name = name_bytes.split(b"\x00", 1)[0].decode(
                            "ascii", errors="replace"
                        )
                        unpacked_size = struct.unpack("<I", entry[64:68])[0]
                        packed_size = struct.unpack("<I", entry[68:72])[0]
                        offset = struct.unpack("<Q", entry[72:80])[0]
                        file_time = struct.unpack("<Q", entry[80:88])[0]
                        file_state = struct.unpack("<I", entry[88:92])[0]
                        # File time to string
                        try:
                            dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(
                                microseconds=file_time / 10
                            )
                            file_time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            file_time_str = str(file_time)
                        # File state string
                        if file_state == 5:
                            state_str = "Encrypted/Compressed"
                        elif file_state == 4:
                            state_str = "Encrypted"
                        elif file_state == 1:
                            state_str = "Compressed"
                        elif file_state == 0:
                            state_str = "Plain"
                        else:
                            state_str = f"Unknown ({file_state})"
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QTableWidgetItem(name))
                        self.table.setItem(row, 1, QTableWidgetItem(str(unpacked_size)))
                        self.table.setItem(row, 2, QTableWidgetItem(str(packed_size)))
                        self.table.setItem(row, 3, QTableWidgetItem(str(offset)))
                        self.table.setItem(row, 4, QTableWidgetItem(file_time_str))
                        self.table.setItem(row, 5, QTableWidgetItem(state_str))
                self.update_file_count_label()
            except Exception as ex:
                from ui_helpers import show_dark_message

                show_dark_message(self, "Error", str(ex))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    viewer = BMViewer()
    # Set dark style sheet with dark red as primary color
    dark_red = "#8B0000"
    style = f"""
        QWidget {{
            background-color: #141414;
            color: #e0e0e0;
            font-size: 8pt;
        }}
        QGroupBox {{
            border: 1px solid #424242;
            margin-top: 10px;
            color: #e0e0e0;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
            color: white;
        }}
        QPushButton {{
            background-color: {dark_red};
            color: #fff;
            border-radius: 4px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: #a83232;
        }}
        QLineEdit, QComboBox, QTextEdit {{
            background-color: #212121;
            color: #fff;
            border-radius: 4px;
            padding: 6px 12px;
            border: 1px solid #444;
        }}
        QComboBox QAbstractItemView {{
            background-color: #232323;
            color: #fff;
            selection-background-color: #8B0000;
            selection-color: #fff;
            border-radius: 0 0 4px 4px;
        }}
        QComboBox::drop-down {{
            background: #232323;
            border-left: 1px solid #444;
            width: 28px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: none;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 8px solid #fff;
            margin: 0 8px;
        }}
        QTableWidget {{
            background-color: #141414;
            color: #fff;
            gridline-color: #444;
            selection-background-color: {dark_red};
            selection-color: #fff;
        }}
        QHeaderView::section {{
            background-color: #212121;
            color: #fff;
            padding: 4px 2px;
            border: none;
        }}
        QLabel {{ color: #e0e0e0; }}
        QRadioButton {{
            color: #e0e0e0;
            spacing: 8px;
            font-size: 10pt;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid #8B0000;
            background: #232323;
        }}
        QRadioButton::indicator:checked {{
            background: #8B0000;
            border: 2px solid #232323;
        }}
        QRadioButton::indicator:unchecked {{
            background: #232323;
            border: 2px solid #8B0000;
        }}
        QScrollBar:vertical {{
            background: #232323;
            width: 12px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: #8B0000;
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: #141414;
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: #232323;
            height: 12px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: #8B0000;
            min-width: 20px;
            border-radius: 6px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
            width: 0px;
        }}
        /* Ensure table scrollbars are dark */
        QTableWidget QScrollBar:vertical, QTableWidget QScrollBar:horizontal {{
            background: #232323;
        }}
        /* Style the top-left corner cell */
        QTableCornerButton::section {{
            background: #212121;
            border: 1px solid #444;
        }}
    """
    viewer.setStyleSheet(style)
    viewer.show()
    sys.exit(app.exec_())
