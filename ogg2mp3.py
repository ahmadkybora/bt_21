#!/usr/bin/env python
"""Convert ogg files to mp3"""
from optparse import OptionParser
import tempfile
import os
import subprocess

class CommandException(Exception):
    """Exception that is raised if calling an external command fails"""
    def __init__(self, command):
        self.command = command
    def __str__(self):
        return self.command

def ogg2wav(ogg_file, wav_file):
    """Run ogg123 to convert from an ogg file to a wav file"""
    commands = ["ogg123", "-d", "wav", "-f", wav_file, ogg_file]
    run_command(commands)

def wav2mp3(wav_file, mp3_file, lame_vbr_setting):
    """Convert wav file to mp3 file"""
    commands = ["lame",
                "-V",
                lame_vbr_setting,
                "--vbr-new",
                "-h",
                wav_file,
                mp3_file]
    run_command(commands)

def run_command(command):
    """Run a command, given an array of the command and arguments"""
    proc = subprocess.Popen(command)
    ret = proc.wait()
    if ret != 0:
        raise CommandException(" ".join(command))


def ogg2mp3(input_files, outputdir, lame_V):
    """Convert ogg files to mp3"""
    for ogg_file in input_files:
        #Convert ogg file to wav
        input_file_dir, input_file_name = os.path.split(ogg_file)
        if outputdir == None:
            mp3dir = input_file_dir
        else:
            mp3dir = outputdir
        input_file_base_name, _ = os.path.splitext(input_file_name)
        wav_file = os.path.join(tempfile.mkdtemp(), input_file_base_name+".wav")
        ogg2wav(ogg_file, wav_file)

        #Convert wav file to mp3
        mp3_file = os.path.join(mp3dir, input_file_base_name+".mp3")
        wav2mp3(wav_file, mp3_file, lame_V)

def main():
    """Main script. Get options and arguments"""
    usage = "usage: %prog [options] <input file pattern>"
    parser = OptionParser(usage)
    parser.add_option("-o", "--outputdir",
                      action="store", type="string", dest="outputdir")
    parser.add_option("-V",
                      action="store", type="string", dest="lameV", default="2")

    options, args = parser.parse_args()
    if len(args) < 1:
        # need some files to process!
        parser.error("incorrect number of arguments")
    ogg2mp3(args, options.outputdir, options.lameV)

if __name__ == "__main__":
    main()