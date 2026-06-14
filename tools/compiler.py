import gi
import io
import os
import json
import zipfile
from PIL import Image, ExifTags, ImageOps
from typing import List
from concurrent.futures import ThreadPoolExecutor
import threading
from tools.data import cached_data
from tools.error_manager import warn_user_of_error
# from tools.snapshot_manager import import_snapshot, export_snapshot
# from tools.error_manager import toast_overlay, warn_user_of_error
# from tools.misc import clear_listbox
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

# Step by Step Process
# First, get all the files and their dir
# Next, loop through all of them (asnyc). 
#   Compress into this:

# "path/to/file":
#    "compressed_file": compressed_file_object (TO OUTPUT AS WEBP)
#    "file": uncompressed (but still stripped of info)
#     "size": [
#         "x",
#         "y"
#     ],
#     "location": "Unknown",
#     "camera": "",
#     "shutterSpeed": "",
#     "iso": "",
#     "aperture": "",
#     "lens": ""


# Output JSON:
# "file_name": {
#     "uncompressedPath": "uncompressed_webp/file_name.jpg"
#     "compressedPath": "compressed_webp/file_name.webp"
#     "size": [
#         "x",
#         "y"
#     ],
#     "location": "Unknown",
#     "camera": "",
#     "shutterSpeed": "",
#     "iso": "",
#     "aperture": "",
#     "lens": ""
# },


class ImageCompilerClass:
    def __init__(self):
        self.images = []
        self.lock = threading.Lock()

    def ImageCompiler(
        self,
        # REMOVE BEFORE COMMITTING! TODO
        output_path: str,
    ):
        # output_name = "output_name"
        """
        Output_path -> where it should be outputted
        """

        
        from dataclasses import dataclass, asdict
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

        @dataclass
        class PhotoJsonData:
            image_name: str
            photodata: PhotoData

        # dir = 'image_converter/image_inputs'

        # listOfImageData:List[PhotoJsonData] = list()
        final_category_list: dict = {}

        make = model = software = shutterSpeed = aperture = focalLength = ''
        exposureTime = iso = lensMake = lensModel = width = height = ''


        # file = all_files.get_item(0)
        # all_files = cached_data.selected_files
        all_categories = cached_data.categories_list
        try:    
            with zipfile.ZipFile(f"{output_path}/flagmaster.me.toolkit.output.zip", "x") as zipf:
                # Loop through categories
                for category in all_categories:
                    # the list of all the outputs of the category
                    category_image_list:List[PhotoJsonData] = list()
                    
                    # Loop through file in category
                    for file_path in all_categories[category]:
                        gio_file = Gio.File.new_for_path(file_path)
                        if gio_file == None:
                            print(f"Not valid path when compiling!: {file_path}")
                            pass
                        else:
                            file_path = gio_file.get_path()
                            if file_path == None:
                                pass
                            else:    
                                img = Image.open(file_path)
                                img = ImageOps.exif_transpose(img)
                                img_exif = img.getexif()
                                IFD_CODE_LOOKUP = {i.value: i.name for i in ExifTags.IFD}

                                for tag_code, value in img_exif.items():

                                    # if the tag is an IFD block, nest into it
                                    if tag_code in IFD_CODE_LOOKUP:

                                        ifd_tag_name = IFD_CODE_LOOKUP[tag_code]
                                        # print(f"IFD '{ifd_tag_name}' (code {tag_code}):")
                                        ifd_data = img_exif.get_ifd(tag_code).items()

                                        for nested_key, nested_value in ifd_data:

                                            nested_tag_name = ExifTags.GPSTAGS.get(nested_key, None) or ExifTags.TAGS.get(nested_key, None) or nested_key
                                            match nested_tag_name:
                                                case "ShutterSpeedValue":
                                                    shutterSpeed = f" {nested_value}"
                                                    print(f" {nested_value}")
                                                case "ApertureValue":
                                                    aperture = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "FocalLength":
                                                    focalLength = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "ExposureTime":
                                                    exposureTime = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "ISOSpeedRatings":
                                                    iso = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "LensMake":
                                                    lensMake = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "LensModel":
                                                    lensModel = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "ExifImageWidth":
                                                    width = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                                case "ExifImageHeight":
                                                    height = f" {nested_value}"
                                                    print(f" {nested_tag_name}: {nested_value}")
                                            # print(f" {nested_tag_name}: {nested_value}")

                                    else:
                                        # root-level tag
                                        # print(f"{ExifTags.TAGS.get(tag_code)}: {value}")
                                        thingy = f"{ExifTags.TAGS.get(tag_code)}: {value}"
                                        thingy.startswith("")
                                        match thingy:
                                            case "":
                                                print("Nothing")
                                            case s if thingy.startswith('Make'):
                                                make = thingy
                                                print(thingy)
                                            case s if thingy.startswith('Model'):
                                                model = thingy
                                                print(thingy)
                                            case s if thingy.startswith('Software'):
                                                software = thingy
                                                print(thingy)


                                camera = make.removeprefix('Make:') + model.removeprefix("Model:")
                                lens = lensMake + lensModel

                                if aperture == ' nan':
                                    aperture = ''
                                print("===============================================================================")

                                # PART THAT CONVERRTS IMAGE TO WEBP

                                # data = list(img.getdata())
                                file_basename = gio_file.get_basename()
                                if file_basename == None:
                                    file_basename = "broken filename lmao"
                                image_name = file_basename.split('.JPG')[0] + '.webp'
                                image_name = file_basename.split('.JPG')[0] + '.webp'

                                img.convert('RGB')
                                
                
                                uncompressed_buffer = io.BytesIO()
                                img.save(uncompressed_buffer,
                                        format="jpeg")
                                zipf.writestr(f"uncompressed_images/{image_name}", uncompressed_buffer.getvalue())


                                compressed_buffer = io.BytesIO()
                                img.save(
                                    compressed_buffer,
                                    "webp",
                                    quality=5,
                                    optimize=True
                                )
                                # img.close()

                                
                                zipf.writestr(f"compressed_images/{image_name}", compressed_buffer.getvalue())


                                photodata = PhotoData(
                                    compressedPath= "compressed_images/" + image_name,
                                    size = [width.strip(), height.strip()],
                                    location= "",
                                    camera = camera,
                                    shutterSpeed= shutterSpeed.strip(),
                                    iso= iso.strip(),
                                    aperture= aperture.strip(),
                                    lens= lens.replace('\x00','').strip()
                                )

                                
                                photoJsonData = PhotoJsonData(
                                    image_name=image_name,
                                    photodata=photodata
                                )

                                category_image_list.append(photoJsonData)

                                # print(listOfImageData)
                    
                    category_json: dict[str, list[dict]]
                    photoJson = {}
                    for item in category_image_list:
                        photoJson[item.image_name] = asdict(item.photodata)

                    for item in category_image_list:
                        final_category_list[category] = photoJson
                    print(photoJson)
                    print(final_category_list)



                # print(photoJson)

                funky_bits = io.BytesIO()
                zipf.writestr(
                    "photoInfo.json",
                    json.dumps(final_category_list, ensure_ascii=False, indent=4)
                )
                warn_user_of_error(error_message=f"Zip saved to {output_path}")
        except Exception as error:
            warn_user_of_error(error_message=f"{error}")