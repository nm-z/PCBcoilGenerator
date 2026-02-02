# CLAUDE.md - AI Assistant Guide for Coilgen V3

## Project Overview

Coilgen V3 is a specialized Python desktop application for designing and generating **SansEC (Sans Electrical Connection) coil patterns** for wireless sensors. SansEC is an innovative technology developed by NASA's Langley Research Center that enables self-resonating planar coils without electrical connections for wireless sensing applications including damage detection, strain measurement, and smart aircraft skins.

**Key capabilities:**
- Interactive coil design with real-time visualization
- Multi-shape support (square, circle, hexagon, octagon)
- Multiple inductance calculation formulas (Wheeler, Monomial, Current Sheet)
- Multi-layer PCB support with coupling calculations
- Export to industry-standard formats (SVG, Gerber, DXF)
- Resonant frequency estimation via linear regression model

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| Primary UI | Tkinter |
| Visualization | Pygame |
| Math/Calculations | NumPy |
| PCB Export | KiCad pcbnew module |
| DXF Export | dxfwrite |
| Build System | PyInstaller |
| CI/CD | GitHub Actions |

## Directory Structure

```
Coilgen-V3/
├── PCBcoilV2.py              # Main entry point, core calculations, shape classes
├── tkinter_coil_gui.py       # Tkinter parameter input GUI
├── pygameRenderer.py         # Pygame rendering engine (viewport, zoom, grid)
├── pygameUI.py               # Keyboard/mouse event handling
├── pcbnew_exporter.py        # Export functionality (SVG/Gerber/DXF via KiCad)
├── matplotlibRenderer.py     # Optional 3D flux visualization
├── run_with_console.py       # Cross-platform console launcher
├── run_PCBcoilV2.bat         # Windows batch runner
├── requirements.txt          # Python dependencies
├── PCBcoilV2.spec            # PyInstaller build configuration
├── .env                      # KiCad PYTHONPATH configuration
├── .github/
│   └── workflows/
│       └── windows_build.yml # GitHub Actions CI/CD
├── fancy/
│   ├── keyboard_fancy.py     # Keyboard visualization metadata
│   └── keyBindLegend.png     # Keyboard legend image
└── Temp/                     # Temporary KiCad PCB files
```

## Core Modules and Their Purposes

### PCBcoilV2.py (Main Entry Point)
- **coilClass**: Main data structure holding all coil parameters and calculation methods
- **Shape classes**: `squareSpiral`, `circularSpiral`, `hexagonSpiral`, `octagonSpiral`
- **Base class**: `_shapeBaseClass` and `NthDimSpiral` for polygon shapes
- **Key methods**: `calcPos()`, `calcLength()`, `calcInductance()`, `calcResonantFrequency()`

### tkinter_coil_gui.py
- `CoilParameterGUI`: Main Tkinter form for parameter input
- Handles: turns, diameter, trace width, clearance, layers, copper thickness
- Shape/formula dropdowns, export options, frequency estimation

### pygameRenderer.py
- `pygameWindowHandler`: Window management, events, framerate control
- `pygameDrawer`: Rendering pipeline for coils, grid, background
- Coordinate transformation between pixel and real-world units

### pygameUI.py
- Event handling for keyboard shortcuts and mouse interactions
- Parameter adjustment via keyboard (see Key Bindings below)

### pcbnew_exporter.py
- KiCad pcbnew integration for PCB layout generation
- Functions: `add_track()`, `generate_loop_antenna_with_pads_2_layer()`
- Plot output via `PLOT_CONTROLLER` for SVG/Gerber formats

## Development Commands

### Running the Application
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Run main application
python PCBcoilV2.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Building Executable
```bash
pyinstaller PCBcoilV2.spec
# Output: dist/Coilgen_V3.6_3.exe
```

### Environment Setup
The `.env` file must point to KiCad's Python packages for pcbnew module access:
```
PYTHONPATH=/path/to/kicad/lib/python3/site-packages
```

## Code Conventions

