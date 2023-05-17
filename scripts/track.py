## This script is used to run a particle flow simulation and track the results using MLflow
##
## Usage:
## python track.py <experiment> <outputDirectory> <datFile> --runShell <True/False> --executable <executableName> --args <comma separated extra arguments>
##
## Examples:
## python3 track.py fluid "/media/HDD/thivin/ITC/Output/Siminhale_Fluid_Solutions" "tnse3d.dat"
## python3 track.py particle "/media/HDD/thivin/ITC/Output/Siminhale_Particle_Solutions" "tnse3d.dat" --args "1000,../Siminhale_Fluid_Solutions/"

import os
import sys
import mlflow
import argparse
import subprocess

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from os.path import join
from datetime import datetime
from tqdm import tqdm

class Simulation:
    experimentName = "Simulation"
    trackingUri = "http://10.24.36.24:5000"
    uiUsername = "mlflow"
    uiPassword = "siminhale"
    parameters = {}
    metrics = ["TIMESTEPLENGTH", "RE_NR"]

    def __init__(self, outputDirectory, datFile, runShell, command, args, runName=None):
        dt_string = self.startTimer()
        mlflow.set_experiment(self.experimentName)
        # mlflow.set_tracking_uri(self.trackingUri)
        # mlflow.set_credentials(self.uiUsername, self.uiPassword)
        # print(mlflow.get_tracking_uri())

        with mlflow.start_run() as run:
            mlflow.set_tag("mlflow.runName", runName if runName else "Run " + dt_string)
            self.parameters = self.parseDatFile(datFile)
            self.outputDirectory = outputDirectory
            if (runShell == "True"):
                self.runShell(command, args)
            else:
                print("Skipping the run command options")
            self.log(args)

        self.endTimer()

    def startTimer(self):
        self.start = datetime.now()
        print(self.experimentName + " started: " + self.start.strftime("%H:%M:%S"))
        return self.start.strftime("%Y-%m-%d (%H:%M)")

    def endTimer(self):
        end = datetime.now()
        print("Mlflow run ended: " + end.strftime("%H:%M:%S"))
        print("Mlflow run duration: " + str(end - self.start).split(".")[0])

    def logArgs(self, args=[]):
        if (len(args) < 2):
            return
        mlflow.log_param("Extra Args", args[1:])

    def logParameters(self):
        print("Logging Parameters:")
        for key, value in tqdm(self.parameters.items()):
            mlflow.log_param(key, value)

    def logMetrics(self):
        print("Logging Metrics:")
        for i in tqdm(range(len(self.metrics))):
            mlflow.log_metric(self.metrics[i], self.parameters[self.metrics[i]])

    def logArtifacts(self):
        meshFile = self.parameters["GEOFILE"] if int(self.parameters["MESH_TYPE"]) == 1 else self.parameters["BNDFILE"]
        outFile = self.parameters["OUTFILE"]
        print("Logging Artifacts: Mesh file")
        mlflow.log_artifact(join(self.outputDirectory, meshFile) , artifact_path="Input")
        print("Logging Artifacts: Output file")
        mlflow.log_artifact(join(self.outputDirectory, outFile)  , artifact_path="Output")

        if (int(self.parameters["WRITE_VTK"]) == 1):
            print("Logging Artifacts: VTK")
            vtkDir = self.parameters["OUTPUTDIR"]
            # mlflow.log_artifacts(join(self.outputDirectory, vtkDir), artifact_path="Output")
            files = os.listdir(join(self.outputDirectory, vtkDir))
            for i in tqdm(range(len(files))):
                mlflow.log_artifact(join(self.outputDirectory, vtkDir, files[i]), artifact_path=join("Output", vtkDir))

    def log(self, args):
        self.logArgs(args)
        self.logParameters()
        self.logMetrics()
        self.logArtifacts()

    def parseDatFile(self, filePath):
        values = {}
        with open(filePath, "r") as f:
            lines = f.readlines()
        for line in lines:
            specialChars = ["#", " ", "\n", "\t", "\r", "=", ":",
                            "(", ")", "[", "]", "{", "}", "<", ">",
                            "/", "\\", "|", ";", ",", ".", "?", "!",
                            "@", "$", "%", "^", "&", "*", "-", "_",
                            "+", "=", "~", "`", "\"", "\'"]
            if(not line.startswith(tuple(specialChars))):
                key, value = line.split(":")
                values[key] = value.strip()
        return values

    # run the executable and log the output as an artifact
    def runShell(self, command, args):
        reply = input(f"Are you sure you want to run the command \"{self.command} {self.args}\"?  (y/n)")
        if(reply == "y"):
            process = subprocess.Popen([self.command] + self.args, stdout=subprocess.PIPE, universal_newlines=True)
            stdout, _ = process.communicate()

            # Log the standard output as a file artifact
            stdoutPath = join(self.outputDirectory, "stdout.txt")
            with open(stdoutPath, "w") as f:
                f.write(stdout)
                mlflow.log_artifact(stdoutPath, artifact_path="Output")

