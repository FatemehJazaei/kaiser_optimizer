from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout, QDialog,  QLabel, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal, Qt 
from PyQt6.QtGui import QIcon
from PyQt6 import QtGui
from ui import Ui_MainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import optimizer as opt
import sys
import os

class DescriptionAboutUs(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Us")
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon('images/logo.png'))
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # margin around the content
        layout.setSpacing(15)

        # About text with formatting
        description_text = """
        <h2 style="color: #2E4053;">Quantum Remote Sensing Metrology Lab</h2>
        <p style="font-size: 11pt; line-height: 1.4;">
            Our research group focuses on developing advanced techniques in quantum remote sensing and 
            high-precision metrology. We combine modern signal processing methods with cutting-edge 
            quantum technologies to improve measurement accuracy and data interpretation.
        </p>
        <p style="font-size: 10pt; font-style: italic; color: gray;">
            Thank you for using our software.
        </p>
        """

        description = QLabel(description_text)
        description.setWordWrap(True)
        description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        description.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(description)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.setStyleSheet("                QPushButton {\n"
"                        background-color: white;  \n"
"                        color: #282B6A;\n"
"                        border-radius: 8px;\n"
"                        padding: 6px 12px;\n"
"                        font-weight: bold;\n"
"                        font-size: 14px;\n"
"                        border: 2px solid #282B6A;\n"
"                }\n"
"\n"
"                QPushButton:hover {\n"
"                        background-color: #E0E0FF; \n"
"                        color: #1A1D4F; \n"
"                }")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)



