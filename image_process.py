from PIL import Image as im
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import os
import sys

def main(filename):
    imagepath = "./garconsdata/JPEGImages/"
    txtpath = "./garconsdata/ImageSets/Main/test.txt"
    filepath = "./garconsdata/Annotations/"
    im1 = im.open(imagepath + filename)
    sz = im1.size

    # root tree
    Annot = ET.Element('annotation')
    Fol = ET.SubElement(Annot, 'folder')
    Fol.text = 'garconsdata'
    Fil = ET.SubElement(Annot, 'filename')
    Fil.text = filename

    # source tree
    Sou = ET.SubElement(Annot, 'source')
    DB = ET.SubElement(Sou, 'database')
    DB.text = 'The VOC2007 Database'
    anno = ET.SubElement(Sou, 'annotation')
    anno.text = 'PASCAL VOC2007'
    Ima = ET.SubElement(Sou, 'image')
    Ima.text = 'flickr'
    FLd = ET.SubElement(Sou, 'flickrid')
    FLd.text = 'jhk623'

    # owner tree
    Own = ET.SubElement(Annot, 'owner')
    Flid = ET.SubElement(Own, 'flickerid')
    Flid.text = 'jhk623'
    Nam = ET.SubElement(Own, 'name')
    Nam.text = 'jh'

    # size tree
    Siz = ET.SubElement(Annot, 'size')
    Wid = ET.SubElement(Siz, 'width')
    Wid.text = str(sz[0]) 
    Hei = ET.SubElement(Siz, 'height')
    Hei.text = str(sz[1])
    Dep = ET.SubElement(Siz, 'depth')
    Dep.text = '3'

    # segmented
    Seg = ET.SubElement(Annot, 'segmented')
    Seg.text = '0'

    # object tree
    Obj = ET.SubElement(Annot, 'object')
    nam = ET.SubElement(Obj, 'name')
    nam.text = 'face'
    Pos = ET.SubElement(Obj, 'pose')
    Pos.text = 'Unspecified'
    Trun = ET.SubElement(Obj, 'truncated')
    Trun.text = '0'
    Dif = ET.SubElement(Obj, 'difficult')
    Dif.text = '0'
    # bndbox tree in object tree
    Bnd = ET.SubElement(Obj, 'bndbox')
    Xmin = ET.SubElement(Bnd, 'xmin')
    Xmin.text = '0'
    Ymin = ET.SubElement(Bnd, 'ymin')
    Ymin.text = '0'
    Xmax = ET.SubElement(Bnd, 'xmax')
    Xmax.text = '0'
    Ymax = ET.SubElement(Bnd, 'ymax')
    Ymax.text = '0'
    Ang = ET.SubElement(Bnd, 'angle')
    Ang.text = '0'

    # make xml tree format
    ET.dump(Annot)

    # save data with xxxxxx.jpg
    filenum = 100000
    ElementTree(Annot).write(filepath + "%06d.xml" %filenum, encoding='utf-8')
    tt = open(txtpath, 'w')
    tt.write("%06d" %filenum)
    tt.close()

if __name__ == '__main__':
    main(sys.argv[1])
