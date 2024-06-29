from svgelements import SVG, Color # type: ignore
import cairosvg # type: ignore

class svgEdit:
    def __init__(self, file: str) -> None:
        """Class to interface with an SVG file, abnd change colors of paths in the file.

        Args:
            file (str): Filename 
        """
        self.svg = SVG.parse(file) #type: ignore
        return

    def returnStr(self) -> bytes: #type: ignore
        """Function to return the SVG file as a string.

        Returns:
            bytes: SVG file as a string
        """

        self.svg.write_xml("UI_PID.svg") #type: ignore

        return cairosvg.svg2svg(url="UI_PID.svg") #type: ignore

    def changeColor(self, paths: list[str], color: str) -> bytes:
        """Function to change the color of the paths in the SVG file.

        Args:
            paths (list[str]): names of the paths to change the color of
            color (str): Color to change the paths to as a XHTML color name or any other format excepted by https://github.com/meerk40t/svgelements?tab=readme-ov-file#color
        """
        for element in self.svg.elements(): #type: ignore
            if element.id in paths: #type: ignore
                element.fill = Color(color)
        
        self.svg.write_xml("UI_PID.svg") #type: ignore

        #print(type(cairosvg.svg2svg(url="UI_PID.svg")))

        return cairosvg.svg2svg(url="UI_PID.svg") #type: ignore