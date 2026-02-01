
import os
import exiftool
from datetime import datetime

class ExifHandler:
    def __init__(self, exiftool_path=None):
        self.exiftool_path = exiftool_path

    def get_metadata(self, filepath):
        """
        Reads metadata from the given file using ExifTool.
        Returns a dictionary of tags.
        """
        try:
            with exiftool.ExifToolHelper(executable=self.exiftool_path) as et:
                metadata = et.get_metadata(filepath)[0]
                return metadata
        except Exception as e:
            print(f"Error reading metadata for {filepath}: {e}")
            return None

    def get_date_info(self, filepath):
        """
        Extracts the most relevant 'Date Taken' AND its source tag.
        Returns (date_str, source_tag) or (None, None).
        """
        meta = self.get_metadata(filepath)
        if not meta:
            return None, None
        
        return self._extract_date_from_meta(meta)

    def get_batch_date_info(self, filepaths):
        """
        Batch fetches date info for multiple files.
        Returns dict: {norm_lower_path: date_str}
        Keys are normalized absolute lower-case paths for robust matching.
        """
        results = {}
        if not filepaths:
            return results
        
        try:
            with exiftool.ExifToolHelper(executable=self.exiftool_path) as et:
                metadata_list = et.get_metadata(filepaths)
                
                for meta in metadata_list:
                    src = meta.get("SourceFile")
                    date_val, _ = self._extract_date_from_meta(meta)
                    
                    if src and date_val:
                        # Normalize to help matching across systems/formats
                        # We use absolute path lowercased
                        abs_path = os.path.abspath(src)
                        norm_key = abs_path.lower()
                        results[norm_key] = date_val
                        
        except Exception as e:
            print(f"Error in batch metadata: {e}")
            
        return results

    def _extract_date_from_meta(self, meta):
        # Candidate tags in order of preference
        tags = [
            'EXIF:DateTimeOriginal',
            'QuickTime:CreateDate',
            'QuickTime:MediaCreateDate',
            'XMP:DateCreated',
            'IPTC:DateCreated',
            'File:FileModifyDate'
        ]
        
        for tag in tags:
            if tag in meta:
                return meta[tag], tag
        
        return None, None

    def update_date(self, filepath, new_date_str):
        """
        Updates the creation date tags to the new date.
        """
        try:
            params = [
                f"-AllDates={new_date_str}",
                "-overwrite_original"
            ]
            
            lower_path = filepath.lower()
            if lower_path.endswith(('.mp4', '.mov', '.m4v')):
                 params.append(f"-QuickTime:CreateDate={new_date_str}")
                 params.append(f"-QuickTime:MediaCreateDate={new_date_str}")

            with exiftool.ExifToolHelper(executable=self.exiftool_path) as et:
                et.execute(*params, filepath)
            return True
        except Exception as e:
            print(f"Error updating metadata for {filepath}: {e}")
            return False
