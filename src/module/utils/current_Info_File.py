# Déterminer le nom du fichier info.json courant

# from shared import metadata

def get_current_info_file(metadata):
    return f"data/webpages/info{metadata['file_index']}.json"