### Naming
- **Classes**: PascalCase (e.g., `coilClass`, `squareSpiral`, `pygameDrawer`)
- **Functions**: Mixed camelCase/snake_case (e.g., `calcPos()`, `add_track()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `magneticConstant`, `TEMP_DIR`)

### Type Hints
Type hints are used throughout:
```python
def calcPos(itt: int|float, diam: float, ...) -> tuple[float, float]:
```

### Shape Class Pattern
All shapes inherit from `_shapeBaseClass` and implement:
```python
@staticmethod
def calcPos(itt, diam, traceWidth, clearance) -> tuple[float, float]

@staticmethod
def calcLength(itt, diam, traceWidth, clearance) -> float

stepsPerTurn: int  # Number of sides (4 for square, 6 for hexagon, etc.)
formulaCoefficients: dict  # Wheeler/Monomial formula constants
```

### Export Filename Encoding
Exported files encode all parameters in the filename:
```
SQ_di30_tu10_wi500_cl200_cT35_La2_Pt1600_Re45_In12345.dxf
│  │   │   │    │     │    │   │     │    │
│  │   │   │    │     │    │   │     │    └─ Inductance (μH×1e-3)
│  │   │   │    │     │    │   │     └────── Resistance (mΩ)
│  │   │   │    │     │    │   └──────────── PCB thickness
│  │   │   │    │     │    └─────────────── Layers
│  │   │   │    │     └──────────────────── Copper thickness
│  │   │   │    └────────────────────────── Clearance
│  │   │   └─────────────────────────────── Trace width
│  │   └─────────────────────────────────── Turns
│  └─────────────────────────────────────── Diameter
└────────────────────────────────────────── Shape
```

## Key Data Flow

```
User Input (Tkinter/Pygame)
    ↓
update_coil_params(params)
    ↓
coilClass.__init__() + calculations
    ├─ calcInductance()
    ├─ calcTotalResistance()
    ├─ calcResonantFrequency()
    └─ renderAsCoordinateList() → [(x,y), ...]
    ↓
pygameDrawer.drawLineList(formattedLineLists)
    ↓
Display to Pygame Window
    ↓
(Optional) Export via pcbnew_exporter
    ├─ generate_svg()
    ├─ generate_gerber()
    └─ generate_dxf()
    ↓
Output files
```

## Keyboard Shortcuts (Pygame)

| Key | Action |
|-----|--------|
| `-`/`=` | Decrease/increase turns |
| `[`/`]` | Decrease/increase diameter |
| `;`/`'` | Decrease/increase trace width |
| `.`/`/` | Decrease/increase clearance |
| `u`/`i` | Decrease/increase copper thickness |
| `k`/`l` | Decrease/increase layer count |
| `m`/`,` | Decrease/increase PCB thickness |
| `9`/`0` | Change shape |
| `o`/`p` | Change formula |
| `s` | Save to file |
| `z` | Toggle zoom |
| `g` | Toggle grid |
| `h` | Show key binding legend |

## Inductance Formulas

The application implements three inductance estimation methods:

1. **Wheeler Formula** (default) - Fast empirical approximation
2. **Monomial Formula** - Polynomial fit to measurement data
3. **Current Sheet Formula** - More accurate for coupled layers

## Testing

**Current state**: No formal test suite exists. Testing is done manually via:
- Pygame visualization for real-time feedback
- Export validation (SVG/Gerber/DXF file inspection)
- Console output with colorama for visual debugging

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/windows_build.yml`):
1. Triggers on push to main
2. Sets up Python 3.12
3. Installs dependencies + PyInstaller
4. Builds executable with PyInstaller
5. Uploads artifact

## Common AI Assistant Tasks

### Adding a New Coil Shape
1. Create new class inheriting from `NthDimSpiral` or `_shapeBaseClass` in `PCBcoilV2.py`
2. Implement `calcPos()` and `calcLength()` static methods
3. Define `stepsPerTurn` and `formulaCoefficients`
4. Add to shape selection in `tkinter_coil_gui.py`
5. Update keyboard shortcuts in `pygameUI.py` if needed

### Modifying Export Functionality
- Edit `pcbnew_exporter.py`
- Key functions: `add_track()`, `generate_loop_antenna_with_pads_2_layer()`
- Uses KiCad's pcbnew Python API

### Updating UI Parameters
- Tkinter form: `tkinter_coil_gui.py` (`CoilParameterGUI` class)
- Pygame shortcuts: `pygameUI.py`

### Physics/Calculation Changes
- Core calculations in `PCBcoilV2.py`
- Look for `calcInductance_singleLayer_*` functions
- Multi-layer coupling in `coilClass.calcMultilayerCoupling()`

## Dependencies

From `requirements.txt`:
- numpy - Mathematical calculations
- pygame - Real-time visualization
- dxfwrite - DXF file export
- pandas, openpyxl - Data handling
- opencv-python - Image processing
- matplotlib - 3D plotting
- KicadModTree - KiCad integration

**External requirement**: KiCad 8.0+ must be installed for pcbnew module access.

## Files to Ignore (from .gitignore)

- `.vscode/`, `.idea/` - Editor configs
- `__pycache__/`, `*.py[cod]` - Python bytecode
- `*.dxf`, `*.xlsx`, `*.png` - Generated outputs (except keyBindLegend.png)
- `*.spec` - PyInstaller specs

## Important Notes for AI Assistants

1. **KiCad Dependency**: The pcbnew module requires KiCad installation. Export functionality will fail without it.

2. **Coordinate Systems**: The codebase uses millimeters for real-world units. pcbnew uses nanometers internally (`pcbnew.FromMM()` for conversion).

3. **Shape Polymorphism**: New shapes should follow the existing pattern - inherit from base class, implement required static methods.

4. **No Formal Tests**: Be cautious with refactoring. Verify changes manually through visualization.

5. **Console Output**: Uses colorama for colored output. Check console for debug information.

6. **Temp Files**: Temporary KiCad files are stored in `Temp/` directory.

7. **Attribution**: The Python calculations and Pygame rendering are based on the [PCBcoilGenerator](https://github.com/thijses/PCBcoilGenerator) project by thijses.
