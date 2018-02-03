import itertools
import os
import torch
from torch.autograd import Variable
import numpy as np
import pandas as pd
import torch.nn as nn


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.val = 0
        self.sum = 0
        self.count = 0
        self.avg_mom = 0.98
        self.avg_loss_mom = 0.

    def reset(self):
        self.__init__()

    def update(self, val):
        self.val = val
        self.count += 1
        self.sum += val * self.count
        self.avg_loss_mom = self.avg_loss_mom * self.avg_mom + val * (1 - self.avg_mom)

    @property
    def avg(self):
        return self.sum / self.count

    @property
    def debias_loss(self):
        # More info: https://youtu.be/J99NV9Cr75I?t=2h4m
        return self.avg_loss_mom / (1 - self.avg_mom ** self.count)


def to_np(v):
    """

    Args:
        v (Variable, Tensor): Pytorch Variable/Tensor

    Returns:
        np.ndarray: A numpy array
    """
    if isinstance(v, Variable):
        v = v.data
    return v.cpu().numpy()


def to_gpu(x, *args, **kwargs):
    """
    Moves torch tensor to gpu if possible

    Returns:
        torch.Tensor: Moved to the GPU or not
    """
    return x.cuda(*args, **kwargs) if torch.cuda.is_available() else x


def to_csv(test_file, output_file, identifier_field, predicted_field,
           predictions, read_format='csv'):
    df = None
    if read_format == 'csv':
        df = pd.read_csv(test_file)
    elif read_format == 'feather':
        df = pd.read_feather(test_file)
    df = df[[identifier_field]]
    df[predicted_field] = predictions
    df.to_csv(output_file, index=False)


def children(module: nn.Module):
    """
        Returns a list of an nn.Module children modules
        (in other terms the list of layers of a given model)
    Args:
        module (nn.Module):
            A Pytorch module
    Returns:
        list: A list of the module children
    """
    return module if isinstance(module, (list, tuple)) else list(module.children())


def get_labels_from_folders(path, y_mapping=None):
    """
    Get labels from folder names as well as the absolute path to the files
    from the folders
    Args:
        path (str): The path to inspect
        y_mapping (dict): If the labels were already mapped to an integer,
        give that mapping here in the form of {index: label}

    Returns:
        files (tuple): A tuple containing (file_path, label)
        y_mapping (dict): The mapping between the label and their index
    """
    y_all = [label for label in os.listdir(path) if os.path.isdir(os.path.join(path, label))]
    if not y_mapping:
        y_mapping = {v: k for k, v in enumerate(y_all)}

    files = [[(file, y_mapping[label]) for file in os.listdir(os.path.join(path, label))] for label in y_all]
    files = np.array(files).reshape(-1, 2)
    return files, y_mapping


def split_by_idx(idxs, *a):
    mask = np.zeros(len(a[0]), dtype=bool)
    mask[np.array(idxs)] = True
    return [(o[mask], o[~mask]) for o in a]
