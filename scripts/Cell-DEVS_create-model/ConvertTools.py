# Tools for converting 2D models into 3D models
# Thomas Roller

import json
from GeneralTools import GeneralTools

# Tools to bring the 2D model into 3D
class ConvertTools:

    # Create the head of the JSON file
    @staticmethod
    def createHead (length, width, modelConfig):
        coords = [length, width]
        if (modelConfig["height"] > 1):
            coords += [modelConfig["height"]]

        data = {
            "scenario" : {
                "shape" : coords,
                "wrapped" : False,
                "default_delay" : "transport",
                "default_cell_type" : "CO2_cell",
                "default_state" : {
                    "counter": -1,
                    "concentration" : 500,
                    "type" : -100
                },
            "default_config" : {
                    "CO2_cell" : {
                        "conc_increase" : 143.2,
                        "base" : 500,
                        "resp_time" : 5,
                        "window_conc" : 400,
                        "vent_conc" : 300
                    }
                },
                "neighborhood": [
                    {
                        "type" : modelConfig["neighbourhood"],
                        "range" : modelConfig["range"]
                    }
                ]
            },
            "cells" : []
        }
        return data

    # Determines if a cell with the given coordinates is already in the dictionary
    @staticmethod
    def containsCell (cells, coords):
        for cell in cells:
            if (cell["cell_id"] == coords):
                return True
        return False

    # Get the heights at which to place each cell type
    # Returns a list where the first element is the lowest cell it may appear in and
    # the second element is one above the highest cell it may appear in
    @staticmethod
    def getHeights (height, heights, cellType):
        # WALL
        if (cellType == -300):
            return [1, height - 2]  # keep in mind that HEIGHT is dirived from the shape
        
        # DOOR
        elif (cellType == -400):
            return [1, heights["door_top"]]

        # WINDOW
        elif (cellType == -500):
            return [heights["window"]["bottom"], heights["window"]["top"]]

        # VENTILATION
        elif (cellType == -600):
            return [heights["vent"], heights["vent"]]

        # WORKSTATION or CO2_SOURCE
        elif (cellType == -700 or cellType == -200):
            return [heights["workstation"], heights["workstation"]]

        # Otherwise
        else:
            return [0, 0]  # for loop does no iterations

    # Extent each coordinate in the positive Z direction
    # This brings the 2D model into 3D space
    @staticmethod
    def getExtendedCells (modelConfig, cells):
        allCells = []
        for cell in cells:
            # Add given cells at appropriate heights
            if (modelConfig["walls_only"] and cell["state"]["type"] != -300):
                continue

            heights = ConvertTools.getHeights(modelConfig["height"], modelConfig["heights"], cell["state"]["type"])

            # Go through all Z values (floor and ceiling included)
            for z in range(0, modelConfig["height"]):
                # If Z value is within cell's permitted values, add wall cell at that coordinate
                if (z in range(heights[0], heights[1] + 1)):
                    allCells.append(GeneralTools.makeCell(
                        cell["cell_id"] + [z],
                        cell["state"]["concentration"],
                        cell["state"]["type"],
                        cell["state"]["counter"]
                    ))
                # If Z value is not within cell's permitted values AND that cell requires walls
                # above/below (DOOR and WINDOW), add wall cell at that coordinate
                elif (cell["state"]["type"] == -400 or cell["state"]["type"] == -500):
                    allCells.append(GeneralTools.makeCell(
                        cell["cell_id"] + [z],
                        0,
                        -300,
                        -1
                    ))
        return allCells

    # Add a floor and ceiling
    # This is fairly simple as it just fills in the entire
    # length by width rectangle at the floor and ceiling levels
    @staticmethod
    def addFloorCeiling (width, length, height, cells):
        for w in range (0, width):
            for l in range (0, length):
                if (not ConvertTools.containsCell(cells, [w, l, 0])):
                    cells.append(GeneralTools.makeCell([w, l, 0], 0, -300, -1))  # floor
                if (not ConvertTools.containsCell(cells, [w, l, height - 1])):
                    cells.append(GeneralTools.makeCell([w, l, height - 1], 0, -300, -1))  # ceiling
        return cells

    # Combines the head and the cells
    @staticmethod
    def createStructure (head, cells):
        head["cells"] = cells
        return head

    # Returns a JSON string representation of the dictionary
    @staticmethod
    def getString (data):
        return json.dumps(data, indent=4)