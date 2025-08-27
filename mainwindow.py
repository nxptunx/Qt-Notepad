# This Python file uses the following encoding: utf-8
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog,
    QMessageBox, QDialog, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PySide6.QtGui import QKeySequence, QAction


class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find and Replace")

        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        find_label = QLabel("Find:")
        replace_label = QLabel("Replace with:")

        find_button = QPushButton("Find Next")
        replace_button = QPushButton("Replace")
        replace_all_button = QPushButton("Replace All")

        layout = QVBoxLayout()
        layout.addLayout(self._create_input_row(find_label, self.find_input))
        layout.addLayout(self._create_input_row(replace_label, self.replace_input))

        button_layout = QHBoxLayout()
        button_layout.addWidget(find_button)
        button_layout.addWidget(replace_button)
        button_layout.addWidget(replace_all_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        find_button.clicked.connect(self.find_next)
        replace_button.clicked.connect(self.replace_one)
        replace_all_button.clicked.connect(self.replace_all)

    def _create_input_row(self, label, line_edit):
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return layout

    def find_next(self):
        cursor = self.editor.textCursor()
        text_to_find = self.find_input.text()
        found = self.editor.find(text_to_find)
        if not found:
            cursor.movePosition(cursor.Start)
            if not self.editor.find(text_to_find):
                QMessageBox.information(self, "Find", "Text not found.")

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self.editor.toPlainText()
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        count = text.count(find_text)
        if count == 0:
            QMessageBox.information(self, "Replace All", "Text not found.")
            return
        new_text = text.replace(find_text, replace_text)
        self.editor.setPlainText(new_text)
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences.")


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('QT Notepad')
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.current_file = None

        self._create_actions()
        self._create_menu_bar()

    def _create_actions(self):
        # File
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.save_as_file)

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)

        # Edit
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.editor.redo)

        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.editor.paste)

        self.select_all_action = QAction("Select All", self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.editor.selectAll)

        self.find_replace_action = QAction("Find and Replace", self)
        self.find_replace_action.setShortcut(QKeySequence.Find)
        self.find_replace_action.triggered.connect(self.show_find_replace_dialog)

        # Insert
        self.insert_datetime_cursor = QAction("Insert Date/Time at Cursor", self)
        self.insert_datetime_cursor.setShortcut("Ctrl+D")
        self.insert_datetime_cursor.triggered.connect(self.insert_datetime_cursor_pos)

        self.insert_datetime_top = QAction("Insert Date/Time at Top", self)
        self.insert_datetime_top.triggered.connect(self.insert_datetime_top_pos)

        self.insert_datetime_bottom = QAction("Insert Date/Time at Bottom", self)
        self.insert_datetime_bottom.triggered.connect(self.insert_datetime_bottom_pos)

        self.insert_name = QAction("Insert Name", self)
        self.insert_name.triggered.connect(self.insert_name_func)

        self.insert_signature = QAction("Insert Signature", self)
        self.insert_signature.triggered.connect(self.insert_signature_func)

        # View
        self.fullscreen_action = QAction("Toggle Fullscreen", self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)


        self.zoomIn_action = QAction("Zoom In", self)
        self.zoomIn_action.setShortcut("Ctrl++")
        self.zoomIn_action.triggered.connect(self.zoomIn)

        self.zoomOut_action = QAction("Zoom Out", self)
        self.zoomOut_action.setShortcut("Ctrl+-")
        self.zoomOut_action.triggered.connect(self.zoomOut)

        self.cursor_disable_action = QAction("Disable Cursor", self)
        self.cursor_disable_action.setCheckable(True)
        self.cursor_disable_action.setShortcut("Ctrl+M")
        self.cursor_disable_action.triggered.connect(self.cursor_disable)


    def _create_menu_bar(self):
        menubar = self.menuBar()
        #File Menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        #Edit Menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        edit_menu.addAction(self.find_replace_action)
        #Insert Menu
        insert_menu = menubar.addMenu("Insert")
        insert_menu.addAction(self.insert_datetime_cursor)
        insert_menu.addAction(self.insert_datetime_top)
        insert_menu.addAction(self.insert_datetime_bottom)
        insert_menu.addSeparator()
        insert_menu.addAction(self.insert_name)
        insert_menu.addAction(self.insert_signature)
        #View Menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.fullscreen_action)
        view_menu.addAction(self.zoomIn_action)
        view_menu.addAction(self.zoomOut_action)
        view_menu.addAction(self.cursor_disable_action)
        
        menubar.addMenu("Tools")
        menubar.addMenu("Window")
        menubar.addMenu("Settings")

    # File handling
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open file', '', "Text documents (*.txt);;All files (*.*)")
        if path:
            try:
                with open(path, "r", encoding='utf-8') as file:
                    self.editor.setText(file.read())
                self.current_file = path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error opening file:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding='utf-8') as file:
                    file.write(self.editor.toPlainText())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving file:\n{e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save file', '', "Text documents (*.txt)")
        if path:
            try:
                with open(path, "w", encoding='utf-8') as file:
                    file.write(self.editor.toPlainText())
                self.current_file = path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving file:\n{e}")

    # Dialogs and actions
    def show_find_replace_dialog(self):
        dialog = FindReplaceDialog(self.editor, self)
        dialog.exec()

    def toggle_fullscreen(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    #zoom in and out
    def zoomIn(self):
        font = self.editor.font()
        current_size = font.pointSize()
        if current_size <= 0:
            current_size = 12  # fallback default
        font.setPointSize(current_size + 1)
        self.editor.setFont(font)
    def zoomOut(self):
        font = self.editor.font()
        current_size = font.pointSize()
        if current_size <= 0:
            current_size = 12  # fallback default
        font.setPointSize(current_size - 1)
        self.editor.setFont(font)
    def cursor_disable(self, checked):
        if checked:
            self.editor.setCursorWidth(0)  # Hide cursor
        else:
            self.editor.setCursorWidth(1)  # Show cursor

        

    # Insert methods
    def insert_datetime_cursor_pos(self):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.editor.textCursor().insertText(now)

    def insert_datetime_top_pos(self):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S\n")
        self.editor.setPlainText(now + self.editor.toPlainText())

    def insert_datetime_bottom_pos(self):
        now = "\n" + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.editor.setPlainText(self.editor.toPlainText() + now)

    def insert_name_func(self):
        name = "Your Name Here"
        self.editor.textCursor().insertText(name)

    def insert_signature_func(self):
        signature = "\n\n--\nBest regards,\nYour Name"
        self.editor.textCursor().insertText(signature)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(650, 450)
    window.setMinimumSize(650, 450)
    window.show()
    sys.exit(app.exec())
