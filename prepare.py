#!/usr/bin/env python
import os
from osgeo import gdal, gdalconst
import requests
import patoolib

def download_and_extract_srtm():
    # Download SRTM files
    srtm_urls = [
        "https://srtm.csi.cgiar.org/wp-content/uploads/files/250m/SRTM_NE_250m_TIF.rar",
        "https://srtm.csi.cgiar.org/wp-content/uploads/files/250m/SRTM_SE_250m_TIF.rar",
        "https://srtm.csi.cgiar.org/wp-content/uploads/files/250m/SRTM_W_250m_TIF.rar",
    ]
    for url in srtm_urls:
        filename = os.path.basename(url)
        response = requests.get(url, stream=True)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    # Extract SRTM files using patoolib
    srtm_rar_files = ["SRTM_NE_250m_TIF.rar", "SRTM_SE_250m_TIF.rar", "SRTM_W_250m_TIF.rar"]
    for rar_file in srtm_rar_files:
        patoolib.extract_archive(rar_file, outdir="./")

    # Remove the downloaded rar files
    for rar_file in srtm_rar_files:
        os.remove(rar_file)


def chunk_raster(raster, xtiles, ytiles):
    # Open the raster
    ds = gdal.Open(raster, gdalconst.GA_ReadOnly)

    # Get raster bounds
    ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
    lrx = ulx + (ds.RasterXSize * xres)
    lry = uly + (ds.RasterYSize * yres)

    xmin = ulx
    xsize = lrx - xmin
    ysize = uly - lry

    xdif = xsize / xtiles

    for x in range(xtiles):
        xmax = xmin + xdif
        ymax = uly
        ydif = ysize / ytiles

        for y in range(ytiles):
            ymin = ymax - ydif

            # Create chunk of source raster
            chunk_name = f"{os.path.splitext(raster)[0]}_{x}_{y}.tif"
            gdal.Translate(chunk_name, ds, projWin=[xmin, ymax, xmax, ymin], format="GTiff")

            ymax = ymin

        xmin = xmax

    # Close the raster dataset
    ds = None

if __name__ == '__main__':
    outdir = "/code/data"

    if not os.path.exists(outdir):
        print(f"{outdir} does not exist!")

    os.chdir(outdir)

    # Download and extract SRTM files
    download_and_extract_srtm()

    # Create chunks of SRTM files
    chunk_raster("SRTM_NE_250m.tif", 10, 10)
    chunk_raster("SRTM_SE_250m.tif", 10, 10)
    chunk_raster("SRTM_W_250m.tif", 10, 20)

    # Remove the SRTM files and rar files
    os.remove("SRTM_NE_250m.tif")
    os.remove("SRTM_SE_250m.tif")
    os.remove("SRTM_W_250m.tif")
    os.system("rm -rf *.rar")
