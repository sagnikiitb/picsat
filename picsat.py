#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("--- Sentinel-2 RGB Composite Automator ---")

    # 1. Ask for user inputs
    red = input("red=? ")
    green = input("green=? ")
    blue = input("blue=? ")
    name = input("Output filename base (e.g., swiroutput): ")
    inputfilepath = input("Full Path to the MTD_MSIL1C.xml file of the Project: ")

    if not red or not green or not blue or not name:
        print("Error: All inputs are required.")
        sys.exit(1)

    bands = f"{red},{green},{blue}"
    raw_output = f"{name}.tif"
    optimized_output = f"{name}_optimized.tif"

    # Hardcoded input file as requested
    #input_xml = "/home/fine/Downloads/S2C_MSIL1C_20260416T053641_N0512_R005_T43QBB_20260416T091808.SAFE/MTD_MSIL1C.xml"
    input_xml = f"{inputfilepath}"

    # Expand the home directory path for GPT to avoid alias issues in Python
    gpt_path = os.path.expanduser("~/esa-snap/bin/gpt")

    try:
        # Step 1: Run GPT to create the initial composite
        print(f"\n[1/4] Generating composite ({bands}) via SNAP GPT...")
        gpt_cmd = [
            gpt_path, "composite.xml",
            f"-Pinput={input_xml}",
            f"-Poutput={raw_output}",
            f"-Pbands={bands}"
        ]
        subprocess.run(gpt_cmd, check=True)

        # Step 2: Tile and compress the image
        print(f"\n[2/4] Tiling and compressing to {optimized_output}...")
        gdal_translate_cmd = [
            "gdal_translate",
            "-co", "TILED=YES",
            "-co", "COMPRESS=LZW",
            "-co", "BLOCKXSIZE=512",
            "-co", "BLOCKYSIZE=512",
            raw_output,
            optimized_output
        ]
        subprocess.run(gdal_translate_cmd, check=True)

        # Step 3: Build overviews (pyramids)
        print("\n[3/4] Building overviews (pyramids) for fast rendering...")
        gdaladdo_cmd = [
            "gdaladdo",
            "-r", "average",
            optimized_output,
            "2", "4", "8", "16", "32"
        ]
        subprocess.run(gdaladdo_cmd, check=True)

        # Step 4: Open in QGIS
        print(f"\n[4/4] Opening {optimized_output} in QGIS...")
        # Using Popen so QGIS launches independently without freezing the terminal
        subprocess.Popen(["qgis", optimized_output], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("\nDone! Your optimized Sentinel-2 composite is ready.")

    except subprocess.CalledProcessError as e:
        print(f"\nError: A process failed during execution. Details: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nError: Could not find a required tool. Ensure SNAP and GDAL are installed. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
