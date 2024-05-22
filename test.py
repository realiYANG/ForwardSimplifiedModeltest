import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class RameyFlowCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ramey Flow Calculator')
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Parameter Input Layout
        param_layout = QVBoxLayout()
        self.params = {}
        param_names = [
            ("Depth 1 (TVD ft)", "depth1"),
            ("Temperature 1 (deg F)", "temp1"),
            ("Depth 2 (TVD ft)", "depth2"),
            ("BHT 2 (Deg F)", "bht2"),
            ("Geothermal Gradient (Deg F/ft)", "geo_gradient"),
            ("Inflow JT Effect", "jt_effect"),
            ("Flow Rate (bopd)", "flow_rate"),
            ("Perforation Depth", "perforation_depth"),
            ("Thermal Diffusivity (sq ft/day)", "thermal_diffusivity"),
            ("Time of Production (days)", "production_time"),
            ("Casing Diameter (inches)", "casing_diameter"),
            ("Fluid Density (gm/cc)", "fluid_density"),
            ("Fluid Specific Heat (Btu/lb DegF)", "fluid_specific_heat"),
            ("Time Function Calculation f(t)", "time_function"),
            ("Relaxation Distance (A)", "relaxation_distance"),
            ("Least Squares Fit to Raw Data", "least_squares_fit"),
            ("Sum of Squares", "sum_of_squares")
        ]

        for label, name in param_names:
            param_row = QHBoxLayout()
            param_label = QLabel(label)
            param_input = QLineEdit()
            param_input.setObjectName(name)
            self.params[name] = param_input
            param_row.addWidget(param_label)
            param_row.addWidget(param_input)
            param_layout.addLayout(param_row)

        main_layout.addLayout(param_layout)

        # Data Input Layout
        data_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Depth", "Geothermal Temperature", "Ramey Temperature", "Measured Temperature", "Difference Squared"
        ])
        data_layout.addWidget(self.table)

        main_layout.addLayout(data_layout)

        # Button Layout
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load Data")
        load_button.clicked.connect(self.load_data)
        calculate_button = QPushButton("Calculate & Plot")
        calculate_button.clicked.connect(self.calculate_and_plot)
        button_layout.addWidget(load_button)
        button_layout.addWidget(calculate_button)

        main_layout.addLayout(button_layout)

        # Matplotlib Figure
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "All Files (*);;CSV Files (*.csv)", options=options)
        if file_name:
            self.read_data(file_name)

    def read_data(self, file_name):
        try:
            data = np.loadtxt(file_name, delimiter=',', skiprows=1)
            self.table.setRowCount(data.shape[0])
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(data[i, j])))
            QMessageBox.information(self, "Data Loaded", "Data loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def calculate_and_plot(self):
        try:
            # 获取输入参数
            depth1 = float(self.params['depth1'].text())
            temp1 = float(self.params['temp1'].text())
            depth2 = float(self.params['depth2'].text())
            bht2 = float(self.params['bht2'].text())
            geo_gradient = float(self.params['geo_gradient'].text())
            jt_effect = float(self.params['jt_effect'].text())
            flow_rate = float(self.params['flow_rate'].text())
            perforation_depth = float(self.params['perforation_depth'].text())
            thermal_diffusivity = float(self.params['thermal_diffusivity'].text())
            production_time = float(self.params['production_time'].text())
            casing_diameter = float(self.params['casing_diameter'].text())
            fluid_density = float(self.params['fluid_density'].text())
            fluid_specific_heat = float(self.params['fluid_specific_heat'].text())
            time_function = float(self.params['time_function'].text())
            relaxation_distance = float(self.params['relaxation_distance'].text())
            least_squares_fit = float(self.params['least_squares_fit'].text())
            sum_of_squares = float(self.params['sum_of_squares'].text())

            # 读取表格中的数据
            row_count = self.table.rowCount()
            depths = []
            measured_temps = []
            for row in range(row_count):
                depth = float(self.table.item(row, 0).text())
                measured_temp = float(self.table.item(row, 3).text())
                depths.append(depth)
                measured_temps.append(measured_temp)

            depths = np.array(depths)
            measured_temps = np.array(measured_temps)

            # 计算地热温度和Ramey Temperature
            geothermal_temps = temp1 + geo_gradient * (depths - depth1)
            ramey_temps = self.calculate_ramey_temperature(
                depths, geothermal_temps, depth1, temp1, depth2, bht2,
                jt_effect, flow_rate, perforation_depth, thermal_diffusivity,
                production_time, casing_diameter, fluid_density, fluid_specific_heat,
                time_function, relaxation_distance
            )
            diff_squared = (measured_temps - ramey_temps) ** 2

            # 更新表格
            for row in range(row_count):
                self.table.setItem(row, 1, QTableWidgetItem(f"{geothermal_temps[row]:.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{ramey_temps[row]:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{diff_squared[row]:.2f}"))

            # 绘制图表
            self.ax.clear()
            self.ax.plot(geothermal_temps, depths, 'g-', label='Geothermal Temperature')
            self.ax.plot(ramey_temps, depths, 'r-', label='Ramey Temperature')
            self.ax.plot(measured_temps, depths, 'k-', label='Measured Temperature')
            self.ax.invert_yaxis()
            self.ax.set_xlabel('Temperature (deg F)')
            self.ax.set_ylabel('Depth (ft)')
            self.ax.legend()
            self.canvas.draw()

            QMessageBox.information(self, "Calculation Complete",
                                    "Calculation and plotting completed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate and plot: {str(e)}")

    def calculate_ramey_temperature(self, depths, geothermal_temps, depth1, temp1, depth2, bht2,
                                    jt_effect, flow_rate, perforation_depth, thermal_diffusivity,
                                    production_time, casing_diameter, fluid_density, fluid_specific_heat,
                                    time_function, relaxation_distance):
        # 示例计算逻辑，实际计算可能需要根据具体公式调整
        ramey_temps = geothermal_temps + jt_effect * (depths - perforation_depth) * flow_rate / (
                    thermal_diffusivity * production_time)
        return ramey_temps

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RameyFlowCalculator()
    ex.show()
    sys.exit(app.exec_())