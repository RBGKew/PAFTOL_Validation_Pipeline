#!/usr/bin/env python3

"""
BOLD Dataset Downloader

Author: Berta Gallego
Date: 2025-11-04
Description: 
    This script downloads Angiosperms's orders datasets from the BOLD (Barcode
    of Life Data) public API v4 in TSV format. BOLD can be queried by order,
    but not by class.  The order datasets are merged into a single
    'bold_data.txt' file.

Usage:
    python download_bold.py
"""
import requests
import time
import os


BASE_URL = "https://www.boldsystems.org/index.php/API_Public/combined"

def main(orders, out_dir="bold_orders_tsv", delay=2):
    """
    Download BOLD datasets for a list of orders and merge them.
    """
    os.makedirs(out_dir, exist_ok=True)

    for order in orders:
        download_bold_order(order, out_dir, delay=delay)
    merge_tsv_files(out_dir)


def download_bold_order(order, out_dir, delay=2):
    """Download a single order dataset from BOLD in TSV format."""
    file_path = os.path.join(out_dir, f"{order}.tsv")
    temp_file = os.path.join(out_dir, f"{order}.temp")

    # Skip if already downloaded
    if os.path.exists(file_path):
        print(f"{file_path} already exists, skipping...")
        return

    print(f"Downloading {order}...")
    params = {"taxon": order, "format": "tsv"}

    try:
        with requests.get(BASE_URL, params=params, stream=True, timeout=60) as r:
            if r.status_code != 200:
                print(f"Failed to download {order}, status code: {r.status_code}")
                return

            with open(temp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        os.rename(temp_file, file_path)
        print(f"Saved {order} to {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {order}: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

    time.sleep(delay)


def merge_tsv_files(out_dir, merged_filename="bold_data.txt"):
    """Merge all TSV files from out_dir into a single file."""
    tsv_files = sorted(
        [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".tsv")]
    )

    if not tsv_files:
        print("No TSV files to merge.")
        return

    header_written = False
    with open(merged_filename, "w") as fout:
        for tsv_file in tsv_files:
            print(f"Processing {tsv_file}...")
            with open(tsv_file, "r") as fin:
                lines = fin.readlines()
                if not lines:
                    continue
                header = lines[0]
                if not header_written:
                    fout.write(header)
                    header_written = True
                fout.writelines(lines[1:])

    print(f"All orders merged into {merged_filename}")


if __name__ == "__main__":
    ORDERS = [
        'Acorales', 'Alismatales', 'Amborellales', 'Apiales', 'Aquifoliales',
        'Arecales', 'Asparagales', 'Asterales', 'Austrobaileyales',
        'Berberidopsidales', 'Boraginales', 'Brassicales', 'Bruniales',
        'Buxales', 'Canellales', 'Caryophyllales', 'Celastrales',
        'Ceratophyllales', 'Chloranthales', 'Commelinales', 'Cornales',
        'Crossosomatales', 'Cucurbitales', 'Dilleniales', 'Dioscoreales',
        'Dipsacales', 'Ericales', 'Escalloniales', 'Fabales', 'Fagales',
        'Garryales', 'Gentianales', 'Geraniales', 'Gunnerales', 'Huerteales',
        'Icacinales', 'Lamiales', 'Laurales', 'Liliales', 'Magnoliales',
        'Malpighiales', 'Malvales', 'Metteniusales', 'Myrtales', 'Nymphaeales',
        'Oxalidales', 'Pandanales', 'Paracryphiales', 'Petrosaviales',
        'Picramniales', 'Piperales', 'Poales', 'Proteales', 'Ranunculales',
        'Rosales', 'Santalales', 'Sapindales', 'Saxifragales', 'Solanales',
        'Trochodendrales', 'Vahliales', 'Vitales', 'Zingiberales',
        'Zygophyllales'
    ]
    main(ORDERS)
