
import gzip
import numpy as np
import torch
import cPickle as pickle
import torch.utils.data as data
from example_project.data.make_features import create_data

class TotalData(data.Dataset):
    def __init__(self, args):
        self.baseX, self.progX, self.text, self.labels = create_data(args.max_base, args.max_prog, args.max_before, args.max_after, args.desired_features)

    def __len__(self):
        return self.baseX.size(0)

    def __getitem__(self, idx):
        return {"baseline": self.baseX[idx], "progress": self.progX[idx], "text": self.text[idx], "labels": self.labels[idx]}