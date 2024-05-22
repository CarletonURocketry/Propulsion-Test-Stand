from svgelements import SVG, Color
import cairosvg

class svgEdit:
    def __init__(self, file: str) -> None:
        """Class to interface with an SVG file, abnd change colors of paths in the file.

        Args:
            file (str): Filename 
        """
        self.svg = SVG.parse(file) #type: ignore
        return

    def changeColor(self, paths: list[str], color: str) -> None:
        """Function to change the color of the paths in the SVG file.

        Args:
            paths (list[str]): names of the paths to change the color of
            color (str): Color to change the paths to as a XHTML color name or any other format excepted by https://github.com/meerk40t/svgelements?tab=readme-ov-file#color
        """
        for element in self.svg.elements(): #type: ignore
            if element.id in paths: #type: ignore
                element.fill = Color(color)
        
        self.svg.write_xml("UI_PID.svg") #type: ignore

        cairosvg.svg2png(url="UI_PID.svg", write_to="UI_PID.png") #type: ignore

        return