import json
import os
import sys
import struct

from util import dump_json_from_file, write_vmd_header, get_file_size, Vertex_Attributes


def main():
    """
    Main logic for the converter.
    """
    sys.argv.append("D:\\Game_Shapes")  # Debugging purposes
    if len(sys.argv) == 1 or not os.path.isdir(sys.argv[1]):
        print_help()
        return

    process_dir(sys.argv[1], False, False)


def print_help():
    """
    Prints the help message.
    """

    print("help message")


def process_dir(dir_name, is_recursive, skip_built):
    """
    Processes all of the gltf files in the given directory.
    :param dir_name: Directory to process
    :param is_recursive: Whether the function should process subdirectories
    :param skip_built: Whether to skip gltf files that have already been built
    """

    dir_files = [os.path.join(dir_name, f) for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))]

    for f in dir_files:
        if f.endswith(".gltf"):
            if skip_built:
                test = ""
                # Check if we need to skip this file

            convert_gltf(f, dir_name)

    if is_recursive:
        sub_dirs = [d for d in os.listdir(dir_name) if os.path.isdir(os.path.join(dir_name, d))]

        for d in sub_dirs:
            process_dir(d, is_recursive, skip_built)


def convert_gltf(file_name, dir_name):
    """
    Converts the given gltf file to the vmd format.
    :param file_name: Name of the .gltf file
    :param dir_name: Name of the current directory
    """

    vmd_file_name = os.path.splitext(file_name)[0] + ".vmd"

    metadata = dump_json_from_file(file_name)

    with (open(vmd_file_name, mode='wb')) as vmd:
        if 'meshes' not in metadata or len(metadata['meshes']) == 0:
            return

        write_vmd_header(vmd)

        vmd.seek(0x18, 0)
        vmd.write(struct.pack('>i', get_file_size(vmd)))
        vmd.write(struct.pack('>i', len(metadata['meshes'])))
        vmd.seek(0, 2)

        for m in metadata['meshes']:
            vmd.write(struct.pack('>i', len(m['primitives'])))

            for p in m['primitives']:
                vmd.write(struct.pack('>i', len(p['attributes']) + 1))

                for a in p['attributes']:
                    # Skinning data will be handled differently
                    if a.startswith('JOINTS') or a.startswith('WEIGHTS'):
                        continue

                    vmd.write(struct.pack('>i', Vertex_Attributes[a].value))

                    att_accessor = metadata['accessors'][p['attributes'][a]]

                    vmd.write(struct.pack('>i', 1))

                    if att_accessor['componentType'] == 5126:
                        vmd.write(struct.pack('>i', 4))
                    elif att_accessor['componentType'] == 5123:
                        vmd.write(struct.pack('>i', 2))

                    vmd.write(struct.pack('>b', 0))
                    vmd.write(struct.pack('>b', -1))
                    vmd.write(struct.pack('>b', -1))
                    vmd.write(struct.pack('>b', -1))

                # We need to have a null attribute to end the attribute list
                vmd.write(struct.pack('>i', 255))
                vmd.write(struct.pack('>i', 1))
                vmd.write(struct.pack('>i', 0))
                vmd.write(struct.pack('>b', 0))
                vmd.write(struct.pack('>b', -1))
                vmd.write(struct.pack('>b', -1))
                vmd.write(struct.pack('>b', -1))

                for a in p['attributes']:
                    att_accessor = metadata['accessors'][p['attributes'][a]]
                    att_view = metadata['bufferViews'][att_accessor['bufferView']]

                    vmd.write(struct.pack('>i', att_view['buffer']))
                    vmd.write(struct.pack('>i', att_view['byteOffset']))
                    vmd.write(struct.pack('>i', att_accessor['count']))

                indices_accessor = metadata['accessors'][p['indices']]
                indices_view = metadata['bufferViews'][indices_accessor['bufferView']]

                vmd.write(struct.pack('>i', indices_view['byteOffset']))
                vmd.write(struct.pack('>i', indices_accessor['count']))

        # Write the buffer data (binary data including vertices, indices, etc)
        # Not sure how many buffers GLTF allows, so VMD will support up to 8 for now.
        for b in range(len(metadata['buffers'])):
            buf = metadata['buffers'][b]
            bin_name = os.path.join(dir_name, buf['uri'])

            if not os.path.exists(bin_name):
                return

            # Seek to this buffer's header data and write offset + size
            vmd.seek(56 + (8 * b), 0)
            vmd.write(struct.pack('>i', get_file_size(vmd)))
            vmd.write(struct.pack('>i', buf['byteLength']))

            # Return to the end of the file
            vmd.seek(0, 2)

            # Copy the buffer data from the .bin to the VMD file
            with (open(bin_name, mode='rb')) as bin_file:
                vmd.write(bin_file.read(buf['byteLength']))

        # Write final file size
        vmd.seek(12)
        vmd.write(struct.pack('>i', get_file_size(vmd)))

        vmd.flush()


if __name__ == "__main__":
    main()