class DescriptionAboutSoftware(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Software")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon('logo.png'))
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()

        # HTML text
        description_text = """
        <h3>About This Software</h3>
        <p>This software is a tool for optimizing <b>Kaiser windows</b> using the <i>Firefly Algorithm</i>, a bio-inspired optimization method. 
        It takes a standard Kaiser window as input and returns an optimized version with the same mainlobe width (MW) and lower peak sidelobe ratio (PSLR).</p>

        <b>Input Parameter Ranges:</b>
        <ul>
            <li>Alpha (α): 0 &ndash; 1</li>
            <li>Gamma (γ): 0 &ndash; 10</li>
            <li>Beta (β): 0 &ndash; 100</li>
        </ul>

        <p>You can use the <b>Export</b> button to save:
        <ul>
            <li>The optimized window values (.txt)</li>
            <li>Time-domain and frequency-domain plots (.png)</li>
        </ul>
        </p>

        <p style="font-size: 10pt; font-style: italic;">
        Based on the paper:<br>
        "A Novel Optimization Framework for Classic Windows Using Bio-Inspired Methodology"<br>
        <i>Zhi-huo Xu, Yun-kai Deng, Yu Wang</i>
        </p>
        """

        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        

        layout.addWidget(description_label)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("                QPushButton {\n"
"                        background-color: white;  \n"
"                        color: #282B6A;\n"
"                        border-radius: 8px;\n"
"                        padding: 6px 12px;\n"
"                        font-weight: bold;\n"
"                        font-size: 14px;\n"
"                        border: 2px solid #282B6A;\n"
"                }\n"
"\n"
"                QPushButton:hover {\n"
"                        background-color: #E0E0FF; \n"
"                        color: #1A1D4F; \n"
"                }")
        btn_close.setFixedWidth(100)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class WorkerThread(QThread):

        progress = pyqtSignal(float)
        finished = pyqtSignal(str)
        set_input = pyqtSignal(float, float, float, float, float, float, object, int)
        plot_window = pyqtSignal(object, object, object)


        def __init__(self, window_lenght, beta, freqResolution, num_firefly, iteration, gamma, alpha, lamda):
                super().__init__()
                self.window_lenght = window_lenght
                self.beta = beta
                self.freqResolution = freqResolution
                self.num_firefly = num_firefly
                self.iteration = iteration
                self.gamma = gamma
                self.alpha = alpha
                self.lamda = lamda
                self._is_running = True
                            
        def run(self): 
                firefly_algorithm = opt.FireFly(self, self.window_lenght, self.beta, self.freqResolution, self.num_firefly, self.iteration, self.gamma, self.alpha, self.lamda)
                window, window_optimized = firefly_algorithm.optimizer()
                if self._is_running:
                        mw, pslr, pl= firefly_algorithm.calculate_MW_PSLR_PL(window)
                        mw_optimized, pslr_optimized, pl_optimized = firefly_algorithm.calculate_MW_PSLR_PL(window_optimized)
                        self.set_input.emit(mw_optimized, pslr_optimized, pl_optimized, mw, pslr, pl, window_optimized, self.window_lenght)
                        self.plot_window.emit(firefly_algorithm, window, window_optimized)
                        self.finished.emit("Processing completed.")
                else:
                        self.finished.emit("Process stopped by user.")
          
        def stop(self):
                self._is_running = False

              

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        doubleValidatorAlpha = QtGui.QDoubleValidator(0.0, 1, 2)
        doubleValidatorAlpha.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.textEdit_Alpha.setValidator(doubleValidatorAlpha)
        self.ui.textEdit_Alpha.setText("0.1")

        doubleValidatorlambda = QtGui.QDoubleValidator()
        doubleValidatorlambda.setBottom(0.0) 
        doubleValidatorlambda.setDecimals(2)
        doubleValidatorlambda.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.textEdit_lambda.setValidator(doubleValidatorlambda)
        self.ui.textEdit_lambda.setText("10")

        self.ui.intvalid = QtGui.QIntValidator()
        self.ui.textEdit_Iteration.setValidator(self.ui.intvalid)
        self.ui.textEdit_Iteration.setText("100")
        self.ui.textEdit_Fireflies.setValidator(self.ui.intvalid)
        self.ui.textEdit_Fireflies.setText("100")
        self.ui.textEdit_freqResolution.setValidator(self.ui.intvalid)
        self.ui.textEdit_freqResolution.setText("1024")
        doubleValidatorGamma = QtGui.QDoubleValidator(0.0, 10, 2)
        doubleValidatorGamma.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.textEdit_Gamma.setValidator(doubleValidatorGamma)
        self.ui.textEdit_Gamma.setText("0.15")
        self.ui.textEdit_window_length.setValidator(self.ui.intvalid)
        self.ui.textEdit_window_length.setText("64")
        doubleValidator = QtGui.QDoubleValidator(0.0, 100, 2)
        doubleValidator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.ui.textEdit_Beta.setValidator(doubleValidator)
        self.ui.textEdit_Beta.setText("2.25")
        self.ui.stopButton.hide()
        self.ui.textEdit_mw_original.setReadOnly(True)
        self.ui.textEdit_pslr_original.setReadOnly(True)
        self.ui.textEdit_mw_optimized.setReadOnly(True)
        self.ui.textEdit_pslr_optimized.setReadOnly(True)
        self.ui.textEdit_pl_optimized.setReadOnly(True)
        self.ui.textEdit_pl_original.setReadOnly(True)
        self.ui.textEdit_final_window.setReadOnly(True)

        self.ui.tab_time_domain_box = QVBoxLayout(self.ui.tab_time_domain)
        self.ui.tab_frequancy_response_box = QVBoxLayout(self.ui.tab_frequancy_response)
        self.ui.canvas_time_domain = MplCanvas()
        self.ui.tab_time_domain_box.addWidget(self.ui.canvas_time_domain)
        self.ui.canvas_frequancy_response = MplCanvas()
        self.ui.tab_frequancy_response_box.addWidget(self.ui.canvas_frequancy_response)

        self.ui.textEdit_window_length.editingFinished.connect(self.check_even_or_odd)
        self.ui.exportButton.clicked.connect(self.export_func)
        self.ui.optimizeButton.clicked.connect(self.kaiser_optimizer)
        self.ui.resetButton.clicked.connect(self.reset_func)
        self.ui.stopButton.clicked.connect(self.stop)
        self.ui.about_us_Button.clicked.connect(self.show_about_us)
        self.ui.about_Software_Button.clicked.connect(self.show_about_software)



    def check_even_or_odd(self):

        text = self.ui.textEdit_window_length.text()
        if text.isdigit():
                value = int(text)
                if value % 2 == 1:
                        self.ui.textEdit_window_length.setStyleSheet("""
                                QLineEdit {
                                background-color: #EEE8F0;
                                border: 2px solid red;
                                border-radius: 3px;
                                padding: 3px;
                                color: #333;
                                font-size: 12px;
                                }
                        """)
                else:
                        self.ui.textEdit_window_length.setStyleSheet("""
                                QLineEdit {
                                background-color: #EEE8F0;
                                border: 1px solid #999;
                                border-radius: 3px;
                                padding: 3px;
                                color: #333;
                                font-size: 12px;
                                }
                        """)

    def set_input(self, mw_optimized, pslr_optimized, pl_optimized, mw, pslr, pl, window_optimized, window_lenght):

        self.ui.textEdit_mw_optimized.setText(str(mw_optimized))
        self.ui.textEdit_pslr_optimized.setText(str(pslr_optimized))
        self.ui.textEdit_pl_optimized.setText(str(pl_optimized))
        self.ui.textEdit_mw_original.setText(str(mw))
        self.ui.textEdit_pslr_original.setText(str(pslr))
        self.ui.textEdit_pl_original.setText(str(pl))
        
        if( window_lenght != 0):
                window_optimized_str =  np.array2string(window_optimized[:window_lenght], precision=4, threshold=64)
                self.ui.textEdit_final_window.setPlainText(str(window_optimized_str))
        else:
                self.ui.textEdit_final_window.setPlainText("")

    def check_input(self, window_lenght, beta, freqResolution, num_firefly, iteration, gamma, alpha):

        error_text = ""
        error_count = 0

        if alpha == 0:
                error_count +=1
                error_text = str(error_count) + "- " + "alpha can not be ziro. "                        
        if gamma == 0:
                error_count +=1
                error_text =  error_text + str(error_count) + "- " + "gamma can not be ziro. "
        if iteration == 0:
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "iteration can not be ziro. "
        if num_firefly == 0:
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "Number of firefly can not be ziro. "
        if window_lenght == 0 :
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "window_lenght can not be ziro. "
        if window_lenght % 2 == 1 :
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "window_lenght can not be odd. "
        if beta == 0:
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "beta can not be ziro. "
        if freqResolution == 0:
                error_count +=1
                error_text = error_text + str(error_count) + "- " + "freqResolution can not be ziro. "

        if error_count != 0:
                error_text = str(error_count) + " Error found: " + error_text
                self.ui.label_Error_2.setText(error_text)
                return False
        else:  
                return True

    def plot_window(self, firefly_algorithm, window_standard, window_optimized):

        self.plot_tab1(firefly_algorithm, window_standard, window_optimized, self.ui.canvas_time_domain)

        self.plot_tab2(firefly_algorithm, window_standard, window_optimized,  self.ui.canvas_frequancy_response)

    def plot_tab1(self, firefly_algorithm, window_standard, window_optimized,  canvas):  

        canvas.figure.clf()
        canvas.ax = canvas.figure.add_subplot(111)
        canvas.ax.plot(
            window_standard,
            label=f"Kaiser Window (β = {firefly_algorithm.beta})",
            color="blue"
            )
        canvas.ax.plot(
            window_optimized,
            label=f"Optimized Window ",
            color="red"
            )
        canvas.ax.set_xlabel("Sample index")
        canvas.ax.set_ylabel("Amplitude")
        canvas.ax.legend()
        canvas.ax.grid(True)
        canvas.figure.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
        canvas.draw()

    def plot_tab2(self, firefly_algorithm, window_standard, window_optimized, canvas):

        freq, H_window_standard = firefly_algorithm.calculate_H(window_standard)
        freq, H_window_optimized = firefly_algorithm.calculate_H(window_optimized)

        canvas.figure.clf()
        canvas.ax = canvas.figure.add_subplot(111)
        canvas.ax.plot(
            freq,
            H_window_standard,
            label=f"Kaiser Window (β = {firefly_algorithm.beta})",
            color="blue"
            )
        canvas.ax.plot(
            freq,
            H_window_optimized,
            label=f"Optimized Window ",
            color="red"
            )
                
        canvas.ax.set_xlabel("Sample index")
        canvas.ax.set_ylabel("Magnitude [dB]")
        canvas.ax.legend()
        canvas.ax.grid(True)
        canvas.figure.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
        canvas.draw()

    def reset_func(self):

        self.ui.canvas_time_domain.figure.clf()
        self.ui.canvas_frequancy_response.figure.clf()
        self.ui.textEdit_Alpha.setText("0.1")
        self.ui.textEdit_Iteration.setText("100")
        self.ui.textEdit_Gamma.setText("0.15")
        self.ui.textEdit_Fireflies.setText("100")
        self.ui.textEdit_Beta.setText("2.25")
        self.ui.textEdit_freqResolution.setText("1024")
        self.ui.textEdit_lambda.setText("10")
        self.set_input(0, 0, 0, 0, 0, 0, 0, 0)
        self.ui.canvas_time_domain.draw()
        self.ui.canvas_frequancy_response.draw()

    def kaiser_optimizer(self):

        self.ui.optimizeButton.setEnabled(False)
        self.ui.stopButton.show()
        self.ui.label_Error_2.setText("Checking...")

        alpha = float(self.ui.textEdit_Alpha.text())
        gamma = float(self.ui.textEdit_Gamma.text())
        iteration = int(self.ui.textEdit_Iteration.text())
        num_firefly = int(self.ui.textEdit_Fireflies.text())
        window_lenght = int(self.ui.textEdit_window_length.text())
        beta = float(self.ui.textEdit_Beta.text())
        lamda = float(self.ui.textEdit_Beta.text())
        freqResolution = int(self.ui.textEdit_freqResolution.text())

        if self.check_input(window_lenght, beta, freqResolution, num_firefly, iteration, gamma, alpha):
                
            self.thread = WorkerThread(window_lenght, beta, freqResolution, num_firefly, iteration, gamma, alpha, lamda)
            self.thread.progress.connect(self.update_progress)
            self.thread.finished.connect(self.task_finished)
            self.thread.set_input.connect(self.set_input)
            self.thread.plot_window.connect(self.plot_window)
            self.thread.start()

    def update_progress(self, value):
        self.ui.label_Error_2.setText(f"Processing: {value}%")

    def stop(self):
        self.thread.stop()
        

    def task_finished(self, msg):
        self.ui.label_Error_2.setText(msg)
        self.ui.stopButton.hide()
        self.ui.optimizeButton.setEnabled(True)

    def export_func(self):
        try:
                text = self.ui.textEdit_final_window.toPlainText()
                if text.strip():
                        save_dir = os.getenv("SAVE_DIR", "./")
                        filename, _ = QFileDialog.getSaveFileName(
                                        parent=self,
                                        caption="Save Text File",
                                        #directory=f"{save_dir}/window.txt",
                                        directory=os.path.join(save_dir, "window.txt"),
                                        filter="Text Files (*.txt);;All Files (*)",
                                        options=QFileDialog.Option.DontUseNativeDialog
                                )
                        
                        imgname, _ = QFileDialog.getSaveFileName(
                                        parent=self,
                                        caption="Save Image Files (without extension)",
                                        #directory=f"{save_dir}/plot",
                                        directory=os.path.join(save_dir, "plot"),
                                        filter="PNG Image (*.png);;All Files (*)",
                                        options=QFileDialog.Option.DontUseNativeDialog
                                )
        
                        if os.access(os.path.dirname(imgname), os.W_OK):
                                
                                if filename:
                                        with open(filename, 'w') as file:
                                                file.write(text)
                                if imgname:
                                        if self.ui.canvas_time_domain and self.ui.canvas_frequancy_response:
                                                if not imgname.lower().endswith(".png"):
                                                        imgname += ".png"
                                                self.ui.canvas_time_domain.fig.savefig(imgname.replace(".png", "_time.png"), dpi=300)
                                                self.ui.canvas_frequancy_response.fig.savefig(imgname.replace(".png", "_freq.png"), dpi=300)
                                                QMessageBox.information(self, "Save Files", "ٌWindow and Plots saved successfully!") 
                        else:
                                QMessageBox.critical(self, "Save File", f"Saving failed:\n{str(e)}")
                else:
                        self.ui.label_Error_2.setText("Nothing found to save.")
        except Exception as e:
                QMessageBox.critical(self, "Save File", f"Saving failed:\n{str(e)}")


    def show_about_us(self):
                dialog = DescriptionAboutUs()
                dialog.exec()
        
    def show_about_software(self):
                dialog = DescriptionAboutSoftware()
                dialog.exec()

app = QApplication(sys.argv)
window = MyWindow()
window.setWindowIcon(QIcon('logo.png'))
window.show()
sys.exit(app.exec())
