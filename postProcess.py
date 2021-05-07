from os import walk, rename, mkdir
from os.path import join
import logging
import io
import sys


class PostProcess():
    def __init__(self, debugMode: bool = False, simulationMode: bool = False, logLevel=logging.WARN) -> None:
        self.DEBUG_MODE = debugMode
        self.SIMULATION_MODE = simulationMode

        self.logger = logging.getLogger()
        self.logger.setLevel(logLevel)
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t\t%(message)s')

        output_file_handler = logging.FileHandler("output.log")
        output_file_handler.setFormatter(formatter)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        
        self.logger.addHandler(output_file_handler)
        self.logger.addHandler(stdout_handler)

    def renameFiles(self, baseDirectory: str) -> None:
        dirPath, dirNames, fileNames = next(walk(baseDirectory))
        for fileName in fileNames:
            innerFile = join(dirPath, fileName)
            # if "." not in innerFile:
            if not innerFile.endswith(".html"):
                if self.DEBUG_MODE:
                    self.logger.warning("Renaming: {} => {}".format(
                        innerFile, innerFile+".html"))
                if not self.SIMULATION_MODE:
                    rename(innerFile, innerFile+".html")

        for dirName in dirNames:
            inner = join(dirPath, dirName)
            if self.DEBUG_MODE:
                self.logger.info("Directory: {}".format(inner))
            self.renameFiles(inner)

    def moveFiles(self, baseDirectory: str) -> None:
        dirPath, dirNames, fileNames = next(walk(baseDirectory))

        for fileName in fileNames:
            innerFile = join(dirPath, fileName)
            # if ".html" in innerFile:
            if "index" not in innerFile:
                if self.DEBUG_MODE:
                    self.logger.warning("Moving: {} => {}".format(innerFile, join(
                        innerFile.replace(".html", ""), "index.html")))
                if not self.SIMULATION_MODE:
                    mkdir(innerFile.replace(".html", ""))
                    rename(innerFile, join(
                        innerFile.replace(".html", ""), "index.html"))

        for dirName in dirNames:
            inner = join(dirPath, dirName)
            if self.DEBUG_MODE:
                self.logger.info("Directory: {}".format(inner))
            self.moveFiles(inner)

    def changeURL(self, baseDirectory: str, changeFrom: str, changeTo: str) -> None:
        dirPath, dirNames, fileNames = next(walk(baseDirectory))

        for fileName in fileNames:
            innerFile = join(dirPath, fileName)
            if self.DEBUG_MODE:
                self.logger.info("Reading: {}".format(innerFile))
            if not self.SIMULATION_MODE:
                with io.open(innerFile, encoding="utf-8") as htmlFile:
                    fileContent = htmlFile.read()

            if self.SIMULATION_MODE:
                self.logger.info("SIMULATION MODE: Skipping read: {}".format(innerFile))
                continue

            if changeFrom in fileContent:
                if self.DEBUG_MODE:
                    self.logger.warning("Found instance of \"{}\" in {} Replacing wit with \"{}\".".format(
                        changeFrom, innerFile, changeTo))
                if not self.SIMULATION_MODE:
                    fileContent = fileContent.replace(changeFrom, changeTo)

            if not self.SIMULATION_MODE:
                with io.open(innerFile, "w", encoding="utf-8") as htmlFile:
                    htmlFile.write(fileContent)

        for dirName in dirNames:
            inner = join(dirPath, dirName)
            if "wp-" in inner:
                continue
            if self.DEBUG_MODE:
                self.logger.info("Directory: {}".format(inner))
            self.changeURL(inner, changeFrom, changeTo)


if __name__ == "__main__":
    processor = PostProcess(True, False, logging.DEBUG)
    processor.renameFiles("company")
    processor.moveFiles("company")

    
    fromString = "rel='dns-prefetch' href='//authorised-customer-care.com'"
    toString = "rel='dns-prefetch' href='//authorised-customer-care.com'"
    processor.changeURL(".", fromString, toString)
    processor.changeURL("company", "http://localhost:4009/", "https://authorised-customer-care.com/")
    # processor.changeURL("products", fromString, toString)
    # processor.changeURL("brands", fromString, toString)
    # processor.changeURL("company", fromString, toString)
    # processor.changeURL("product", fromString, toString)
