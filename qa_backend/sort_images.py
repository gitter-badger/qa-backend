# AUTOGENERATED! DO NOT EDIT! File to edit: 3. Sort images.ipynb (unless otherwise specified).

__all__ = ['nn_sort', 'sort_images']

# Internal Cell
from fastcore.script import *
from fastai.vision.all import *
from fastai.callback.wandb import *
from self_supervised.augmentations import *
from self_supervised.layers import *
from self_supervised.vision.barlow_twins import *

# fixup depreciation
from kornia import augmentation as korniatfm
korniatfm.GaussianBlur = korniatfm.RandomGaussianBlur

# Cell
def nn_sort(features):
    x = random.choice(features)
    remaining = list(range(len(features)))
    idxs = []
    while len(remaining):
        i = torch.linalg.norm(x - features[remaining], dim=-1).argsort()[0]
        idxs.append(remaining[i])
        x = features[remaining[i]]
        remaining.pop(i)
    return idxs

# Cell
@call_parse
def sort_images(
        path:Path, # path
        features_file:str = None # features file
    ):
    "Pretrain a model on images in `path`."
    if features_file is None:
        ffiles = list(path.glob('*-features.pkl'))
        if len(ffiles) == 0:
            raise Exception(f"No models found in: {path}!")
        elif len(ffiles) > 1:
            msg = f"Found multiple models in: {path}, please pass one of:"
            for file in ffiles:
                msg += f"\n  --feature_file {file}"
            raise Exception(msg)
        features_file = ffiles[0]

    with open(features_file, 'rb') as f:
        data = pickle.load(f)

    fnames = data['fnames']
    keyfunc = lambda x: fnames[x].parent
    groups = [(name.name, list(group))
              for name, group in itertools.groupby(sorted(range(len(fnames)), key=keyfunc), keyfunc)]
    with open((path/Path(features_file).name.replace("-features", "-grouped")).with_suffix('.json'), 'w') as f:
        json.dump(dict(
            dist_threshold = 1000,
            labeled_clusters = [dict(
                name = f"{name} – sorted perceptualy",
                photos = [dict(
                    dist_to_mean=0, marked=False, murl=str(fnames[group[i]])
                ) for i in nn_sort(data['features'][group])]
            ) for name, group in groups]
        ), f)