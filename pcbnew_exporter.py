import sys
import os

# Adjust the path for packaged environment
if getattr(sys, 'frozen', False):
    kicad_bin_path = os.path.join(sys._MEIPASS, 'KiCad/bin')
else:
    kicad_bin_path = '/usr/bin'  # Default KiCad binary path on Linux

sys.path.append(os.path.join(kicad_bin_path, 'lib/python3/dist-packages'))
import pcbnew
import tkinter as tk
from tkinter import filedialog
from PCBcoilV2 import coilClass

# Get the path to the Temp directory within the project folder
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'Temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_svg(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100)):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def create_board_and_plot(lines, layer, filename):
        board = pcbnew.BOARD()

        for start, end in lines:
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(coil.traceWidth * 1e6))
            track.SetStart(pcbnew.VECTOR2I(int((start[0] + offset[0]) * 1e6), int((-start[1] + offset[1]) * 1e6)))
            track.SetEnd(pcbnew.VECTOR2I(int((end[0] + offset[0]) * 1e6), int((-end[1] + offset[1]) * 1e6)))
            track.SetLayer(layer)
            board.Add(track)

        temp_board_file = os.path.join(TEMP_DIR, f"temp_{filename}.kicad_pcb")
        pcbnew.SaveBoard(temp_board_file, board)

        plot_controller = pcbnew.PLOT_CONTROLLER(board)
        plot_options = plot_controller.GetPlotOptions()
        plot_options.SetOutputDirectory(output_directory)
        plot_options.SetPlotFrameRef(False)
        plot_options.SetAutoScale(False)
        plot_options.SetMirror(False)
        plot_options.SetUseGerberAttributes(False)
        plot_options.SetScale(1)
        plot_options.SetPlotMode(pcbnew.FILLED)
        plot_options.SetPlotViaOnMaskLayer(False)
        plot_options.SetSkipPlotNPTH_Pads(False)
        plot_options.SetSubtractMaskFromSilk(False)
        plot_options.SetFormat(pcbnew.PLOT_FORMAT_SVG)

        plot_controller.SetLayer(layer)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_SVG, f"Generated {filename}")
        plot_controller.PlotLayer()
        plot_controller.ClosePlot()

        logger.info(f"SVG file generated as {output_directory}/{filename}.svg")

    # Generate coil SVG
    coil_filename = f"coil_d{coil.outerDiameter:.1f}_t{coil.traceWidth:.2f}_s{coil.traceSpacing:.2f}"
    create_board_and_plot(coil_line_list, pcbnew.F_Cu, coil_filename)

    # Generate loop antenna SVG if loop_line_list is not empty
    if loop_line_list:
        loop_filename = f"loop_d{coil.loop_diameter:.1f}_t{coil.traceWidth:.2f}"
        create_board_and_plot(loop_line_list, pcbnew.B_Cu, loop_filename)


def initialize_svg_generation(coil, coil_line_list, loop_line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_svg(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100))

def generate_gerber(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add coil tracks
    for line in coil_line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

    # Add loop antenna tracks
    for start, end in loop_line_list:
        add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Plot to Gerber
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()

    plot_options.SetOutputDirectory(output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(True)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    # Plot only the Front Copper layer to Gerber
    plot_controller.SetLayer(pcbnew.F_Cu)
    plot_controller.OpenPlotfile("F_Cu", pcbnew.PLOT_FORMAT_GERBER, "Front Copper Layer")
    plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()
    print(f"Gerber file generated as {output_directory}/F_Cu.gbr")

def initialize_gerber_generation(coil, coil_line_list, loop_line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_gerber(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100))

def generate_dxf(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add coil tracks
    for line in coil_line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

    # Add loop antenna tracks
    for start, end in loop_line_list:
        add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Plot to DXF
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()

    plot_options.SetOutputDirectory(output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    # Set up the DXF plot
    plot_options.SetFormat(pcbnew.PLOT_FORMAT_DXF)

    # Plot the F.Cu (Front Copper) layer
    plot_controller.SetLayer(pcbnew.F_Cu)
    plot_controller.OpenPlotfile("coil", pcbnew.PLOT_FORMAT_DXF, "Generated Coil")
    plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()

    print(f"DXF file generated as {output_directory}/coil.dxf")

def initialize_dxf_generation(coil, coil_line_list, loop_line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_dxf(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100))

def generate_drill(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add coil tracks
    for line in coil_line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

    # Add loop antenna tracks
    for start, end in loop_line_list:
        add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Generate the drill files
    drl_writer = pcbnew.EXCELLON_WRITER(board)
    drl_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)
    drl_writer.SetOptions(False, False, pcbnew.VECTOR2I(0, 0), False)
    drl_writer.SetFormat(True)
    drl_writer.CreateDrillandMapFilesSet(output_directory, True, False)

    print(f"Drill files generated in {output_directory}")

def initialize_drill_generation(coil, coil_line_list, loop_line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_drill(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100))

def export_coil(coil, coil_line_list, export_options):
    for option, var in export_options.items():
        if var.get():
            if option == 'SVG':
                initialize_svg_generation(coil, coil_line_list, [])
            elif option == 'Gerber':
                initialize_gerber_generation(coil, coil_line_list, [])
            elif option == 'DXF':
                initialize_dxf_generation(coil, coil_line_list, [])
            elif option == 'Drill':
                initialize_drill_generation(coil, coil_line_list, [])

def export_loop(coil, loop_line_list, export_options):
    for option, var in export_options.items():
        if var.get():
            if option == 'SVG':
                initialize_svg_generation(coil, [], loop_line_list)
            elif option == 'Gerber':
                initialize_gerber_generation(coil, [], loop_line_list)
            elif option == 'DXF':
                initialize_dxf_generation(coil, [], loop_line_list)
            elif option == 'Drill':
                initialize_drill_generation(coil, [], loop_line_list)