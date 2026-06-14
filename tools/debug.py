from tools.data import cached_data
class DebugClass():
    def print_debug(self):
        print(
            f"""
selected_files = {cached_data.selected_files}

categories_list = {cached_data.categories_list}

active_snapshot = {cached_data.active_snapshot}

new_images = {cached_data.new_images}

"""   
        )
debug = DebugClass()