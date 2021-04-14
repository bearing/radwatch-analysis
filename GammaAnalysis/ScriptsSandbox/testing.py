import argparse
parser = argparse.ArgumentParser(description="Signal processing (background subtraction) for parsed SIS3320 raw data")
parser.add_argument('filename', type=str, help="Input data file of type .spe")
args = parser.parse_args()

specname = args.filename
config = specname + 'Config'

print(specname)
print(config)