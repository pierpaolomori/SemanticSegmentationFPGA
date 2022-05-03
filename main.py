import os
import numpy as np
from PIL import Image
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import argparse


def replace(file_path, line, subst):
    fh, abs_path = mkstemp()
    line_idx = 0
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line_ in old_file:
                if line_idx == line:
                    new_file.write(subst)
                else:
                    new_file.write(line_)
                line_idx += 1
    copymode(file_path, abs_path)
    remove(file_path)
    move(abs_path, file_path)


def quantize(x, precision = 16):
    x_m = np.max(np.abs(x))
    x_m_quantized = np.power(2, precision - 1) - 1
    scaling_factor = np.divide(x_m_quantized, x_m)
    # print("sf = " + str(scaling_factor))
    return np.int16(np.round(x * scaling_factor ))


parser = argparse.ArgumentParser(description='List of parameters needed for model inference')
parser.add_argument('-m', '--model', type=str, default="prune", help='model selection | vanilla | prune |')
parser.add_argument('-n', '--num_img', type=str, default=5, help='Number of images')
parser.add_argument('-s', '--show_seg', type=str, default=1, help='Show Segmentation Output')
parser.add_argument('-u', '--unroll_conf', type=str, default="16_16_4", help='Set Unrolling configuration Pif,Pof,Pkx 16_16_1 | 16_16_4 | 16_32_1 | 16_32_4')
args = parser.parse_args()

if args.unroll_conf == "16_16_1":
    kernel_path = "FPGA_Binaries/16_16_1/F4_3.aocx"
    define_config = "CONFIG_16_16_1"
elif args.unroll_conf == "16_16_4":
    kernel_path = "FPGA_Binaries/16_16_4/F4_3.aocx"
    define_config = "CONFIG_16_16_4"
elif args.unroll_conf == "16_32_1":
    kernel_path = "FPGA_Binaries/16_32_1/F4_3.aocx"
    define_config = "CONFIG_16_32_1"
else:
    kernel_path = "FPGA_Binaries/16_32_4/F4_3.aocx"
    define_config = "CONFIG_16_32_4"

if args.model == "prune":
    # network_model = "Resnet18_16bit_Deeplab_960if_V2_baseline_Cprune_experiment.h"
    weight_path = "weights/pruned_weights.dat"
else:
    # network_model = "Resnet18_16bit_Deeplab_960if_V2_baseline.h"
    weight_path = "weights/std_weights.dat"

""" CONFIG """
pruned_model = True

img_path = 'Quantized_16bit_imgs/'
seg_path = 'Segmentation/'


replace('configs/host_config_hw.yaml', 0, 'kernel_file_name: ' + kernel_path + '\n')
replace('configs/host_config_hw.yaml', 2, 'input_data_folder: ' + img_path + '\n')
replace('configs/host_config_hw.yaml', 4, 'seg_output: ' + seg_path + '\n')
replace('configs/host_config_hw.yaml', 6, 'weight_file_path: ' + weight_path + '\n')
replace('configs/host_config_hw.yaml', 12, 'num_img: ' + str(args.num_img) + '\n')
replace('configs/host_config_hw.yaml', 14, 'show_seg: ' + str(args.show_seg) + '\n')


os.system(f'./host/host_{args.unroll_conf+"_"+args.model} configs/host_config_hw.yaml' )







