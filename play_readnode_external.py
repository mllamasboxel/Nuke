import nuke
import subprocess
import os
import re
import glob

def _expand_sequence(pattern, frame):
    """
    Convert a sequence pattern (%d, %04d, ####, ###) into a real filename for the given frame.
    If the exact expansion doesn't exist, try to find a matching file using glob and return the first match.
    """
    # If pattern contains #### / ### style:
    if "####" in pattern:
        candidate = pattern.replace("####", f"{frame:04d}")
        if os.path.exists(candidate):
            return candidate
        # otherwise try glob
        pattern_glob = pattern.replace("####", "????")
        matches = glob.glob(pattern_glob)
        if matches:
            return sorted(matches)[0]
        return candidate

    if "###" in pattern:
        candidate = pattern.replace("###", f"{frame:03d}")
        if os.path.exists(candidate):
            return candidate
        pattern_glob = pattern.replace("###", "???")
        matches = glob.glob(pattern_glob)
        if matches:
            return sorted(matches)[0]
        return candidate

    # Handle %d and %0Nd patterns using regex
    m = re.search(r'%0?(\d*)d', pattern)
    if m:
        digits = m.group(1)
        if digits == "":
            # plain %d -> no zero padding (but most sequences use padding, handle as 1)
            fmt = "{:d}"
        else:
            fmt = "{:0" + digits + "d}"
        candidate = re.sub(r'%0?\d*d', fmt.format(frame), pattern, count=1)
        if os.path.exists(candidate):
            return candidate
        # fallback: replace the %...d with a glob wildcard and try to find any matching file
        pattern_glob = re.sub(r'%0?\d*d', '*', pattern, count=1)
        matches = glob.glob(pattern_glob)
        if matches:
            return sorted(matches)[0]
        return candidate

    # Not a sequence pattern - return as-is
    return pattern

def play_readnode_in_rv():
    try:
        node = nuke.selectedNode()
    except ValueError:
        nuke.message("No node selected.")
        return

    if node.Class() not in ["Read", "ReadGeo", "DeepRead"]:
        nuke.message("Please select a Read node.")
        return

    # Use the raw knob value (pattern) so we can handle "%d" style patterns.
    # If you're using [getenv] or expressions in the file knob you may want to evaluate:
    # pattern = node['file'].evaluate(int(nuke.frame()))  # optional
    pattern = node['file'].value()
    if not pattern:
        nuke.message("Read node file path is empty.")
        return

    first = int(node['first'].value())
    last  = int(node['last'].value())

    # Expand sequence to an actual file path for the first frame
    first_frame_file = _expand_sequence(pattern, first)

    # Debug prints
    print("Pattern:", pattern)
    print("Expanded first frame file:", first_frame_file)

    if not os.path.exists(first_frame_file):
        msg = f"File not found:\n{first_frame_file}\n\n(from pattern: {pattern})"
        nuke.message(msg)
        return

    # RV executable (adjust path if different)
    rv_exe = r"C:\Program Files\Autodesk\RV-2024.1.0\bin\rv.exe"
    if not os.path.exists(rv_exe):
        nuke.message("RV executable not found:\n{}".format(rv_exe))
        return

    # RV supports sequence patterns, pass the original pattern and frame range
    cmd = [
        rv_exe,
        pattern,
        f"{first}-{last}"
    ]

    print("Launching RV:", cmd)

    try:
        subprocess.Popen(cmd)
    except Exception as e:
        nuke.message("Error launching RV:\n{}".format(str(e)))

# Alias for your menu code (fixed)
play_readnode_with_external_player = play_readnode_in_rv
