#!/usr/bin/env python

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Contributors to the OpenEXR Project.

import sys, os, tempfile, atexit
from subprocess import PIPE, run

print(f"testing exrmultipart: {sys.argv}")

exrmultipart = sys.argv[1]
exrinfo = sys.argv[2]
image_dir = sys.argv[3]

result = run ([exrmultipart], stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 1)
assert("Usage:" in result.stderr)

image = f"{image_dir}/Beachball/multipart.0001.exr"

fd, outimage = tempfile.mkstemp(".exr")
os.close(fd)

def cleanup():
    print(f"deleting {outimage}")
    os.unlink(outimage)
atexit.register(cleanup)

# combine
command = [exrmultipart, "-combine", "-i", f"{image}:0", f"{image}:1", "-o", outimage]
result = run (command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 0)

result = run ([exrinfo, outimage], stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 0)

# error: can't convert multipart images
command = [exrmultipart, "-convert", "-i", image, "-o", outimage]
result = run (command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert (result.returncode != 0)

# convert
singlepart_image = f"{image_dir}/Beachball/singlepart.0001.exr"
command = [exrmultipart, "-convert", "-i", singlepart_image, "-o", outimage]
result = run (command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 0)

result = run ([exrinfo, outimage], stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 0)

# separate

# get part names from the multipart image
result = run ([exrinfo, image], stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(" ".join(result.args))
assert(result.returncode == 0)
part_names = {}
for p in result.stdout.split('\n part ')[1:]:
    output = p.split('\n')
    part_number, part_name = output[0].split(': ')
    part_names[part_number] = part_name

with tempfile.TemporaryDirectory() as tempdir:

    command = [exrmultipart, "-separate", "-i", image, "-o", f"{tempdir}/separate"]
    result = run (command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(" ".join(result.args))
    assert(result.returncode == 0)

    for i in range(1, 10):
        s = f"{tempdir}/separate.{i}.exr"
        result = run ([exrinfo, "-v", s], stdout=PIPE, stderr=PIPE, universal_newlines=True)
        print(" ".join(result.args))
        assert(result.returncode == 0)
        output = result.stdout.split('\n')
        assert(output[1].startswith(' parts: 1'))
        output[2].startswith(' part 1:')
        part_name = output[2][9:]
        part_number = str(i)
        assert(part_names[part_number] == part_name)
        
print("success")