class FluidSimulation (Simulation):
    experimentName = "Fluid Simulation"
    metrics = ["TIMESTEPLENGTH", "RE_NR"]

    def logArtifacts(self):
        Simulation.logArtifacts(self)

        print("Logging Artifacts: Solution files")
        files = [f for f in os.listdir(self.outputDirectory) if f.startswith("Solution_") and f.endswith(".bin")]
        for i in tqdm(range(len(files))):
            type = files[i].split("_")[1].upper()
            mlflow.log_artifact(join(self.outputDirectory, files[i]), artifact_path=f"Output/Solutions/{type}")
            
class ParticleSimulation (Simulation):
    experimentName = "Particle Simulation"
    metrics = ["TIMESTEPLENGTH", "RE_NR"]

    def logArgs(self, args):
        mlflow.set_tag("numberOfParticles", args[1])
        mlflow.set_tag("inputFluidSolutions", args[2])
        if (len(args) > 3):
            mlflow.log_param("Extra Args", args[3:])

    def logArtifacts(self):
        Simulation.logArtifacts(self)

        print("Logging Artifacts: Solution files")
        files = [f for f in os.listdir(self.outputDirectory) if f.startswith("siminhale_") and f.endswith(".csv")]
        for i in tqdm(range(len(files))):
            mlflow.log_artifact(join(self.outputDirectory, files[i]), artifact_path=f"Output/Solutions")

        csvFile = join(self.outputDirectory, files[-1])
        targetFile = join(self.outputDirectory, "deposition_fraction.")
        extensions = ['png', 'pdf', 'ps', 'eps', 'svg']
        particlesTotal, particlesDeposited, particlesEscaped, particlesStagnant, particlesErrored = self.plotDepositionFraction(csvFile, targetFile, extensions)
        mlflow.set_tag("Total Particles", particlesTotal)
        mlflow.set_tag("Deposited Particles", particlesDeposited)
        mlflow.set_tag("Escaped Particles", particlesEscaped)
        mlflow.set_tag("Stagnant Particles", particlesStagnant)
        mlflow.set_tag("Errored Particles", particlesErrored)

        print("Logging Artifacts: Deposition Fraction Plots")
        files = [targetFile + ext for ext in extensions]
        for i in tqdm(range(len(files))):
            mlflow.log_artifact(join(self.outputDirectory, files[i]), artifact_path=f"Output/Plots")

    def plotDepositionFraction(self, csvFile, targetFile, extensions):
        df = pd.read_csv(csvFile)
        df['section'] = df.apply(lambda row: self.categorise(row), axis=1)

        df_grouped = pd.DataFrame(df[(df['deposition'] == 1) & (df['escaped'] == 0)]['section'])
        df_grouped['count'] = 1
        particles = df_grouped.shape[0]
        df_grouped = df_grouped.groupby('section').sum('count').reset_index()
        df_grouped['Deposition fraction'] = (df_grouped['count'] / particles) * 100
        df_grouped.sort_values(by=['section'], inplace=True)

        plt.plot(df_grouped['section'], df_grouped['Deposition fraction'], marker="x")
        plt.xlabel("Segments")
        plt.ylabel("Deposition fraction (%)")
        plt.yscale("log")
        plt.xticks(list(range(0, 22, 2)))
        plt.yticks([0.001, 0.01, 0.1, 1, 10, 100])

        for ext in extensions:
            plt.savefig(targetFile + ext, dpi=300)

        particlesTotal = df.shape[0]
        particlesDeposited = particles
        particlesEscaped = df[df['escaped'] == 1].shape[0]
        particlesStagnant = df[df['escaped'] == 0].shape[0]
        particlesErrored = df[df['error'] == 1].shape[0]
        return particlesTotal, particlesDeposited, particlesEscaped, particlesStagnant, particlesErrored

    def categorise(self, row):  
        if   row['z'] >= -0.06:
            return 1
        elif row['z'] >= -0.180 and row['x'] >= -0.016 and row['x'] < 0.002:
            return 2
        elif row['z'] >= -0.200 and row['x'] >= -0.018 and row['x'] < 0.002:
            return 3
        elif row['z'] >= -0.216 and row['x'] >= -0.006 and row['x'] < 0.030:
            return 4
        elif row['z'] >= -0.220 and row['x'] >=  0.025 and row['x'] < 0.037:
            return 5
        elif row['z'] >= -0.228 and row['z'] < -0.215 and row['x'] >= 0.031 and row['x'] < 0.042:
            return 6
        elif row['z'] >= -0.217 and row['z'] < -0.207 and row['x'] >= 0.033 and row['x'] < 0.047:
            return 7
        elif row['z'] >= -0.207 and row['z'] < -0.187 and row['x'] >= -0.026 and row['x'] < -0.007:
            return 8
        elif row['z'] >= -0.206 and row['z'] < -0.190 and row['x'] >= -0.037 and row['x'] < -0.023:
            return 9
        elif row['z'] >= -0.223 and row['z'] < -0.205 and row['x'] >= -0.034 and row['x'] < -0.014:
            return 10
        elif row['z'] >= -0.230 and row['z'] < -0.221 and row['x'] >= -0.049 and row['x'] < -0.031:
            return 11
        elif row['z'] >= -0.246 and row['z'] < -0.226 and row['x'] >= -0.042 and row['x'] < -0.032:
            return 12
        elif row['z'] >= -0.210 and row['z'] < -0.150 and row['x'] >= 0.041 and row['x'] < 0.090:
            return 13
        elif row['z'] >= -0.260 and row['z'] < -0.220 and row['x'] >= 0.011 and row['x'] < 0.046:
            return 14
        elif row['z'] >= -0.310 and row['z'] < -0.230 and row['x'] >= 0.033 and row['x'] < 0.083:
            return 15
        elif row['z'] >= -0.245 and row['z'] < -0.205 and row['x'] >= 0.047 and row['x'] < 0.111:
            return 16
        elif row['z'] >= -0.260 and row['z'] < -0.222 and row['x'] >= -0.110 and row['x'] < -0.047:
            return 17
        elif row['z'] >= -0.310 and row['z'] < -0.230 and row['x'] >= -0.066 and row['x'] < -0.020 and row['y'] >= 0.080 and row['y'] < 0.130:
            return 18
        elif row['z'] >= -0.200 and row['z'] < -0.140 and row['x'] >= -0.110 and row['x'] < -0.040 and row['y'] >= 0.080 and row['y'] < 0.134:
            return 19
        elif row['z'] >= -0.245 and row['z'] < -0.225 and row['x'] >= -0.100 and row['x'] < -0.044 and row['y'] >= 0.095 and row['y'] < 0.110:
            return 20
        elif row['z'] >= -0.230 and row['z'] < -0.150 and row['x'] >= -0.090 and row['x'] < -0.020 and row['y'] >= 0.110 and row['y'] < 0.210:
            return 21
        elif row['z'] >= -0.260 and row['z'] < -0.220 and row['x'] >= -0.070 and row['x'] < -0.020 and row['y'] >= 0.120 and row['y'] < 0.180:
            return 22
        else:
            return -1

def setupArgs():
    parser = argparse.ArgumentParser(description=f"Run/Track a simulation using MLflow")
    parser.add_argument("experiment", help="the type of experiment to run/track: particle or fluid")
    parser.add_argument("outputDirectory", help="the output directory of the simulation")
    parser.add_argument("datFile", help="the dat file to use")
    parser.add_argument("--runShell", help="pass True to run the executable", default="False")
    parser.add_argument("--executable", help="the executable name", default="parmoon_3D_SEQUENTIAL.exe")
    parser.add_argument("--args", help="comma separated extra arguments", default="") # pass as space separated values to the main command

    args = parser.parse_args()
    outputDirectory = args.outputDirectory
    datFile = join(outputDirectory, args.datFile)
    runShell = args.runShell
    command = join(outputDirectory, args.executable)
    commandArgs = [] if len(args.args) == 0 else args.args.split(",")
    commandArgs.insert(0, datFile)
    return args.experiment, outputDirectory, datFile, runShell, command, commandArgs

if __name__== "__main__":
    experiment, *args = setupArgs()

    if (experiment == "particle"):
        ParticleSimulation(*args)
    elif (experiment == "fluid"):
        FluidSimulation(*args)
    else:
        print("Invalid experiment type")

