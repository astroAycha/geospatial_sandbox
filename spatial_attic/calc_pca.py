""" calc pca """

from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


class LandsatDimRed():
    """ Dimentionality reduction for Landsat 8 data"""

    def __init__(self):
        pass

    def calc_pca(self,
                input_path: str,
                output_path: str,
                clip_path: str | None = None):
        
        """
        calculate pca for landsat 8 data

        Parameters
        ----------
        input_path : str
            path to the input landsat 8 data
        output_path : str
            path to the output pca data
        clip_path : str | None, optional
            path to the clip shapefile, by default None
        """

        band_files = sorted(Path(input_path).glob("*_SR_B[2-7].TIF"))
        print("Bands found:")
        for b in band_files:
            print(" -", b.name)

        if len(band_files) == 0:
            raise FileNotFoundError("No SR bands found. Check input_path.")

        if clip_path:
            # Read clip geometry
            clip_gdf = gpd.read_file(clip_path)

        # --- Clip each band and build multiband stack ---
        clipped_bands = []
        out_transform = None
        out_meta = None

        for i, band_path in enumerate(band_files):
            with rasterio.open(band_path) as src:
                gdf = clip_gdf.to_crs(src.crs)
                clipped, out_transform = mask(src, 
                                              gdf.geometry, 
                                              crop=True, 
                                              filled=False)

                band = clipped[0].astype("float32")
                band[clipped.mask[0]] = np.nan
                clipped_bands.append(band)

                if i == 0:
                    out_meta = src.meta.copy()

        stack = np.stack(clipped_bands, axis=0)  # shape: (bands, rows, cols)
        print("Clipped stack shape (bands, rows, cols):", stack.shape)

        # Save clipped multiband raster
        clipped_out = Path(output_path) / "landsat_clipped_sr_b2_b7.tif"
        out_meta.update({
            "driver": "GTiff",
            "height": stack.shape[1],
            "width": stack.shape[2],
            "count": stack.shape[0],
            "dtype": "float32",
            "transform": out_transform,
            "nodata": np.nan
        })

        with rasterio.open(clipped_out, "w", **out_meta) as dst:
            dst.write(stack)

        print("Saved clipped raster:", clipped_out)

        # --- PCA on clipped pixels ---
        bands, rows, cols = stack.shape
        X = stack.reshape(bands, -1).T  # shape: (pixels, bands)
        valid = np.all(np.isfinite(X), axis=1)

        X_valid = X[valid]
        print("Valid pixels used for PCA:", X_valid.shape[0])

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_valid)

        pca = PCA(n_components=3)
        X_pca = pca.fit_transform(X_scaled)
        print("Explained variance ratio (PC1, PC2, PC3):", 
              pca.explained_variance_ratio_)

        # Put PCA scores back into image grid
        pca_img = np.full((3, rows * cols), np.nan, dtype="float32")
        pca_img[:, valid] = X_pca.T.astype("float32")
        pca_img = pca_img.reshape(3, rows, cols)

        # Save PCA raster
        pca_out = Path(output_path) / "landsat_clipped_pca_3comp.tif"
        out_meta_pca = out_meta.copy()
        out_meta_pca.update({
            "count": 3,
            "dtype": "float32",
            "nodata": np.nan
        })

        with rasterio.open(pca_out, "w", **out_meta_pca) as dst:
            dst.write(pca_img)

        print("Saved PCA raster:", pca_out)


    def plot_pca(self, pca_raster_path: str):
        """ plot pca results """

        with rasterio.open(pca_raster_path) as src:
            pca_data = src.read()
            pca_data[pca_data == src.nodata] = np.nan

        plt.figure(figsize=(15, 5))
        for i in range(3):
            plt.subplot(1, 3, i + 1)
            plt.imshow(pca_data[i], cmap="cividis")
            plt.title(f"PCA Component {i + 1}")
            plt.colorbar()
            plt.axis("off")
        plt.tight_layout()
        plt.show()

        plt.savefig(Path(pca_raster_path).with_suffix(".png"))
        print("Saved PCA plot:", Path(pca_raster_path).with_suffix(".png"))

if __name__ == "__main__":
    input_path = r"C:/Users/aycha/geospatial_sandbox/spatial_attic/data/LC09_L2SP_014028_20250728_20250730_02_T1"
    output_path = r"C:/Users/aycha/geospatial_sandbox/spatial_attic/data/"
    clip_path = ""

    pca_processor = LandsatDimRed()
    pca_processor.calc_pca(input_path, output_path, clip_path)

    pca_raster_path = Path(output_path) / "landsat_clipped_pca_3comp.tif"
    pca_processor.plot_pca(pca_raster_path)