import torch,cv2
import sys, os, argparse
sys.path.append('./code/')
import matplotlib
import numpy as np
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchvision import transforms
import torch.backends.cudnn as cudnn
import torchvision
import torch.nn.functional as F
import datasets, hopenet, hopenet_utils
import math
import ipdb
from tqdm import tqdm
from utils.config import opt
from data.dataset import Dataset, TestDataset, inverse_normalize
from model import FasterRCNNVGG16
from torch.autograd import Variable
from torch.utils import data as data_
from trainer import FasterRCNNTrainer
from utils import array_tool as at
from utils.vis_tool import visdom_bbox
from utils.eval_tool import eval_detection_voc
import resource



def construct_model2():
    cudnn.enabled = True
    snapshot_path = "./input/_epoch_2.pkl"

    # ResNet50 structure
    model = hopenet.Hopenet(torchvision.models.resnet.Bottleneck, [3, 4, 6, 1], 66)

    print('Loading snapshot.')
    # Load snapshot
    saved_state_dict = torch.load(snapshot_path)
    model.load_state_dict(saved_state_dict)

    print( 'Loading data.')

    model.cuda()

    print('Ready to test network.')

    return model


def test_model(model):
    transformations = transforms.Compose([transforms.Scale(224),
    transforms.CenterCrop(224), transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    pose_dataset = datasets.jhk('/outfile/', '', transformations)

    test_loader = torch.utils.data.DataLoader(dataset=pose_dataset,
                                               batch_size=1,
                                               num_workers=8)
    save_text = True
    # Test the Model
    model.eval()  # Change model to 'eval' mode (BN uses moving mean/var).
    total = 0

    idx_tensor = [idx for idx in range(66)]
    idx_tensor = torch.FloatTensor(idx_tensor).cuda()

    roll_error = .0

    l1loss = torch.nn.L1Loss(size_average=False)

    for i, (images, labels, cont_labels, name, xy) in tqdm(enumerate(test_loader)):
        ffff = open("./outfile/" + name[0] + ".txt", 'r')
        imnamelist = ffff.readline().split(" ")
        imname = imnamelist[0]

        images = Variable(images).cuda()
        total += cont_labels.size(0)

        label_roll = cont_labels[:,2].float()

        roll = model(images)

        # Binned predictions
        _, roll_bpred = torch.max(roll.data, 1)
        # Continuous predictions
        roll_predicted = hopenet_utils.softmax_temperature(roll.data, 1)
        roll_predicted = torch.sum(roll_predicted * idx_tensor, 1).cpu() * math.radians(3) - math.radians(99)

        # or = softmax(roll)ean absolute error
        roll_error += torch.sum(torch.abs(roll_predicted - label_roll))

        if save_text:
            name = name[0]
            f = open('output/text/' + name + ".txt", 'w')
            f.write("%s\n" %imname)
            f.write("%s\n" %roll_predicted[0])
            f.write("%d %d %d %d" %(int(xy[0]), int(xy[1]), int(xy[2]), int(xy[3])))
            f.close()


rlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (20480, rlimit[1]))

matplotlib.use('agg')

def construct_model1():
    faster_rcnn = FasterRCNNVGG16()
    path = './checkpoints/fasterrcnn_01170835_0.9044215419174121'
    trainer = FasterRCNNTrainer(faster_rcnn).cuda()
    trainer = trainer.load(path)

    return trainer, faster_rcnn

def eval(trainer, faster_rcnn, test_num=0):
    pred_bboxes, pred_labels, pred_scores = list(), list(), list()
    
    testset = TestDataset(opt)
    dataloader = data_.DataLoader(testset, batch_size=1,num_workers=opt.test_num_workers, shuffle=False, pin_memory=True )

    for ii, (img, sizes, gt_bboxes_, gt_labels_, gt_difficults_, fname) in tqdm(enumerate(dataloader)):
        ori_img_ = inverse_normalize(at.tonumpy(img[0]))
        sizes = [sizes[0][0], sizes[1][0]]
        _bboxes, _labels, _scores = trainer.faster_rcnn.predict([ori_img_], visualize=True)
        filenum = 1 
        for i in _bboxes[0]:
            for j in i:
                j = int(j)
            outfile = open("./outfile/%06d.txt" %filenum, 'w')
            outfile.write("%s 0 0 0 %d %d %d %d" %(fname, i[0],i[1],i[2],i[3]))
            filenum +=1 
        numfile = open("./input/test.txt", 'w')
        for i in range(filenum-1):
            numfile.write("%06d\n" %(i+1))
        numfile.close()
        if ii == test_num: break

    print('----test is finished----')


m1t,m1f = construct_model()
m2 = construct_model2()

eval(m1t,m1f)
test_model(m2)








