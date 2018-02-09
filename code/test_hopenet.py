import torch,cv2
import sys, os, argparse

import numpy as np

import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import transforms
import torch.backends.cudnn as cudnn
import torchvision
import torch.nn.functional as F

import datasets, hopenet, utils
import math

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Head pose estimation using the Hopenet network.')
    parser.add_argument('--snapshot', dest='snapshot', help='Name of model snapshot.',
          default='./input/_epoch_2.pkl', type=str)
    parser.add_argument('--dataset', dest='dataset', help='Dataset type.', default='jhk', type=str)
    parser.add_argument('--text', dest='save_text', help='12345.', default='True', type=bool)
    parser.add_argument('--data_dir', dest='data_dir', help='Directory path for data.', default='/outfile/', type=str)
    parser.add_argument('--filename_list', dest='filename_list', help='Path.', default='', type=str)
    parser.add_argument('--batch_size', dest='batch_size', help='Batch size.', default=1, type=int)
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]', default=0, type=int)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    
    cudnn.enabled = True
    gpu = args.gpu_id
    snapshot_path = args.snapshot

    # ResNet50 structure
    model = hopenet.Hopenet(torchvision.models.resnet.Bottleneck, [3, 4, 6, 1], 66)

    print('Loading snapshot.')
    # Load snapshot
    saved_state_dict = torch.load(snapshot_path)
    model.load_state_dict(saved_state_dict)

    print( 'Loading data.')

    transformations = transforms.Compose([transforms.Scale(224),
    transforms.CenterCrop(224), transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    if args.dataset == 'jhk':
        pose_dataset = datasets.jhk(args.data_dir, args.filename_list, transformations)
    else:
        print ('Error: not a valid dataset name')
        sys.exit()
    test_loader = torch.utils.data.DataLoader(dataset=pose_dataset,
                                               batch_size=args.batch_size,
                                               num_workers=8)

    model.cuda(gpu)

    print ('Ready to test network.')

    # Test the Model
    model.eval()  # Change model to 'eval' mode (BN uses moving mean/var).
    total = 0

    idx_tensor = [idx for idx in range(66)]
    idx_tensor = torch.FloatTensor(idx_tensor).cuda(gpu)

    roll_error = .0

    l1loss = torch.nn.L1Loss(size_average=False)

    for i, (images, labels, cont_labels, name, xy) in enumerate(test_loader):
        ffff = open("./outfile/" + name[0] + ".txt", 'r')
        imnamelist = ffff.readline().split(" ")
        imname = imnamelist[0]

        images = Variable(images).cuda(gpu)
        total += cont_labels.size(0)

        label_roll = cont_labels[:,2].float()

        roll = model(images)

        # Binned predictions
        _, roll_bpred = torch.max(roll.data, 1)
        # Continuous predictions
        roll_predicted = utils.softmax_temperature(roll.data, 1)
        roll_predicted = torch.sum(roll_predicted * idx_tensor, 1).cpu() * math.radians(3) - math.radians(99)


        # or = softmax(roll)ean absolute error
        roll_error += torch.sum(torch.abs(roll_predicted - label_roll))

        if args.save_text:
            name = name[0]
            f = open('output/text/' + name + ".txt", 'w')
            f.write("%s\n" %imname)
            f.write("%s\n" %roll_predicted[0])
            f.write("%d %d %d %d" %(int(xy[0]), int(xy[1]), int(xy[2]), int(xy[3])))
            f.close()

