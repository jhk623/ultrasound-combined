import os
import ipdb
import matplotlib
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

rlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (20480, rlimit[1]))

matplotlib.use('agg')
faster_rcnn = FasterRCNNVGG16()

def eval(dataloader, faster_rcnn, test_num=0):
    pred_bboxes, pred_labels, pred_scores = list(), list(), list()
    path = './checkpoints/fasterrcnn_01170835_0.9044215419174121'
    trainer = FasterRCNNTrainer(faster_rcnn).cuda()
    trainer.load(path)

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

testset = TestDataset(opt)
test_dataloader = data_.DataLoader(testset,
                                       batch_size=1,
                                       num_workers=opt.test_num_workers,
                                       shuffle=False, \
                                       pin_memory=True
                                       )

eval(test_dataloader,faster_rcnn, test_num=1)



### 2018.01.20
### JAEHONG KIM


