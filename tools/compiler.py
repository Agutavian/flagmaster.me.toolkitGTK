import io
import os
import json
import zipfile
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ExifTags, ImageOps
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib

from tools.data import cached_data
from tools.error_manager import warn_user_of_error


@dataclass
class PhotoData:
    compressedPath: str
    size: list
    location: str
    camera: str
    shutterSpeed: str
    iso: str
    aperture: str
    lens: str


def _process_single_image(file_path: str) -> tuple[str, bytes, bytes, PhotoData] | None:
    """Worker function to process EXIF, JPEG, and WEBP conversion for a single image path."""
    if not file_path or not os.path.exists(file_path):
        return None

    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)

            make = model = shutter_speed = aperture = ''
            iso = lens_make = lens_model = width = height = ''

            # Extract EXIF tags safely
            try:
                exif = img.getexif()
                if exif:
                    make = str(exif.get(ExifTags.Base.Make, '') or '').strip()
                    model = str(exif.get(ExifTags.Base.Model, '') or '').strip()

                    exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                    if exif_ifd:
                        shutter_speed = str(exif_ifd.get(ExifTags.Base.ShutterSpeedValue, '') or '').strip()
                        aperture = str(exif_ifd.get(ExifTags.Base.ApertureValue, '') or '').strip()
                        iso = str(exif_ifd.get(ExifTags.Base.ISOSpeedRatings, '') or '').strip()
                        lens_make = str(exif_ifd.get(ExifTags.Base.LensMake, '') or '').strip()
                        lens_model = str(exif_ifd.get(ExifTags.Base.LensModel, '') or '').strip()
                        width = str(exif_ifd.get(ExifTags.Base.ExifImageWidth, '') or '').strip()
                        height = str(exif_ifd.get(ExifTags.Base.ExifImageHeight, '') or '').strip()
            except Exception:
                pass

            camera = f"{make} {model}".strip()
            lens = f"{lens_make} {lens_model}".replace('\x00', '').strip()

            if not width or width == 'None':
                width = str(img.width)
            if not height or height == 'None':
                height = str(img.height)

            file_basename = os.path.basename(file_path)
            base_name = os.path.splitext(file_basename)[0]
            image_name = f"{base_name}.webp"

            rgb_img = img.convert('RGB')

            # Uncompressed JPEG buffer
            uncompressed_buf = io.BytesIO()
            rgb_img.save(uncompressed_buf, format="JPEG")
            uncompressed_bytes = uncompressed_buf.getvalue()

            # Compressed WebP buffer
            compressed_buf = io.BytesIO()
            rgb_img.save(compressed_buf, format="WEBP", quality=5, optimize=True)
            compressed_bytes = compressed_buf.getvalue()

            photodata = PhotoData(
                compressedPath=f"compressed_images/{image_name}",
                size=[width, height],
                location="",
                camera=camera,
                shutterSpeed=shutter_speed,
                iso=iso,
                aperture="" if aperture == "nan" else aperture,
                lens=lens
            )

            return image_name, uncompressed_bytes, compressed_bytes, photodata
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return None


class ImageCompilerClass:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)

    def ImageCompiler(self, output_path: str, on_complete=None):
        if not output_path:
            warn_user_of_error("ERROR: Output path cannot be empty")
            return
        if not os.path.isdir(output_path):
            warn_user_of_error("ERROR: Output path is not a valid directory")
            return

        all_categories = cached_data.categories_list
        if not all_categories or all(len(files) == 0 for files in all_categories.values()):
            warn_user_of_error("ERROR: No categories or images selected to compile")
            return

        warn_user_of_error("Starting image compilation in background...")

        def _worker():
            try:
                zip_filename = os.path.join(output_path, "flagmaster.me.toolkit.output.zip")
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)

                final_category_list: dict[str, dict] = {}

                # Gather all unique file paths across categories
                unique_paths = set()
                for paths in all_categories.values():
                    unique_paths.update(paths)

                # Process images in parallel across CPU cores
                processed_results: dict[str, tuple[str, bytes, bytes, PhotoData]] = {}
                futures = {
                    path: self._executor.submit(_process_single_image, path)
                    for path in unique_paths
                }

                for path, future in futures.items():
                    res = future.result()
                    if res is not None:
                        processed_results[path] = res

                # Write results to zip file
                with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
                    written_uncompressed = set()
                    written_compressed = set()

                    for category, file_paths in all_categories.items():
                        category_photo_json = {}
                        for path in file_paths:
                            if path in processed_results:
                                img_name, uncomp_bytes, comp_bytes, photodata = processed_results[path]

                                if img_name not in written_uncompressed:
                                    zipf.writestr(f"uncompressed_images/{img_name}", uncomp_bytes)
                                    written_uncompressed.add(img_name)

                                if img_name not in written_compressed:
                                    zipf.writestr(f"compressed_images/{img_name}", comp_bytes)
                                    written_compressed.add(img_name)

                                category_photo_json[img_name] = asdict(photodata)

                        final_category_list[category] = category_photo_json

                    zipf.writestr(
                        "photoInfo.json",
                        json.dumps(final_category_list, ensure_ascii=False, indent=4)
                    )

                GLib.idle_add(warn_user_of_error, f"Zip saved successfully to {zip_filename}")
                if on_complete:
                    GLib.idle_add(on_complete)

            except Exception as error:
                GLib.idle_add(warn_user_of_error, f"Compilation failed: {error}")

        self._executor.submit(_worker)
